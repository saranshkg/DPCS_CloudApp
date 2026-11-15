# 03. Configure and run the Flask application locally

This guide installs the Python dependencies, configures the application to use local MySQL, creates the database tables and starts the Flask development server.

Complete `README_01_PREREQUISITES.md` and `README_02_LOCAL_MYSQL.md` first.

Run all commands from the repository root, the directory containing `app.py`.

## 1. Confirm the repository is configured for MySQL

The repository originally used PostgreSQL. Confirm that the MySQL changes from `README_01_PREREQUISITES.md` have been applied.

### `requirements.txt`

It must contain these dependencies:

```text
Flask>=3.0,<4
Flask-SQLAlchemy>=3.1,<4
Flask-WTF>=1.2,<2
PyMySQL>=1.1,<2
python-dotenv>=1.0,<2
boto3>=1.35,<2
Pillow>=10,<13
gunicorn>=22,<24
```

There should be no `psycopg` dependency for this MySQL version.

### `app.py`

The file already calls `load_dotenv()` and reads `DATABASE_URL` from the environment. Confirm that its fallback URL uses the MySQL dialect:

```python
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://campusboard_app:CHANGE_ME@127.0.0.1:3306/campusboard"
)
```

### `.env`

Confirm it contains a valid local MySQL connection URL:

```dotenv
SECRET_KEY=your-generated-secret
DATABASE_URL=mysql+pymysql://campusboard_app:YOUR_PASSWORD@127.0.0.1:3306/campusboard
AWS_REGION=ap-south-1
S3_BUCKET=
```

The `.env` file must be in the same directory as `app.py`. The repository's `.gitignore` excludes it.

## 2. Activate the virtual environment

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

The prompt should show `(.venv)`.

If activation is blocked in PowerShell, see the execution-policy instructions in `README_01_PREREQUISITES.md`. You can also run the virtual environment's Python directly without activating it:

PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

macOS/Linux:

```bash
.venv/bin/python -m pip install -r requirements.txt
```

## 3. Install Python dependencies

With the virtual environment activated:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Verify that the MySQL driver and Flask packages are installed:

```bash
python -c "import flask, flask_sqlalchemy, pymysql, dotenv, boto3; print('Dependencies OK')"
```

Expected:

```text
Dependencies OK
```

If `ModuleNotFoundError: No module named 'dotenv'` appears, verify that `python-dotenv` is in `requirements.txt`, then rerun the install command.

If `ModuleNotFoundError: No module named 'pymysql'` appears, verify that `PyMySQL` is in `requirements.txt`, then rerun the install command.

## 4. Initialize the database tables

Make sure MySQL is running and the application user can connect. Then run:

```bash
flask --app app init-db
```

Expected output:

```text
Database initialized successfully.
```

The command creates these tables:

- `categories`
- `ideas`
- `comments`

It also inserts five categories if they do not already exist:

- Technology
- Campus Life
- Research
- Events
- Other

The command is safe to rerun for the default categories. `db.create_all()` creates missing tables but does not alter existing tables when the model changes. For schema changes in a later version, use a migration tool rather than relying on `init-db`.

If the `flask` executable is not found, use:

```bash
python -m flask --app app init-db
```

## 5. Verify the tables in MySQL

Connect as the application user:

```bash
mysql --protocol=TCP -h 127.0.0.1 -P 3306 -u campusboard_app -p campusboard
```

Run:

```sql
SHOW TABLES;

SELECT id, name
FROM categories
ORDER BY id;

SELECT COUNT(*) AS idea_count FROM ideas;
SELECT COUNT(*) AS comment_count FROM comments;
```

Expected:

- Three tables are listed.
- Five categories are listed.
- Idea and comment counts are initially zero.

Exit:

```sql
EXIT;
```

## 6. Start the Flask development server

Run:

```bash
flask --app app run --debug
```

If needed:

```bash
python -m flask --app app run --debug
```

Expected output includes a local address, usually:

```text
 * Running on http://127.0.0.1:5000
```

Open <http://127.0.0.1:5000> in a browser.

The debug server is for local development only. Do not expose it directly to the public internet or use it as the production server on EC2.

Stop the server with `Ctrl+C`.

## 7. Test the health endpoint

With the Flask server running, open:

<http://127.0.0.1:5000/health>

Expected JSON:

```json
{
  "database": "connected",
  "status": "healthy"
}
```

This endpoint executes `SELECT 1` against MySQL. It verifies application-to-database connectivity, not S3 connectivity.

## 8. Test creating and commenting on ideas

1. Open <http://127.0.0.1:5000/>.
2. Select **Share an idea**.
3. Enter a name, title and description.
4. Select a category.
5. Leave the image field empty for this test.
6. Publish the idea.
7. Confirm that the detail page opens.
8. Add a comment using a second name.
9. Return to the home page and confirm that the idea appears.

The application does not have login or registration. The name field is user-supplied text, not an authenticated identity.

## 9. Run the server on a different local port

If port 5000 is already in use:

```bash
flask --app app run --debug --port 5001
```

Open <http://127.0.0.1:5001>.

Do not change the MySQL port to resolve a Flask port conflict. Flask and MySQL use different ports.

## 10. Configuration and security notes

- Keep `SECRET_KEY` unique and private. The fallback value in `app.py` is only a development fallback.
- Do not use the MySQL root account in `DATABASE_URL`.
- Do not commit `.env`.
- Do not use Flask's debug server for a public deployment.
- The application creates database tables with `db.create_all()`. This is adequate for the teaching application, not a replacement for schema migrations.
- The application creates an S3 client when `app.py` is imported. AWS credentials are not required for database-only testing, but they are required for image uploads.
- Do not use real personal or sensitive information in this teaching application.

## 11. Common application errors

### `ModuleNotFoundError`

Activate `.venv` and reinstall:

```bash
python -m pip install -r requirements.txt
```

Confirm that the terminal's `python` points to the virtual environment:

macOS/Linux:

```bash
which python
```

Windows PowerShell:

```powershell
Get-Command python
```

### `Access denied for user`

Test the MySQL login independently using the command in Section 5. Correct the password, host or grants in MySQL before debugging Flask.

### `Unknown database 'campusboard'`

Run the SQL database creation steps in `README_02_LOCAL_MYSQL.md`.

### `No module named 'MySQLdb'`

The URL is probably using the default MySQL driver rather than PyMySQL. It must begin:

```text
mysql+pymysql://
```

Also verify that `PyMySQL` is installed.

### CSRF token missing or invalid

The HTML forms include a CSRF token and the application enables Flask-WTF's `CSRFProtect`. Submit forms through the rendered pages rather than sending a raw POST request without a token. Check that browser cookies are enabled.

### `Address already in use`

Use another Flask port, for example `--port 5001`, or stop the process using port 5000.

## 12. Completion checklist

- [ ] Python dependencies install successfully.
- [ ] Flask connects to local MySQL.
- [ ] `flask --app app init-db` completes.
- [ ] The three tables exist.
- [ ] The five categories exist.
- [ ] `/health` returns `healthy`.
- [ ] An idea can be created without an image.
- [ ] A comment can be added.
- [ ] The idea and comment appear in MySQL.

Continue to `README_04_LOCAL_END_TO_END_TEST.md`.
