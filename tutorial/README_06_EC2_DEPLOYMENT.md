# 6. EC2 Deployment: Ubuntu, Gunicorn and Nginx

This section deploys the Flask application to an Ubuntu EC2 instance. It assumes:

- The application runs locally.
- MySQL and S3 integration have already been tested locally.
- The VPC, public subnet, Internet Gateway and security groups from Section 5 exist.
- The application source is available in the GitHub repository.

The EC2 instance will run Flask through Gunicorn. Nginx will accept public HTTP requests and forward them to Gunicorn on localhost.

## 6.1 Launch an EC2 instance

1. Open **EC2 → Instances → Launch instances**.
2. Name: `campusboard-app`.
3. AMI: Ubuntu Server 24.04 LTS, 64-bit x86.
4. Instance type: `t3.micro` for a small workshop deployment, subject to current account eligibility and workload.
5. Create or select an SSH key pair. Download the private key and keep it secure.
6. Network settings:
   - VPC: `campusboard-vpc`
   - Subnet: `campusboard-public-a`
   - Auto-assign public IP: Enable
   - Security group: `campusboard-ec2-sg`
7. Storage: the default 8 GiB gp3 volume is sufficient for this exercise.
8. Launch the instance.

Wait until the instance is running and both status checks pass. Record its public IPv4 address or public DNS name.

## 6.2 Connect over SSH

On the computer holding the downloaded key, restrict its permissions:

    chmod 400 campusboard-key.pem

Connect:

    ssh -i campusboard-key.pem ubuntu@EC2_PUBLIC_IP

Replace `EC2_PUBLIC_IP` with the instance's public IPv4 address.

If the connection times out, check:
- The instance has a public IPv4 address.
- The subnet route table sends `0.0.0.0/0` to the Internet Gateway.
- The EC2 security group allows TCP 22 from your current public IP.
- The correct key pair and username are being used. For Ubuntu AMIs, the username is `ubuntu`.

## 6.3 Install system packages

Update Ubuntu and install Python tooling, Git and Nginx:

    sudo apt update
    sudo apt upgrade -y
    sudo apt install -y python3 python3-venv python3-pip python3-dev build-essential git nginx

Check versions:

    python3 --version
    git --version
    nginx -v

## 6.4 Clone the application

Clone the project:

    git clone https://github.com/saranshkg/DPCS_CloudApp.git
    cd DPCS_CloudApp

If the repository is private, configure an approved Git authentication method. Do not put a personal access token directly in a shell command or repository URL.

Inspect the files:

    ls -la

The deployment assumes the repository contains `app.py` and `requirements.txt`, and that the Flask application object is named `app`.

## 6.5 Create the Python environment

    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn

If Gunicorn is already listed in `requirements.txt`, the separate installation is unnecessary.

Check that the application imports:

    python -c "from app import app; print(app)"

Resolve any missing dependency or import error before configuring Nginx.

## 6.6 Configure environment variables

Create the environment file:

    nano .env

Set the production values:

    SECRET_KEY=REPLACE_WITH_A_LONG_RANDOM_SECRET
    DATABASE_URL=mysql+pymysql://DB_USER:URL_ENCODED_PASSWORD@RDS_ENDPOINT:3306/campusboard
    AWS_REGION=ap-south-1
    S3_BUCKET=dpcs-campusboard-1

Replace:
- `SECRET_KEY` with a new random value.
- `DB_USER` with the RDS application username.
- `URL_ENCODED_PASSWORD` with the URL-encoded database password.
- `RDS_ENDPOINT` with the RDS endpoint hostname.

Do not copy the local database URL into this file. Do not commit `.env` to Git.

If the password contains characters such as `@`, `:`, `/`, `#` or `%`, URL-encode the password before placing it in the SQLAlchemy URL. Keep the username and hostname unchanged.

Restrict access to the file:

    chmod 600 .env

The application must load `.env` during startup, as it does in the local setup. If it does not, configure the systemd service in Section 6.8 to load the file explicitly.

## 6.7 Test Gunicorn locally on the instance

With the virtual environment active:

    gunicorn --workers 2 --bind 127.0.0.1:8000 app:app

From another SSH session, test:

    curl -I http://127.0.0.1:8000

A valid HTTP response confirms that Gunicorn can serve the application locally. Stop the foreground process with `Ctrl+C`.

If the application needs database or S3 access, those services must be configured before testing routes that use them.

## 6.8 Run Gunicorn as a systemd service

Create a service file:

    sudo nano /etc/systemd/system/campusboard.service

Use the following content. Replace `/home/ubuntu/DPCS_CloudApp` if the repository is in a different location.

    [Unit]
    Description=Campus Ideas Board Flask application
    After=network.target

    [Service]
    User=ubuntu
    Group=www-data
    WorkingDirectory=/home/ubuntu/DPCS_CloudApp
    EnvironmentFile=/home/ubuntu/DPCS_CloudApp/.env
    ExecStart=/home/ubuntu/DPCS_CloudApp/.venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8000 app:app
    Restart=always
    RestartSec=5

    [Install]
    WantedBy=multi-user.target

Set ownership and permissions:

    sudo chown -R ubuntu:www-data /home/ubuntu/DPCS_CloudApp
    sudo chmod 640 /home/ubuntu/DPCS_CloudApp/.env

Enable and start the service:

    sudo systemctl daemon-reload
    sudo systemctl enable campusboard
    sudo systemctl start campusboard

Check its status:

    sudo systemctl status campusboard

View recent logs:

    sudo journalctl -u campusboard -n 100 --no-pager

Follow logs while testing:

    sudo journalctl -u campusboard -f

If the service fails, check the working directory, virtual environment path, `app:app` import target, environment file and application logs.

## 6.9 Configure Nginx as a reverse proxy

Create an Nginx site:

    sudo nano /etc/nginx/sites-available/campusboard

Use:

    server {
        listen 80;
        server_name _;

        client_max_body_size 10M;

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

Enable the site and disable the default site:

    sudo ln -s /etc/nginx/sites-available/campusboard /etc/nginx/sites-enabled/campusboard
    sudo rm -f /etc/nginx/sites-enabled/default

Validate and reload:

    sudo nginx -t
    sudo systemctl reload nginx
    sudo systemctl enable nginx

Check status:

    sudo systemctl status nginx

## 6.10 Test the public application

Open this address in a browser:

    http://EC2_PUBLIC_IP

The Campus Ideas Board should load through Nginx.

At this point, the application may still fail on database or image operations until Sections 7–9 are completed. A page load confirms the EC2, Gunicorn and Nginx path, not the full deployment.

## 6.11 Useful operations

Restart the application after changing application code or `.env`:

    sudo systemctl restart campusboard

Check application logs:

    sudo journalctl -u campusboard -n 100 --no-pager

Check Nginx logs:

    sudo tail -n 100 /var/log/nginx/error.log
    sudo tail -n 100 /var/log/nginx/access.log

Check listening ports:

    sudo ss -ltnp

Gunicorn should listen only on `127.0.0.1:8000`. Public traffic should enter through Nginx on port 80.

## 6.12 Deployment checkpoint

- [ ] EC2 is in the public subnet and has a public IPv4 address.
- [ ] SSH works from the permitted client IP.
- [ ] Python environment and dependencies are installed.
- [ ] The application imports successfully.
- [ ] Gunicorn runs as a systemd service.
- [ ] Nginx forwards HTTP traffic to Gunicorn.
- [ ] The application loads at `http://EC2_PUBLIC_IP`.

Continue to Section 7 to create the managed MySQL database in RDS.
