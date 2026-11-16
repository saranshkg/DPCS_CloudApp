# 04. End-to-end local verification

This guide verifies the application from browser to Flask to MySQL. It also explains how to test the S3 image-upload path from a local computer.

Complete `README_01_PREREQUISITES.md`, `README_02_LOCAL_MYSQL.md` and `README_03_LOCAL_APPLICATION.md` first.

## 1. Start the services

Start MySQL if it is not already running.

macOS with Homebrew:

```bash
brew services start mysql@8.4
```

Windows PowerShell (run elevated if required):

```powershell
Start-Service MySQL84
```

Linux:

```bash
sudo systemctl start mysql
```

Activate the Python virtual environment and start Flask:

macOS/Linux:

```bash
source .venv/bin/activate
flask --app app run --debug
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
flask --app app run --debug
```

Keep this terminal open while testing.

## 2. Verify the HTTP application and database

Open:

- Home page: <http://127.0.0.1:5000/>
- Health check: <http://127.0.0.1:5000/health>
- New idea form: <http://127.0.0.1:5000/ideas/new>

The health endpoint should return:

```json
{
  "database": "connected",
  "status": "healthy"
}
```

If the home page returns a database error, verify the MySQL service and `.env` connection URL before continuing.

## 3. Create a test idea without an image

On `/ideas/new`, submit:

| Field | Test value |
|---|---|
| Your name | Test User One |
| Title | Improve campus study spaces |
| Description | Add more quiet study spaces with accessible power outlets. |
| Category | Campus Life |
| Image | Leave empty |

Expected:

- The application reports that the idea was published.
- The browser redirects to `/ideas/<id>`.
- The idea detail page shows the title, description, category and author.
- The home page lists the idea.

## 4. Add a comment

On the idea detail page, submit:

| Field | Test value |
|---|---|
| Your name | Test User Two |
| Comment | A quiet study area near the library would be useful. |

Expected:

- The application reports that the comment was added.
- The comment appears on the idea detail page.
- The comment count on the home page increases.

Open a second browser, private window or another device on the same network and load the same idea URL. The same idea and comment should be visible because they are stored in the shared database, not in browser-local storage.

For another device on the same LAN, the development server must bind to all interfaces:

```bash
flask --app app run --host 0.0.0.0 --port 5000
```

Find the computer's LAN IP and open `http://LAN_IP:5000` from the second device. Both devices must be on a network that permits peer-to-peer connections. Do not use this command on an untrusted network; the Flask debug server is not a production server.

## 5. Verify rows in MySQL

In a second terminal:

```bash
mysql --protocol=TCP -h 127.0.0.1 -P 3306 -u campusboard_app -p campusboard
```

Run:

```sql
SELECT
    i.id,
    i.title,
    i.author_name,
    c.name AS category,
    i.image_key,
    i.created_at
FROM ideas AS i
JOIN categories AS c ON c.id = i.category_id
ORDER BY i.id DESC;

SELECT
    cm.id,
    cm.idea_id,
    cm.author_name,
    cm.body,
    cm.created_at
FROM comments AS cm
ORDER BY cm.id DESC;
```

Expected:

- The test idea appears in `ideas`.
- Its category name comes from the `categories` table through a join.
- The comment appears in `comments` and references the idea's ID.
- `image_key` is `NULL` for an idea created without an image.

Exit MySQL:

```sql
EXIT;
```


## 06. Configure S3 and test the local application

The application stores uploaded images in Amazon S3, not in MySQL or on the Flask server. MySQL stores only the S3 object key in `ideas.image_key`.

If no bucket is configured, text-only ideas and comments still work. Image uploads require an S3 bucket and working AWS credentials. Complete this section if you want to test image uploads locally.

### 6.1 Create an S3 bucket

Use the AWS Console:

1. Open https://s3.console.aws.amazon.com/.
2. Select the AWS Region you intend to use in `.env`, for example `ap-south-1`.
3. Create a globally unique bucket name, for example `dpcs-campusboard-<unique-suffix>`.
4. Keep **Block all public access** enabled.
5. Keep bucket versioning disabled for this exercise.
6. Keep the default encryption settings.
7. Create the bucket.

Bucket names are globally unique across AWS. If your chosen name is unavailable, add a random suffix. Do not make the bucket public. The application uses presigned URLs to display images from a private bucket.

### 6.2 Configure local AWS credentials

AWS CLI v2 is needed for the command-line checks in this section. Install it using the official instructions if you have not already:

https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

