# 7. RDS MySQL: Managed Database

This section creates a managed MySQL database in Amazon RDS and restricts access to the EC2 application server.

The target is:
- Engine: MySQL 8.4 LTS, if offered in the selected Region.
- Database name: `campusboard`.
- Network: private subnets in two Availability Zones.
- Access: TCP 3306 only from `campusboard-ec2-sg`.

Do not make the database publicly accessible.

## 7.1 Create a DB subnet group

RDS uses a DB subnet group to determine which subnets it can use. Create the group from the two private subnets.

1. Open **RDS → Subnet groups → Create DB subnet group**.
2. Name: `campusboard-db-subnet-group`.
3. Description: `Private subnets for Campus Ideas Board`.
4. VPC: `campusboard-vpc`.
5. Add the private subnets:
   - `campusboard-private-a` in `ap-south-1a`
   - `campusboard-private-b` in `ap-south-1b`
6. Create the subnet group.

Confirm that the subnet group contains subnets in at least two AZs.

## 7.2 Create the RDS database

1. Open **RDS → Databases → Create database**.
2. Choose **Standard create**.
3. Engine: **MySQL**.
4. Engine version: select MySQL 8.4 LTS if available. Otherwise select the MySQL version supported by the application and record the selected version.
5. Template: choose a development or free-tier template only if it is available and appropriate for the AWS account. Template availability and pricing vary.
6. DB instance identifier: `campusboard-db`.
7. Credentials:
   - Master username: choose a name such as `dbadmin`.
   - Set a strong master password and store it securely.
   - Prefer managed credentials through AWS Secrets Manager if that option is available and the workshop budget permits.

For a small workshop:
- Choose a small burstable instance class supported in the Region.
- Use a small storage allocation suitable for the exercise.
- Disable Multi-AZ deployment unless the exercise specifically requires high availability. The subnet group still needs subnets in two AZs.
- Do not enable public access.

## 7.3 Configure connectivity

Under Connectivity:

- VPC: `campusboard-vpc`.
- DB subnet group: `campusboard-db-subnet-group`.
- Public access: **No**.
- VPC security group: select `campusboard-rds-sg`.
- Availability Zone: leave automatic unless the exercise requires a specific AZ.
- Port: `3306`.

The RDS security group must have an inbound MySQL rule whose source is `campusboard-ec2-sg`. Do not allow inbound port 3306 from the internet.

Create the database and wait until its status is **Available**.

## 7.4 Record the RDS endpoint

Open the database details page and copy the endpoint hostname. It will resemble:

    campusboard-db.xxxxxxxxxxxx.ap-south-1.rds.amazonaws.com

Do not include `https://`, a port suffix or a trailing slash in the hostname.

Record:
- Endpoint hostname.
- Port, normally `3306`.
- Master username.
- Database name, `campusboard`.

The endpoint is not a web address. It is the hostname the MySQL client uses to connect.

## 7.5 Create the application database and user

For the workshop, connect to RDS from the EC2 instance. Do not open the database to your laptop or the public internet.

On EC2, install a MySQL client:

    sudo apt update
    sudo apt install -y mysql-client

Connect using the RDS endpoint and master username:

    mysql -h RDS_ENDPOINT -P 3306 -u RDS_USERNAME -p

Replace `RDS_ENDPOINT` and `RDS_USERNAME` with your values. Enter the master password when prompted.

Create the database and a separate application user. Replace the sample password with a strong password:

    CREATE DATABASE campusboard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    CREATE USER 'campusboard_app'@'%' IDENTIFIED BY 'REPLACE_WITH_A_STRONG_PASSWORD';
    GRANT ALL PRIVILEGES ON campusboard.* TO 'campusboard_app'@'%';
    FLUSH PRIVILEGES;

The `%` host pattern is acceptable here because the RDS security group limits network access to the EC2 security group. Do not expose port 3306 publicly.


> [!CAUTION]
> **Emergency cleanup only**
>
> Run the following 2 SQL commands **only if something went wrong while executing the database and user creation commands above** and you need to undo their effects. Do not run them as part of the normal setup.
```sql
DROP USER IF EXISTS 'campusboard_app'@'%';
DROP DATABASE IF EXISTS campusboard;
```

If everything went well, exit My
Exit:

    EXIT;

Use the application account in Flask. Do not use the RDS master account in the application.

## 7.6 Test connectivity from EC2

Install the MySQL client if it is not already installed, then run:

    mysql -h RDS_ENDPOINT -P 3306 -u campusboard_app -p campusboard

After connecting, run:

    SELECT VERSION();
    SHOW TABLES;

At first, `SHOW TABLES` may return no application tables. The tables will be created by the application's database initialization step in Section 9.

If the connection times out:
- Confirm the RDS instance is Available.
- Confirm EC2 and RDS are in the same VPC.
- Confirm `campusboard-rds-sg` allows TCP 3306 from `campusboard-ec2-sg`.
- Confirm the EC2 instance is attached to `campusboard-ec2-sg`.
- Confirm the DB subnet group uses the intended private subnets.
- Check the endpoint and port.

If the connection is rejected with an authentication error, verify the username, password and database name. A timeout is usually a network or security-group problem; an access-denied error is usually a credential or privilege problem.

## 7.7 Configure the application database URL

Edit the EC2 `.env` file:

    nano /home/ubuntu/DPCS_CloudApp/.env

Set:

    DATABASE_URL=mysql+pymysql://campusboard_app:URL_ENCODED_PASSWORD@RDS_ENDPOINT:3306/campusboard

Replace the placeholders. URL-encode special characters in the password. Do not surround the URL with quotes unless the application's environment-file parser requires them.

Keep the local database URL on your own computer. The EC2 `.env` must point to the RDS endpoint.

Continue to README_06 and finish it before coming here!

Restart the application after changing the environment:

    sudo systemctl restart campusboard

## 7.8 Database initialization

If the project defines the Flask CLI command used locally, run it on EC2 from the project directory and with the virtual environment active:

    cd /home/ubuntu/DPCS_CloudApp
    source .venv/bin/activate
    flask --app app init-db

If this command is not defined in the deployed version, do not invent a replacement. Inspect the application's database initialization code and use the project's actual setup procedure.

Check the database tables:

    mysql -h RDS_ENDPOINT -P 3306 -u campusboard_app -p campusboard

Then:

    SHOW TABLES;

The expected application tables include the tables used for categories, ideas and comments.

## 7.9 RDS checkpoint

- [ ] DB subnet group includes both private subnets in different AZs.
- [ ] RDS MySQL database is Available.
- [ ] Public access is disabled.
- [ ] RDS security group permits TCP 3306 only from the EC2 security group.
- [ ] EC2 can connect using the application database user.
- [ ] The EC2 `.env` points to the RDS endpoint.
- [ ] Application tables have been initialized.

Continue to Section 8 for the EC2 instance's S3 permissions.
