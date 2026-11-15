# 02. Install and configure local MySQL

This guide installs MySQL Server 8.4 LTS, starts the database service, creates the application's database and creates a restricted application user.

Database name: `campusboard`  
Application user: `campusboard_app`  
Application host: `127.0.0.1`  
Application port: `3306`

Use MySQL 8.4 LTS locally and on Amazon RDS where practical. Choose **one** installation method for your computer. Do not install multiple MySQL distributions unless you know how to manage their services and data directories.

Official reference: [MySQL 8.4 Installation](https://dev.mysql.com/doc/refman/8.4/en/installing.html).

## 1. Install MySQL 8.4 LTS

### macOS

Choose either Homebrew or the official Oracle installer. Do not use both for this tutorial. Both may attempt to run a server on port `3306`.

#### Option A: Homebrew

Install Homebrew if needed: <https://brew.sh/>.

```bash
brew update
brew install mysql@8.4
brew services start mysql@8.4
```

Homebrew's `mysql@8.4` formula may not be linked into the default command path. Add its binaries to your PATH.

For the default zsh shell:

```bash
echo 'export PATH="$(brew --prefix mysql@8.4)/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

For bash:

```bash
echo 'export PATH="$(brew --prefix mysql@8.4)/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Verify:

```bash
mysql --version
brew services list
```

A fresh Homebrew installation commonly allows this initial administrative connection without a password:

```bash
mysql -u root
```

If you previously set a root password, use:

```bash
mysql -u root -p
```

#### Option B: Official MySQL installer

1. Open <https://dev.mysql.com/downloads/mysql/>.
2. Select macOS and download the MySQL 8.4 LTS DMG package matching your Mac's processor.
3. Run the installer and follow its prompts.
4. If prompted to choose an authentication method, use the default recommended by the installer unless your course instructions specify otherwise.
5. Set and record the root password.
6. Start MySQL using the MySQL preference pane or the installed launch daemon.

Open a new Terminal window. Check whether the client is on your PATH:

```bash
mysql --version
```

If the command is not found, use the full path to the MySQL client. The usual Oracle package location is:

```bash
/usr/local/mysql/bin/mysql --version
```

Connect with:

```bash
/usr/local/mysql/bin/mysql -u root -p
```

The installation path can differ by package version and machine. If that path does not exist, locate the `mysql` executable from the installation directory or use the MySQL preference pane.

### Windows 10/11

1. Open <https://dev.mysql.com/downloads/installer/>.
2. Download the MySQL Installer for Windows. If the installer page does not offer the required 8.4 release, use the MySQL Community Server download page at <https://dev.mysql.com/downloads/mysql/>.
3. Run the installer. Select **Server only** if you only need the database server and command-line client. Select **Developer Default** if you also want MySQL Workbench.
4. In MySQL Configurator, configure a standalone server.
5. Keep TCP/IP enabled and use port `3306`, unless that port is already occupied.
6. Configure MySQL as a Windows service. The service is commonly named `MySQL84`, but use the name shown by your installer.
7. Set a root password and keep it available for the one-time database setup. Do not use root in the Flask application.

Open a **new PowerShell** window and verify:

```powershell
mysql --version
Get-Service *mysql*
```

If `mysql` is not recognized, add the MySQL Server `bin` directory to PATH. A common location is:

```text
C:\Program Files\MySQL\MySQL Server 8.4\bin
```

You can also open **MySQL 8.4 Command Line Client** from the Start menu.

If the service is stopped, open PowerShell as Administrator and start it using the actual service name shown by `Get-Service`:

```powershell
Start-Service MySQL84
```

Connect:

```powershell
mysql -u root -p
```

If your service has a different name, replace `MySQL84` in the service command.

### Ubuntu / Debian

For this tutorial, use Oracle's MySQL APT repository and explicitly select the MySQL 8.4 series. The distribution's default `mysql-server` package may install a different version or a MySQL-compatible alternative.

1. Open the official [MySQL APT repository guide](https://dev.mysql.com/doc/mysql-apt-repo-quick-guide/en/).
2. Download the APT repository configuration package for your Ubuntu or Debian release from <https://dev.mysql.com/downloads/repo/apt/>.
3. Install the downloaded package. Replace the filename below with the exact filename you downloaded:

```bash
sudo dpkg -i mysql-apt-config_*_all.deb
```

4. In the configuration screen, select **MySQL Server & Cluster**, then select **mysql-8.4**. Confirm and exit.
5. Install MySQL:

```bash
sudo apt-get update
sudo apt-get install mysql-server
```

During installation, follow the prompts. Depending on the package and authentication configuration, you may be asked to set a root password.

Check and start the service:

```bash
sudo systemctl status mysql
sudo systemctl start mysql
sudo systemctl enable mysql
```

Connect using the local administrative socket:

```bash
sudo mysql
```

If your installation uses password authentication for root instead, connect with:

```bash
mysql -u root -p
```

### Fedora / RHEL / Rocky Linux / AlmaLinux / Oracle Linux

Use Oracle's MySQL Yum repository to install the 8.4 LTS Community Server. Do not assume that the distribution's native `mysql` package installs Oracle MySQL 8.4.

1. Open the official [MySQL Yum repository guide](https://dev.mysql.com/doc/refman/8.4/en/linux-installation-yum-repo.html).
2. Download the repository-release RPM appropriate for your distribution and version from the MySQL Yum repository download page linked there.
3. Install the RPM. Replace the filename with the one you downloaded:

```bash
sudo dnf install ./mysql84-community-release-*.noarch.rpm
```

On systems using `yum`, use `sudo yum localinstall` instead.
4. Confirm that the MySQL 8.4 LTS repository is enabled:

```bash
sudo dnf repolist enabled | grep mysql
```

On RHEL 8-compatible systems, if the distribution's built-in MySQL module masks the Oracle packages, disable that module as described in the official guide:

```bash
sudo dnf module disable mysql
```

5. Install and start MySQL:

```bash
sudo dnf install mysql-community-server
sudo systemctl enable --now mysqld
sudo systemctl status mysqld
```

On older systems, replace `dnf` with `yum` where appropriate.

The initial root password is commonly generated and written to the MySQL error log. Find it using the command documented for your package, commonly:

```bash
sudo grep 'temporary password' /var/log/mysqld.log
```

Then run:

```bash
mysql -u root -p
```

Change the temporary password when prompted. If the log path or initial-password procedure differs on your distribution, follow the post-installation instructions in the official MySQL guide.

### Alternative: Docker (macOS, Windows, or Linux)

Use this option if you cannot install or start a native MySQL service. It requires Docker Desktop on macOS/Windows or Docker Engine on Linux.

Start a MySQL 8.4 container:

```bash
docker run --name campusboard-mysql \
  -e MYSQL_ROOT_PASSWORD=LocalRootPass_ChangeMe \
  -p 127.0.0.1:3306:3306 \
  -d mysql:8.4
```

Wait for the server to initialize:

```bash
docker logs -f campusboard-mysql
```

When the log indicates that MySQL is ready for connections, press `Ctrl+C` to stop following the logs. The container continues running.

Connect:

```bash
docker exec -it campusboard-mysql mysql -u root -p
```

Enter `LocalRootPass_ChangeMe` when prompted. This is a local teaching password, not a password to reuse elsewhere.

To stop and restart the container:

```bash
docker stop campusboard-mysql
docker start campusboard-mysql
```

To remove the container and its data:

```bash
docker rm -f campusboard-mysql
```

**Warning:** This basic Docker command does not attach a persistent volume. Removing the container deletes its database data. Do not remove it until you have finished the exercise or exported the data.

If port `3306` is already occupied, change the host-side port mapping, for example `-p 127.0.0.1:3307:3306`. In that case, use port `3307` in the application connection URL later in this guide.

## 2. Verify the server

Open a terminal and connect as an administrator using the method for your installation:

| Installation | Administrative connection |
|---|---|
| macOS, Homebrew | `mysql -u root` or `mysql -u root -p` |
| macOS, Oracle installer | `mysql -u root -p` (or the full client path) |
| Windows | `mysql -u root -p` |
| Ubuntu / Debian | `sudo mysql` or `mysql -u root -p` |
| Fedora / RHEL family | `mysql -u root -p` |
| Docker | `docker exec -it campusboard-mysql mysql -u root -p` |

At the MySQL prompt, run:

```sql
SELECT VERSION();
SELECT @@hostname, @@port;
```

Expected:

- The version begins with `8.4`.
- The port is `3306`, unless you deliberately chose another port.

Exit:

```sql
EXIT;
```

Check that the server is listening on the expected port.

**macOS / Linux:**

```bash
lsof -nP -iTCP:3306 -sTCP:LISTEN
```

**Windows PowerShell:**

```powershell
Get-NetTCPConnection -LocalPort 3306 -State Listen
```

If nothing is listening, the MySQL service may not be running, may be configured on another port, or may still be starting.

## 3. Create the database and application user

Use an administrative MySQL account for this one-time setup. Do not put the administrative account in the Flask connection string.

Connect using the administrative command from Section 2. If you used Docker, run the SQL commands inside the container's MySQL prompt.

Run the following SQL. Replace `REPLACE_WITH_A_LONG_RANDOM_PASSWORD` with a unique password. For this tutorial, use a long password made from letters, numbers, underscores, and hyphens. This avoids URL-encoding problems when the password is placed in the SQLAlchemy connection URL in Section 6.

```sql
CREATE DATABASE campusboard
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

CREATE USER 'campusboard_app'@'127.0.0.1'
  IDENTIFIED BY 'REPLACE_WITH_A_LONG_RANDOM_PASSWORD';

GRANT ALL PRIVILEGES ON campusboard.*
  TO 'campusboard_app'@'127.0.0.1';

SHOW GRANTS FOR 'campusboard_app'@'127.0.0.1';
```

`FLUSH PRIVILEGES` is not required after `CREATE USER` or `GRANT`.

The application will connect to `127.0.0.1` over TCP, so the account is created for that host. MySQL accounts include both a username and a host component. An account for `'campusboard_app'@'localhost'` is a separate account and is not needed for the connection URL used in this guide.

Exit:

```sql
EXIT;
```

## 4. Test the application database user

Connect over TCP to the loopback address. This tests the same host and port that the Flask application will use.

**macOS / Linux:**

```bash
mysql --protocol=TCP -h 127.0.0.1 -P 3306 \
  -u campusboard_app -p campusboard
```

**Windows PowerShell:**

```powershell
mysql --protocol=TCP -h 127.0.0.1 -P 3306 -u campusboard_app -p campusboard
```

**Docker:** If the MySQL client is installed on your computer, use the same command. Otherwise, connect inside the container:

```bash
docker exec -it campusboard-mysql mysql \
  --protocol=TCP -h 127.0.0.1 -P 3306 \
  -u campusboard_app -p campusboard
```

Enter the application user's password.

At the MySQL prompt, run:

```sql
SELECT DATABASE();
SELECT CURRENT_USER();
SHOW TABLES;
```

Expected:

- `DATABASE()` returns `campusboard`.
- `CURRENT_USER()` identifies `campusboard_app` and the host entry used for the connection.
- `SHOW TABLES` returns an empty set because the Flask tables have not yet been created.

Exit:

```sql
EXIT;
```

If this connection fails, do not proceed to Flask. Fix MySQL connectivity first.

## 5. Configure the Flask connection URL

In the repository root, create `.env` by copying `.env.example`.

**macOS / Linux:**

```bash
cp .env.example .env
```

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set:

```dotenv
SECRET_KEY=replace-this-with-a-long-random-value
DATABASE_URL=mysql+pymysql://campusboard_app:REPLACE_WITH_A_LONG_RANDOM_PASSWORD@127.0.0.1:3306/campusboard
AWS_REGION=ap-south-1
S3_BUCKET=
```

Use the same password entered in the SQL statements.

Generate a Flask secret key with Python:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

On Windows, if `python` is not recognized, try:

```powershell
py -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output into `SECRET_KEY`.

If you used Docker with a different host-side port, replace `3306` in `DATABASE_URL` with that port.

`S3_BUCKET` may remain empty for database-only local testing. The application can display, create, and comment on ideas without S3, but image uploads will not work until an S3 bucket and AWS credentials are configured.

If your database password contains URL-reserved characters, percent-encode the password component before placing it in `DATABASE_URL`. For example, `@` becomes `%40`, `:` becomes `%3A`, and `/` becomes `%2F`. Do not encode the entire URL.

## 6. Common MySQL problems

### `Can't connect to MySQL server on '127.0.0.1'`

Check that the service is running and that the port is correct.

**macOS, Homebrew:**

```bash
brew services list
brew services restart mysql@8.4
```

**macOS, Oracle installer:** Check the MySQL preference pane or launch daemon. Confirm that the server is configured to listen on port `3306`.

**Windows:**

```powershell
Get-Service *mysql*
Start-Service MySQL84
```

Replace `MySQL84` with the actual service name. Run PowerShell as Administrator to start a system service.

**Ubuntu / Debian:**

```bash
sudo systemctl status mysql
sudo systemctl restart mysql
```

**Fedora / RHEL family:**

```bash
sudo systemctl status mysqld
sudo systemctl restart mysqld
```

**Docker:**

```bash
docker ps
docker logs campusboard-mysql
```

Confirm that MySQL is listening on the port used in `DATABASE_URL`. If another process already uses port `3306`, stop the duplicate service or deliberately configure a different host-side port and update `DATABASE_URL`.

### `Access denied for user 'campusboard_app'`

Check:

- The username is exactly `campusboard_app`.
- The password matches the `CREATE USER` statement.
- The connection uses `127.0.0.1` and the correct port.
- The account exists for the host `127.0.0.1`.

As an administrator, run:

```sql
SELECT user, host
FROM mysql.user
WHERE user = 'campusboard_app';
```

If the account exists but the password is uncertain, reset it as an administrator:

```sql
ALTER USER 'campusboard_app'@'127.0.0.1'
  IDENTIFIED BY 'YOUR_NEW_LONG_RANDOM_PASSWORD';
```

Update `.env` to use the new password.

### `Unknown database 'campusboard'`

Create it using Section 3, then verify:

```sql
SHOW DATABASES LIKE 'campusboard';
```

### `mysql: command not found` or `mysql is not recognized`

The MySQL client is not on PATH.

- **Homebrew macOS:** Add the `mysql@8.4` `bin` directory to PATH as shown in Section 1.
- **Oracle macOS installer:** Try `/usr/local/mysql/bin/mysql`.
- **Windows:** Add the MySQL Server `bin` directory to PATH, or open MySQL Command Line Client from the Start menu.
- **Linux:** Confirm that the MySQL client package was installed. Use the package manager instructions in the official MySQL guide.

Open a new terminal after changing PATH.

### Port `3306` is already in use

You may have another MySQL installation, MariaDB, or a Docker container running.

Identify the process:

**macOS / Linux:**

```bash
lsof -nP -iTCP:3306 -sTCP:LISTEN
```

**Windows PowerShell:**

```powershell
Get-NetTCPConnection -LocalPort 3306 -State Listen
```

Stop the service or container you do not intend to use. Do not delete database directories to resolve a port conflict.

Alternatively, configure this MySQL instance to use another port and use that same port in both the test connection and `DATABASE_URL`.

### The installed version is not 8.4

Run:

```sql
SELECT VERSION();
```

If it reports MariaDB, MySQL 8.0, or another version, you have not installed the intended MySQL release. Follow the Oracle repository or installer instructions for your operating system. Avoid mixing Oracle packages with a distribution's native MySQL-compatible packages.

### MySQL starts, then immediately stops

Inspect the service logs rather than repeatedly reinstalling it.

- **macOS Homebrew:** `brew services list` and `brew services info mysql@8.4`
- **Windows:** Open Event Viewer and inspect the MySQL service error; also inspect the MySQL data directory's `.err` log.
- **Ubuntu / Debian:** `sudo journalctl -u mysql --no-pager -n 80`
- **Fedora / RHEL family:** `sudo journalctl -u mysqld --no-pager -n 80`
- **Docker:** `docker logs campusboard-mysql`

Common causes include a port conflict, invalid configuration, insufficient disk space, or an existing data directory created by another MySQL version. Do not delete or reinitialize a data directory unless you are certain it contains no data you need.

## 7. Completion checklist

- [ ] MySQL Server 8.4 is installed and running.
- [ ] It listens on the port used in the connection URL.
- [ ] Database `campusboard` exists.
- [ ] Application user `campusboard_app` can connect over TCP to `127.0.0.1`.
- [ ] The application user has privileges on `campusboard.*`.
- [ ] `.env` contains a MySQL SQLAlchemy URL.
- [ ] `.env` is not tracked by Git.

Continue to `README_03_LOCAL_APPLICATION.md`.

## Official references

- [MySQL 8.4 installation overview](https://dev.mysql.com/doc/refman/8.4/en/installing.html)
- [MySQL on macOS](https://dev.mysql.com/doc/refman/8.4/en/macos-installation.html)
- [MySQL on Windows](https://dev.mysql.com/doc/refman/8.4/en/windows-installation.html)
- [MySQL on Linux](https://dev.mysql.com/doc/refman/8.4/en/linux-installation.html)
- [MySQL APT repository guide](https://dev.mysql.com/doc/mysql-apt-repo-quick-guide/en/)
- [MySQL Yum repository guide](https://dev.mysql.com/doc/mysql-yum-repo-quick-guide/en/)