For this tutorial, use the AWS Console sign-in flow. You do not need to create access keys or run `aws configure`.

You can authenticate using either your AWS root account or an IAM identity.

**Option A: Sign in directly using the root account (default profile)**

Run:

```bash
aws login
```

A browser window will open. Sign in using your AWS account's root email address and password. Complete any requested authentication steps. If prompted for a region, enter `ap-south-1`.

This authenticates the AWS CLI using the `default` profile. You do not need to set `AWS_PROFILE`.

**Option B: Sign in using a named profile**

If you prefer to use a separate IAM identity, run:

```bash
aws login --profile campusboard-dev
```

A browser window will open. Sign in using the IAM identity you intend to use. If prompted for a region, enter `ap-south-1`.

This creates or updates the `campusboard-dev` profile using temporary credentials from your console session.

**Verify the authenticated identity**

For Option A:

```bash
aws sts get-caller-identity
```

For Option B:

```bash
aws sts get-caller-identity --profile campusboard-dev
```

The output shows the AWS account ID and identity ARN. Check that you authenticated to the intended AWS account.

**Select the profile for your terminal session**

If you chose Option A, no additional configuration is required. The AWS CLI and Boto3 use the default profile automatically.

If you chose Option B, set the profile for the current terminal session.

macOS / Linux:

```bash
export AWS_PROFILE=campusboard-dev
export AWS_DEFAULT_REGION=ap-south-1
```

Windows PowerShell:

```powershell
$env:AWS_PROFILE = "campusboard-dev"
$env:AWS_DEFAULT_REGION = "ap-south-1"
```

For Option A, you can set the region without selecting a profile.

macOS / Linux:

```bash
export AWS_DEFAULT_REGION=ap-south-1
```

Windows PowerShell:

```powershell
$env:AWS_DEFAULT_REGION = "ap-south-1"
```

Check which credentials and profile the CLI is using:

```bash
aws configure list
```

**Important:** Running `aws login` authenticates the default profile. Running `aws login --profile campusboard-dev` authenticates the named profile. These are separate profiles and do not automatically share credentials.

The console login session uses temporary credentials and expires after a limited period. Re-run the corresponding `aws login` command when it expires.

Do not create root access keys. Root has broad access to the AWS account. Using root for this local exercise is acceptable for the demonstration, but do not use root credentials for routine development or production workloads.

### 6.3 Check S3 access

List the buckets:

```bash
aws s3 ls
```

Then check the bucket you created:

```bash
aws s3 ls s3://YOUR_BUCKET_NAME/
```

Replace `YOUR_BUCKET_NAME` with the exact bucket name.

If you authenticated using the root account, you do not need to attach an additional S3 IAM policy for this test.

If you authenticated using an IAM identity, that identity needs the appropriate S3 permissions. For this application, grant:

- `s3:PutObject` and `s3:GetObject` for `arn:aws:s3:::YOUR_BUCKET_NAME/images/*`.
- `s3:ListBucket` on `arn:aws:s3:::YOUR_BUCKET_NAME` only if you need to list bucket contents using the CLI.

Do not create root access keys.

### 6.4 Set the bucket in `.env`

Edit `.env`:

```dotenv
AWS_REGION=ap-south-1
S3_BUCKET=YOUR_BUCKET_NAME
```

The region must match the bucket's actual region. Restart Flask after changing `.env`, because application configuration is loaded when the process starts.

Boto3 uses the same AWS credential provider chain as the AWS CLI. It can use either:

- The default profile authenticated with `aws login`.
- The named profile authenticated with `aws login --profile campusboard-dev`.

If you chose Option A, do not set `AWS_PROFILE`.

If you chose Option B, keep `AWS_PROFILE=campusboard-dev` set in the same terminal from which you start Flask.

Boto3 must support AWS console login credentials. In `requirements.txt`, use:

```text
boto3[crt]>=1.41,<2
```

Install or update the dependency in the active virtual environment:

```bash
python -m pip install -r requirements.txt
```

### 6.5 Test an image upload

1. Start Flask if it is not already running.
2. Open http://127.0.0.1:5000/ideas/new.
3. Create a new idea.
4. Attach a valid JPEG, PNG or WEBP image smaller than 5 MB.
5. Publish the idea.
6. Confirm that the detail page displays the image.

The application checks the actual image format using Pillow. Renaming a PDF or text file to `.jpg` does not make it a valid image.

Verify that the object was uploaded:

```bash
aws s3 ls s3://YOUR_BUCKET_NAME/images/
```

Verify that MySQL stores the object key:

