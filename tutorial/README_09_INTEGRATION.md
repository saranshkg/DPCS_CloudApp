# 9. Integration: Connect EC2, RDS and S3

This section connects the deployed Flask application to the RDS database and S3 bucket. It assumes Sections 5–8 are complete.

## 9.1 Confirm the three resources

| Component | Resource | Required configuration |
|---|---|---|
| Application | EC2 `campusboard-app` | Public subnet, `campusboard-ec2-sg` |
| Database | RDS `campusboard-db` | Private DB subnet group, `campusboard-rds-sg` |
| Image storage | S3 `dpcs-campusboard-1` | Private bucket, EC2 IAM role access |

The EC2 instance must be able to reach RDS over the VPC network and S3 through the AWS API.

## 9.2 Check the security-group relationship

Open the security groups in the VPC Console.

`campusboard-ec2-sg`:
- Inbound TCP 22 from your current IP.
- Inbound TCP 80 from the internet.
- Outbound traffic permitted for the workshop.

`campusboard-rds-sg`:
- Inbound TCP 3306 with source `campusboard-ec2-sg`.
- No inbound MySQL rule from `0.0.0.0/0`.

The RDS security group must reference the EC2 security group, not the EC2 public IP address.

## 9.3 Configure the production environment file

On EC2:

    cd /home/ubuntu/DPCS_CloudApp
    nano .env

Use the production values:

    SECRET_KEY=REPLACE_WITH_A_LONG_RANDOM_SECRET
    DATABASE_URL=mysql+pymysql://campusboard_app:URL_ENCODED_PASSWORD@RDS_ENDPOINT:3306/campusboard
    AWS_REGION=ap-south-1
    S3_BUCKET=dpcs-campusboard-1

Check each value:
- `SECRET_KEY` is a production secret, not the local development value.
- `DATABASE_URL` points to the RDS endpoint, not `127.0.0.1` or `localhost`.
- The database username is the application user, not the RDS master user.
- `AWS_REGION` matches the S3 bucket's region.
- `S3_BUCKET` is the intended bucket name.
- No long-term AWS access keys are present.

Restrict file permissions:

    chmod 600 .env

The systemd service created in Section 6 loads this file through `EnvironmentFile`.

## 9.4 Confirm RDS connectivity

From EC2:

    mysql -h RDS_ENDPOINT -P 3306 -u campusboard_app -p campusboard

Run:

    SELECT 1;
    SHOW TABLES;

Exit the MySQL client. If the connection fails, resolve the RDS endpoint, security-group, subnet or credential issue before testing the Flask application.

## 9.5 Confirm S3 permissions

From EC2, if AWS CLI is installed:

    aws sts get-caller-identity
    aws s3 ls s3://dpcs-campusboard-1/images/

The identity should be the EC2 instance role. A successful bucket listing confirms that the role can access the prefix. The Flask application uses Boto3 and the same instance-role credential provider.

## 9.6 Initialize the production database

Run the project's database initialization command from the application directory:

    cd /home/ubuntu/DPCS_CloudApp
    source .venv/bin/activate
    flask --app app init-db

Use this command only if it is defined by the project, as in the local setup. It should connect to the RDS database because the EC2 `.env` points to RDS.

If the command fails, inspect the traceback and confirm that the production `DATABASE_URL` is loaded. Do not initialize or modify the local MySQL database by mistake.

## 9.7 Restart the application

    sudo systemctl restart campusboard
    sudo systemctl status campusboard

Inspect logs:

    sudo journalctl -u campusboard -n 100 --no-pager

If the service does not start, common causes include:
- Invalid or missing environment variables.
- A malformed SQLAlchemy database URL.
- A password containing unescaped URL characters.
- A database connection failure.
- A missing Python dependency.
- A mismatch between the Gunicorn import target and the Flask application object.

## 9.8 End-to-end integration test

Open:

    http://EC2_PUBLIC_IP

Test the full application:

1. Load the home page.
2. Create an idea without an image.
3. Open the idea detail page.
4. Add a comment.
5. Return to the home page and confirm the idea appears.
6. Create another idea with an image.
7. Open its detail page and confirm the image loads.
8. Refresh the page and confirm the idea, comment and image still exist.

The data should persist because:
- Ideas and comments are stored in RDS.
- Image objects are stored in S3.
- The database stores the S3 object key, not the image bytes.

## 9.9 Confirm persistence directly

Connect to RDS from EC2:

    mysql -h RDS_ENDPOINT -P 3306 -u campusboard_app -p campusboard

Inspect the tables:

    SHOW TABLES;

Then inspect records using the actual table and column names in the project. For the expected schema, useful checks are:

    SELECT id, author_name, title, image_key, created_at FROM ideas ORDER BY id DESC LIMIT 10;
    SELECT id, idea_id, author_name, body, created_at FROM comments ORDER BY id DESC LIMIT 10;

If the application's table or column names differ, use `DESCRIBE ideas;` and `DESCRIBE comments;` and adapt the queries.

In the S3 Console, open `dpcs-campusboard-1/images/` and confirm that the uploaded image object exists.

## 9.10 Integration checkpoint

- [ ] Flask is running on EC2 through Gunicorn and Nginx.
- [ ] Flask connects to RDS using the application database user.
- [ ] Ideas and comments persist in RDS.
- [ ] Flask uploads images to the private S3 bucket.
- [ ] Images load through presigned URLs.
- [ ] The EC2 instance uses its IAM role for S3 access.
- [ ] No database or AWS secret is committed to Git.
