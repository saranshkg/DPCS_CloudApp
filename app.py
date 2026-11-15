
import os
import uuid
from datetime import datetime, timezone

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, abort
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from PIL import Image, UnidentifiedImageError
from sqlalchemy import text
from werkzeug.utils import secure_filename

from dotenv import load_dotenv
load_dotenv()

# --------------------------------------------------
# Configuration
# --------------------------------------------------

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "local-development-only"
)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://campusboard_app:CHANGE_ME@127.0.0.1:3306/campusboard"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True
}

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
S3_BUCKET = os.getenv("S3_BUCKET")

# s3 = boto3.client("s3", region_name=AWS_REGION)

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    endpoint_url=f"https://s3.{AWS_REGION}.amazonaws.com",
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "virtual"}
    )
)

ALLOWED_FORMATS = {
    "JPEG": ("jpg", "image/jpeg"),
    "PNG": ("png", "image/png"),
    "WEBP": ("webp", "image/webp"),
}


# --------------------------------------------------
# Database models
# --------------------------------------------------

class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    ideas = db.relationship("Idea", back_populates="category")


class Idea(db.Model):
    __tablename__ = "ideas"

    id = db.Column(db.Integer, primary_key=True)

    author_name = db.Column(db.String(60), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    image_key = db.Column(db.String(500), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    category = db.relationship(
        "Category",
        back_populates="ideas"
    )

    comments = db.relationship(
        "Comment",
        back_populates="idea",
        cascade="all, delete-orphan",
        order_by="Comment.created_at"
    )


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)

    idea_id = db.Column(
        db.Integer,
        db.ForeignKey("ideas.id", ondelete="CASCADE"),
        nullable=False
    )

    author_name = db.Column(db.String(60), nullable=False)
    body = db.Column(db.String(1000), nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    idea = db.relationship(
        "Idea",
        back_populates="comments"
    )


# --------------------------------------------------
# S3 image upload
# --------------------------------------------------

def upload_image(file):

    if not file or not file.filename:
        return None

    if not S3_BUCKET:
        raise RuntimeError("S3_BUCKET is not configured")

    # Check that the uploaded file is a valid image.
    try:
        image = Image.open(file.stream)
        image.verify()

        image_format = image.format

        if image_format not in ALLOWED_FORMATS:
            raise ValueError("Only JPEG, PNG and WEBP images are allowed")

        extension, content_type = ALLOWED_FORMATS[image_format]

    except (UnidentifiedImageError, OSError):
        raise ValueError("The uploaded file is not a valid image")

    finally:
        file.stream.seek(0)

    # Generate a unique S3 object key.
    key = f"images/{uuid.uuid4().hex}.{extension}"

    # Upload to S3. Objects remain private.
    s3.upload_fileobj(
        file.stream,
        S3_BUCKET,
        key,
        ExtraArgs={
            "ContentType": content_type,
            "ServerSideEncryption": "AES256"
        }
    )

    return key


def get_image_url(key):

    if not key:
        return None

    return s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": key
        },
        ExpiresIn=3600
    )


# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.route("/")
def index():

    ideas = (
        Idea.query
        .order_by(Idea.created_at.desc())
        .limit(50)
        .all()
    )

    return render_template(
        "index.html",
        ideas=ideas
    )


@app.route("/ideas/new", methods=["GET", "POST"])
def new_idea():

    categories = Category.query.order_by(Category.name).all()

    if request.method == "POST":

        author_name = request.form.get("author_name", "").strip()
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        try:
            category_id = int(request.form.get("category_id", ""))
        except (ValueError, TypeError):
            category_id = None

        category = db.session.get(Category, category_id)

        if not 2 <= len(author_name) <= 60:
            flash("Name must be between 2 and 60 characters.", "error")
            return render_template(
                "new_idea.html", categories=categories
            )

        if not 5 <= len(title) <= 120:
            flash("Title must be between 5 and 120 characters.", "error")
            return render_template(
                "new_idea.html", categories=categories
            )

        if not 10 <= len(description) <= 3000:
            flash("Description must be between 10 and 3000 characters.", "error")
            return render_template(
                "new_idea.html", categories=categories
            )

        if not category:
            flash("Please select a valid category.", "error")
            return render_template(
                "new_idea.html", categories=categories
            )

        image_key = None
        image_file = request.files.get("image")

        try:
            if image_file and image_file.filename:
                image_key = upload_image(image_file)

            idea = Idea(
                author_name=author_name,
                title=title,
                description=description,
                category_id=category.id,
                image_key=image_key
            )

            db.session.add(idea)
            db.session.commit()

        except (ValueError, RuntimeError, BotoCoreError, ClientError) as error:
            db.session.rollback()
            app.logger.exception("Idea creation failed")
            flash(f"Could not publish idea: {error}", "error")

            return render_template(
                "new_idea.html", categories=categories
            )

        flash("Your idea has been published!", "success")

        return redirect(url_for("idea_detail", idea_id=idea.id))

    return render_template(
        "new_idea.html",
        categories=categories
    )


@app.route("/ideas/<int:idea_id>")
def idea_detail(idea_id):

    idea = db.get_or_404(Idea, idea_id)

    image_url = get_image_url(idea.image_key)

    return render_template(
        "idea_detail.html",
        idea=idea,
        image_url=image_url
    )


@app.route("/ideas/<int:idea_id>/comment", methods=["POST"])
def add_comment(idea_id):

    idea = db.get_or_404(Idea, idea_id)

    author_name = request.form.get("author_name", "").strip()
    body = request.form.get("body", "").strip()

    if not 2 <= len(author_name) <= 60:
        flash("Name must be between 2 and 60 characters.", "error")
        return redirect(url_for("idea_detail", idea_id=idea.id))

    if not 2 <= len(body) <= 1000:
        flash("Comment must be between 2 and 1000 characters.", "error")
        return redirect(url_for("idea_detail", idea_id=idea.id))

    comment = Comment(
        idea_id=idea.id,
        author_name=author_name,
        body=body
    )

    db.session.add(comment)
    db.session.commit()

    flash("Comment added!", "success")

    return redirect(url_for("idea_detail", idea_id=idea.id))


@app.route("/health")
def health():

    # Checks application and database connectivity.
    db.session.execute(text("SELECT 1"))

    return {"status": "healthy", "database": "connected"}


# --------------------------------------------------
# Database initialization
# --------------------------------------------------

@app.cli.command("init-db")
def init_db():

    db.create_all()

    default_categories = [
        "Technology",
        "Campus Life",
        "Research",
        "Events",
        "Other"
    ]

    for name in default_categories:

        existing = Category.query.filter_by(name=name).first()

        if not existing:
            db.session.add(Category(name=name))

    db.session.commit()

    print("Database initialized successfully.")


if __name__ == "__main__":
    app.run(debug=True)