```sql
SELECT id, title, image_key
FROM ideas
ORDER BY id DESC
LIMIT 5;
```

The S3 bucket remains private. The browser receives a time-limited presigned URL generated by Flask. The current application sets the URL expiry to one hour.

## 6.6 S3 failure cases

- **`NoCredentialsError` or credential-provider error:** Check that you authenticated using `aws login`. If using a named profile, check that `AWS_PROFILE=campusboard-dev` is set in the terminal running Flask.
- **`ExpiredToken` or expired login session:** Run `aws login` again, or `aws login --profile campusboard-dev` if using the named profile. Restart Flask.
- **`AccessDenied`:** Confirm that you authenticated to the intended AWS account. If using an IAM identity, check its S3 permissions. If using root, check whether an organisation-level restriction or bucket policy is denying access.
- **`NoSuchBucket`:** Check the bucket name and AWS account.
- **Redirect or signature errors:** Verify that `AWS_REGION` matches the bucket's actual region.
- **Upload works but image display fails:** Check `s3:GetObject` access and confirm that the object still exists.
- **Image uploads but the database insert fails:** The teaching application does not delete an uploaded S3 object after a database commit failure. This can leave an orphaned object.

## 7. Verify validation and edge cases

Test the following:

| Test | Expected behaviour |
|---|---|
| Empty author name | Rejected |
| One-character author name | Rejected |
| Title shorter than 5 characters | Rejected |
| Description shorter than 10 characters | Rejected |
| No category selected | Rejected |
| Invalid category ID submitted manually | Rejected |
| Empty comment | Rejected |
| Comment longer than 1,000 characters | Rejected |
| Idea ID that does not exist | 404 response |
| No image attached | Idea is saved with `image_key = NULL` |
| Image over 5 MB | Flask rejects request with HTTP 413 |
| Unsupported or renamed non-image file | Upload is rejected |
| Image upload without S3 configuration | Upload fails; text-only use remains possible |

The 5 MB request limit applies to the whole multipart request, not just the image. The application also relies on server-side validation; the HTML `accept` attribute is only a browser hint.

## 8. Reset local test data

To remove test ideas and comments while keeping the categories:

```sql
DELETE FROM comments;
DELETE FROM ideas;
```

To remove all application tables and recreate them, connect as a MySQL administrative user and run:

```sql
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS ideas;
DROP TABLE IF EXISTS categories;
```

Then run:

```bash
flask --app app init-db
```

Dropping tables permanently deletes the records. It does not delete uploaded S3 objects. Remove test objects separately if required:

```bash
aws s3 rm s3://YOUR_BUCKET_NAME/images/ --recursive
```

Check the bucket and AWS account before running the deletion command.

## 9. Troubleshooting summary

| Symptom | First check |
|---|---|
| Browser cannot open localhost | Is Flask running? Is the port 5000? |
| `/health` fails | Is MySQL running? Is `DATABASE_URL` correct? |
| `Access denied` from MySQL | Can the application MySQL user connect from the terminal? |
| `No module named ...` | Is `.venv` active? Were requirements installed into it? |
| CSRF error | Submit the rendered form and allow cookies |
| Image upload fails | Is `S3_BUCKET` set? Are AWS credentials configured? |
| AWS CLI works but Flask cannot access S3 | Is Boto3 at least 1.41 with CRT installed? Is Flask using the same profile? Restart Flask after changing the environment |
| Image URL returns AccessDenied | Does the authenticated identity have `s3:GetObject`? Is the bucket policy blocking access? |
| Another device cannot connect | Is Flask bound to `0.0.0.0`? Does the local firewall allow port 5000? |

## 10. Local completion checklist

- [ ] MySQL is running.
- [ ] Flask starts without import errors.
- [ ] `/health` returns `healthy`.
- [ ] An idea can be created.
- [ ] A comment can be added using a second contributor name.
- [ ] The idea and comment are visible from another browser or device.
- [ ] SQL queries show the corresponding database rows.
- [ ] If S3 is configured, an image uploads and displays.
- [ ] The S3 bucket is private.
- [ ] No credentials or `.env` file have been committed.

The local application is ready. Continue to the AWS deployment README. The deployment will use EC2 for Flask, RDS for MySQL and S3 for images. On EC2, use an instance role for S3 access rather than local console credentials or long-lived access keys.

## Official AWS references

- [AWS CLI login with console credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html)
- [Boto3 credentials, including console login credentials](https://docs.aws.amazon.com/boto3/latest/guide/credentials.html)
- [Install AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
