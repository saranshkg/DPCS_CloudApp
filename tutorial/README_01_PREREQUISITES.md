# 01. Prerequisites

This guide prepares your computer to run the Campus Ideas Board repository locally.

Repository: <https://github.com/saranshkg/DPCS_CloudApp>

The application uses:

- Python and Flask for the web application.
- MySQL 8.4 LTS for relational data.
- SQLAlchemy for database access.
- Amazon S3 for optional image uploads.
- Flask-WTF for CSRF protection.

Follow the instructions for your operating system. If MySQL is already installed, do not install another distribution. Multiple installations can compete for port `3306`.

## 1. Required software

| Software | Recommended version | Required for |
|---|---:|---|
| Git | Current stable | Cloning the repository |
| Python | 3.11 or 3.12 | Running Flask |
| MySQL Server | 8.4 LTS | Local relational database |
| pip | Bundled with Python | Installing Python dependencies |
| Terminal | macOS Terminal, PowerShell, Windows Terminal, or Linux shell | Running commands |

Optional until image uploads are tested:

- AWS CLI v2
- An AWS account
- An S3 bucket and an IAM identity with limited access to that bucket

## 2. Check whether tools are already installed

Run these commands in a terminal.

**macOS / Linux**

```bash
git --version
python3 --version
python3 -m pip --version
mysql --version
```

**Windows PowerShell**

```powershell
git --version
py --version
py -m pip --version
mysql --version
```

If a command is not found, install the corresponding software below. Check that `mysql --version` reports MySQL 8.4.x.

## 3. Install Git

- **macOS:** Install Xcode Command Line Tools with `xcode-select --install`, or install Git from <https://git-scm.com/download/mac>.
- **Windows:** Install Git for Windows from <https://git-scm.com/download/win>. Use Git Bash or PowerShell for the commands in these guides.
- **Ubuntu / Debian:**

```bash
sudo apt update
sudo apt install -y git
```

- **Fedora / RHEL family:**

```bash
sudo dnf install -y git
```

Verify:

```bash
git --version
```

## 4. Install Python

Use Python 3.11 or 3.12. The project will use a virtual environment rather than installing packages into the system Python.

- **macOS:** Install from <https://www.python.org/downloads/macos/> or use Homebrew:

```bash
brew install python@3.12
```

- **Windows:** Install Python 3.12 from <https://www.python.org/downloads/windows/>. In the installer, enable **Add python.exe to PATH**. The `py` launcher is recommended on Windows.
- **Ubuntu / Debian:**

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

- **Fedora / RHEL family:**

```bash
sudo dnf install -y python3 python3-pip
```

Verify:

**macOS / Linux**

```bash
python3 --version
python3 -m venv --help
```

**Windows**

```powershell
py --version
py -m venv --help
```

The version should be Python 3.11.x or 3.12.x. On Linux, if your distribution's default Python is older, install Python 3.11 or 3.12 using the instructions for that distribution.

## 5. Clone the repository

Choose a working directory, then run:

```bash
git clone https://github.com/saranshkg/DPCS_CloudApp.git
cd DPCS_CloudApp
```

Confirm that the expected files exist:

```text
DPCS_CloudApp/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── templates/
    ├── base.html
    ├── index.html
    ├── new_idea.html
    └── idea_detail.html
```

If `git clone` reports that the directory already exists, either use the existing directory or choose a different parent directory. Do not clone one copy inside another copy.

## 6. Create a Python virtual environment

A virtual environment keeps this project's packages separate from other Python projects.

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the current-user policy below, then retry:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Alternatively, use Command Prompt:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
```

When activated, the shell prompt normally begins with `(.venv)`.

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Inside an activated environment, use `python` and `python -m pip` on all platforms. This avoids accidentally installing packages into a different Python installation.

## 7. MySQL installation

Install MySQL Server 8.4 LTS by following `README_02_LOCAL_MYSQL.md`.

If MySQL is already installed, verify its version and confirm that its service is running. The local application will connect to `127.0.0.1` on port `3306`, unless you deliberately configured another port.

## 8. Optional: AWS CLI

The application can run locally without AWS credentials if you do not upload images. Image uploads require an S3 bucket and AWS credentials or another supported AWS credential source.

### Install AWS CLI v2 using the official instructions:

<https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html>

Do not create or use root access keys. For local development, use a dedicated IAM identity or AWS IAM Identity Center credentials with access restricted to the workshop bucket. On EC2, use an instance role instead of long-lived access keys.

### Add AWS CLI's user-local installation directory to PATH (Linux)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify installation
aws --version

## 9. Ready-to-continue checklist

Before proceeding to `README_02_LOCAL_MYSQL.md`, confirm:

- [ ] Git is installed.
- [ ] Python 3.11 or 3.12 is installed.
- [ ] The repository is cloned.
- [ ] The terminal is in the repository root.
- [ ] A `.venv` virtual environment exists and is activated.
- [ ] MySQL Server 8.4 LTS is installed and ready to run.
- [ ] You know whether AWS/S3 image uploads are part of your local test.

