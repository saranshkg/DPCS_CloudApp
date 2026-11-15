# 10. Verification: Test the Deployed Application

This section verifies the application from the browser and checks that data is stored in the intended AWS services.

Use the public EC2 address:

    http://EC2_PUBLIC_IP

The application should be reachable from a device outside the EC2 instance.

## 10.1 Browser test plan

Run these tests in order.

| Test | Action | Expected result |
|---|---|---|
| Home page | Open the EC2 public address | Ideas Board loads |
| Create idea | Submit title, description, author and category | Idea is created |
| Browse ideas | Return to the home page | New idea appears |
| Idea details | Open the new idea | Full idea details appear |
| Add comment | Submit a comment | Comment appears on the idea page |
| Upload image | Create an idea with an image | Idea is created and image uploads |
| Display image | Open the idea detail page | Image loads |
| Refresh | Refresh the page | Idea, comment and image remain |
| Second device | Open the site from another device/network | Same ideas and comments appear |

Use different author names when testing from different devices. The application does not authenticate contributors, so an entered name is only a label and does not prove identity.

## 10.2 Verify the database

Connect to RDS from EC2:

    mysql -h RDS_ENDPOINT -P 3306 -u campusboard_app -p campusboard

Check the tables:

    SHOW TABLES;

Inspect the most recent ideas:

    SELECT id, author_name, title, category_id, image_key, created_at
    FROM ideas
    ORDER BY id DESC
    LIMIT 10;

Inspect comments:

    SELECT id, idea_id, author_name, body, created_at
    FROM comments
    ORDER BY id DESC
    LIMIT 10;

If the schema uses different names, inspect it first:

    DESCRIBE ideas;
    DESCRIBE comments;

Confirm:
- New ideas appear in RDS.
- Comments reference the expected idea IDs.
- Image-backed ideas contain an S3 object key.
- Ideas without images have an empty or NULL image key, according to the application schema.

## 10.3 Verify S3 objects

In the AWS Console:
1. Open S3.
2. Open `dpcs-campusboard-1`.
3. Open the `images/` prefix.
4. Confirm the object uploaded during the browser test exists.

Alternatively, from EC2:

    aws s3 ls s3://dpcs-campusboard-1/images/

The object should remain in S3 even after a presigned URL expires. A presigned URL controls temporary access, not object retention.

## 10.4 Verify the application services

On EC2:

    sudo systemctl status campusboard
    sudo systemctl status nginx

Check the application logs:

    sudo journalctl -u campusboard -n 100 --no-pager

Check Nginx errors:

    sudo tail -n 100 /var/log/nginx/error.log

Check that Gunicorn is listening only on localhost:

    sudo ss -ltnp

Expected arrangement:
- Nginx listens on port 80.
- Gunicorn listens on `127.0.0.1:8000`.
- MySQL RDS listens on port 3306 inside the VPC.

## 10.5 Test from a second device

Use a phone or another computer on a different network if possible.

1. Open `http://EC2_PUBLIC_IP`.
2. Confirm the same ideas appear.
3. Open an idea with an image.
4. Add a comment using a different author name.
5. Refresh the first device and confirm the comment appears.

This confirms that the application is not relying on data stored only in the original browser or on the developer's laptop.

## 10.6 Troubleshooting by symptom

| Symptom | First place to check |
|---|---|
| Site does not load | EC2 public IP, public route table, EC2 security group, Nginx status |
| Nginx shows 502 Bad Gateway | Gunicorn/systemd status and application logs |
| Home page loads but database actions fail | EC2 `.env`, RDS endpoint, RDS security group, database credentials |
| Image upload fails | EC2 IAM role, S3 policy, bucket name, application logs |
| Image uploads but does not display | Presigned URL generation, bucket region, `s3:GetObject` permission, browser URL |
| Changes disappear after restart | Confirm the app uses RDS and S3, not local storage |
| Works on EC2 but not from another device | Public IP, Nginx, EC2 inbound TCP 80 rule |

When reporting an error, capture the relevant application log entry and the time of the test. Do not share passwords, `.env` contents or complete presigned URLs.

## 10.7 Completion criteria

The deployment is verified when:
- The site loads from an external device.
- Ideas and comments are written to RDS.
- Images are uploaded to S3 and retrieved by the application.
- Data remains available after browser refresh and application restart.
- The database is not publicly accessible.
- The application does not depend on local files or credentials from the developer's laptop.
