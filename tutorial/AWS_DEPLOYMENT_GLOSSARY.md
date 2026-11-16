# AWS Deployment Glossary and Concepts Guide
## Campus Ideas Board

This guide explains the AWS concepts used in the Campus Ideas Board deployment. It is a reference, not a sequence of setup instructions.

## 1. Architecture at a glance

The application has three main parts:
- **EC2** runs Flask, Gunicorn and Nginx.
- **RDS for MySQL** stores ideas, comments and other structured data.
- **S3** stores uploaded image files.

```text
Users' browsers
      |
   HTTP :80
      |
Internet Gateway
      |
VPC: campusboard-vpc (10.0.0.0/16)
      |
Public subnet: 10.0.1.0/24
EC2: campusboard-app
Nginx :80 -> Gunicorn :8000
      |
      +---- Private VPC network ----> RDS MySQL :3306
      |
      +---- AWS API ----------------> S3 bucket
                                      dpcs-campusboard-1
                                      images/...
```

S3 is an AWS service accessed through its API. It is not inside the VPC or one of its subnets.

### Resource names used in this project

| Concept | Project resource |
|---|---|
| AWS Region | `ap-south-1` (Mumbai) |
| VPC | `campusboard-vpc`, `10.0.0.0/16` |
| Public subnet | `campusboard-public-a`, `10.0.1.0/24` |
| Private subnet A | `campusboard-private-a`, `10.0.11.0/24` |
| Private subnet B | `campusboard-private-b`, `10.0.12.0/24` |
| EC2 instance | `campusboard-app` |
| EC2 security group | `campusboard-ec2-sg` |
| RDS security group | `campusboard-rds-sg` |
| RDS database | `campusboard-db` |
| S3 bucket | `dpcs-campusboard-1` |
| S3 object prefix | `images/` |
| EC2 IAM role | `campusboard-ec2-role` |
| IAM policy | `CampusBoardS3ImagesPolicy` |

These are names chosen for this deployment, not AWS concepts.

## 2. Hosting and public access

**Hosting:** Running an application on a server that other people can reach over a network. In this project, Flask is hosted on an Ubuntu EC2 instance.

**Server:** A computer that provides a service to other computers. The EC2 instance is the server. It runs the application processes and responds to browser requests.

**Public IP address:** An internet-routable address users can connect to, subject to routing and security rules. Users open the application at `http://EC2_PUBLIC_IP`, replacing the placeholder with the address shown in the EC2 Console.

A public IP alone does not make the application reachable. The subnet route, Internet Gateway, security group, Nginx and application process must all be working.

**Private IP address:** An address used within a private network such as the VPC. EC2 and RDS communicate over private network addresses. RDS does not need a public IP for this application.

**Automatically assigned public IP:** EC2 can automatically assign a public IPv4 address when an instance is launched in a subnet configured to assign public addresses. It is generally not permanent. When an instance is stopped and started, the automatically assigned public IP can change. A reboot normally retains it. If it changes, use the new address shown in the EC2 Console.

**Elastic IP:** A static public IPv4 address allocated to an AWS account. It can be associated with an EC2 instance and retained when the instance is stopped or replaced, subject to reassociation. It is not required for this workshop. AWS may charge for public IPv4 addresses, including Elastic IPs, according to current pricing and usage conditions.

**Public DNS name:** A hostname that resolves to a public IP address. EC2 can provide a public DNS name when it has public IPv4 connectivity. Like an automatically assigned public IP, it can change when the public IP changes.

**Domain name:** A human-readable address such as `campusboard.example.com`. A domain is registered through a domain registrar and configured to direct users to the hosted application. It is optional for this workshop; users can access the application using the EC2 public IP.

**DNS record:** A DNS instruction that maps a name to an address or another hostname. Common records include:
- **A:** maps a hostname to an IPv4 address.
- **AAAA:** maps a hostname to an IPv6 address.
- **CNAME:** maps one hostname to another hostname.

A simple deployment with a stable public IP can use an A record. If the EC2 public IP changes, the record may need updating. A stable production setup generally uses a stable address or a load balancer.

**HTTP and HTTPS:** HTTP is the protocol browsers use to request web pages. This workshop initially serves the application over HTTP on port 80. HTTPS is HTTP protected by TLS encryption and normally uses port 443. A public production site should use HTTPS.

**TLS certificate:** Helps a browser verify a website's identity and establish an encrypted HTTPS connection. A certificate must be valid for the hostname users visit. A certificate for a domain does not automatically cover an EC2 public IP.

**Web server and application server:** A web server handles incoming HTTP requests and may serve static files or forward requests. An application server runs the application code. In this project, Nginx is the web server and reverse proxy, Gunicorn is the WSGI application server, and Flask contains the application logic.

**Reverse proxy:** Accepts a client request and forwards it to another server. Nginx accepts public requests on port 80 and forwards them to Gunicorn on the same EC2 machine.

**Binding address:** A process listens on an IP address and port. `127.0.0.1` means the local machine only; `0.0.0.0` means all network interfaces. Gunicorn should bind to `127.0.0.1:8000` in this setup. Nginx can reach it locally, but users on the internet cannot connect directly to port 8000.

**Public reachability checklist:** For users to open the application through the EC2 public IP:
1. EC2 has a current public IPv4 address or public DNS name.
2. Its subnet route table sends internet-bound traffic to an Internet Gateway.
3. The EC2 security group permits inbound HTTP on port 80.
4. Nginx is running and listening on port 80.
5. Nginx forwards requests to Gunicorn.
6. Gunicorn is running and Flask imports successfully.

SSH access is separate. Port 22 should be allowed only from the administrator's current public IP, not from the whole internet.

---

## 2. AWS account, identity and permissions

**AWS account:** The top-level container for AWS resources, access control and billing. EC2, RDS, S3 and IAM resources are created within an account.

**Root user:** The identity created when an AWS account is opened. It has extensive account-level authority. Use it only for account-level tasks that require it. Never use root credentials in an application or store root access keys on EC2.

**IAM (Identity and Access Management):** Controls who or what can perform which actions on which AWS resources. IAM controls AWS API permissions, not network connectivity.

**IAM user:** An identity that can be assigned credentials and permissions. It may represent a person or a legacy application identity. It is not the same as an application running on EC2.

**IAM role:** An identity that a trusted person or service can assume. A role provides temporary credentials rather than requiring permanent access keys to be stored in the application. In this project, `campusboard-ec2-role` is attached to EC2 so Boto3 can access S3.

**IAM policy:** A document containing permission statements. It specifies allowed or denied actions and the resources to which they apply. `CampusBoardS3ImagesPolicy` grants the application the S3 permissions needed for the `images/` objects in `dpcs-campusboard-1`.

**Trust policy:** Specifies who or what is allowed to assume a role. The EC2 role trusts the EC2 service. Its permissions policy separately specifies what the role can do.

**EC2 instance profile:** The mechanism through which an IAM role is associated with an EC2 instance. The Console generally handles this association when a role is attached.

**Temporary credentials:** Short-lived credentials issued when a role is assumed. They include an access key, secret key and session token. Boto3 can obtain and refresh them automatically when using the EC2 role.

**Least privilege:** Grant only the permissions needed for a task. The application needs access to its image objects, not unrestricted access to every S3 bucket or AWS service.

**Credentials versus permissions:** Credentials establish *who is making the request*. IAM policies determine *what that identity may do*.

**AWS CLI profile:** A named set of CLI configuration and credentials, often including a default Region. A local profile such as `campusboard-dev` is not automatically copied to EC2. On EC2, the application should use its attached IAM role.

## 4. SSH, PEM files and server access

**SSH (Secure Shell):** A protocol for securely opening a remote command-line session. The administrator uses SSH to connect to the Ubuntu EC2 instance.

**SSH key pair:** A pair consisting of a public key installed on the server and a private key kept by the administrator. The private key proves possession of the matching key without being sent to the server.

**PEM file:** The `.pem` file downloaded when creating an EC2 key pair normally contains the private key. Treat it like a password:
- Keep it private and secure.
- Do not commit it to Git.
- Do not send it to other people or paste it into chat.
- Keep a secure backup if you need to reconnect later.

On Linux or macOS, SSH commonly requires restrictive permissions:

    chmod 400 campusboard-key.pem

Connect to the Ubuntu instance:

    ssh -i campusboard-key.pem ubuntu@EC2_PUBLIC_IP

`ubuntu` is the default username for the Ubuntu AMI used in this guide. Other AMIs may use different usernames.

**Important:** The PEM file is for administrator SSH access. It is not an AWS IAM access key and is not used by Boto3 to access S3.

## 5. Regions and Availability Zones

**AWS Region:** A separate geographic AWS area. EC2 and RDS are created in a selected Region. This project uses `ap-south-1` (Mumbai). Keep EC2 and RDS in this Region, and configure the S3 client for the bucket's Region.

**Availability Zone (AZ):** An isolated location within a Region, made up of one or more data centres. A Region contains multiple AZs. The two private subnets in this project must be in different AZs for the RDS DB subnet group.

**Regional versus zonal resources:** Some resources belong to a Region; others are placed in a particular AZ. An EC2 instance runs in a subnet in one AZ. An S3 bucket is regional.

## 6. VPC and networking

**VPC (Virtual Private Cloud):** A logically isolated virtual network in an AWS Region. It provides the network boundary and IP address range for resources such as EC2 and RDS. `campusboard-vpc` uses `10.0.0.0/16`.

**CIDR block:** Notation describing an IP address range. `10.0.0.0/16` is the VPC range; `10.0.1.0/24` is a smaller range for a subnet. The number after `/` is the prefix length. A smaller prefix number represents a larger address range.

**Subnet:** A smaller IP address range inside a VPC. Each subnet belongs to one AZ.

| Subnet | CIDR | Purpose |
|---|---|---|
| Public subnet A | `10.0.1.0/24` | EC2 application server |
| Private subnet A | `10.0.11.0/24` | RDS placement |
| Private subnet B | `10.0.12.0/24` | RDS placement in another AZ |

**Public subnet:** A subnet whose route table has a route to an Internet Gateway for internet-bound traffic. A resource also needs suitable public addressing and security rules to be reachable from the internet. A subnet is not public merely because it is named “public”.

**Private subnet:** A subnet without a direct route to an Internet Gateway. Resources in it are not directly reachable from the public internet. RDS is placed in the private subnets; EC2 reaches it over the VPC network.

**Route table:** A set of rules that determines where network traffic is sent. Each subnet is associated with a route table. A route such as `0.0.0.0/0 -> Internet Gateway` sends IPv4 traffic for destinations outside the VPC through the IGW. The VPC's `local` route allows communication within its own address ranges.

**Internet Gateway (IGW):** Connects a VPC to the internet. A public subnet's route table uses it for internet-bound traffic. An IGW alone does not make a resource publicly reachable: routes, public addressing and security rules must also permit access.

**NAT Gateway:** Allows resources in private subnets to initiate connections to the internet without accepting unsolicited inbound internet connections. This project does **not** need a NAT Gateway. RDS does not need internet access, and EC2 is in the public subnet. A NAT Gateway would add cost without serving a requirement here.

**Public IPv4 address:** An address that can be used to reach an internet-facing resource, subject to routing and security rules. EC2 needs one for the workshop's simple SSH and browser access.

**Private IP address:** Used for communication within private networks such as the VPC. EC2 uses private network routing to connect to RDS.

**DNS and hostname:** DNS translates hostnames into IP addresses. AWS provides hostnames for services such as EC2 and RDS. The RDS endpoint is a DNS hostname, not a browser URL.

**Security group:** A stateful virtual firewall attached to a resource such as EC2 or RDS. It controls inbound and outbound traffic. Security groups can refer to another security group as a source.

In this project:
- `campusboard-ec2-sg` allows SSH from the administrator's IP and HTTP from users.
- `campusboard-rds-sg` allows MySQL traffic from `campusboard-ec2-sg`.

The RDS rule should use the EC2 security group as its source, not the EC2 public IP.

**Network ACL (NACL):** A subnet-level network filter. Unlike security groups, NACLs are stateless, so inbound and outbound rules must be considered separately. The default NACL is sufficient for this workshop; use security groups for the primary access controls.

**Network interface (ENI):** A virtual network card attached to an instance. It carries the instance's private IP address and security-group associations.

## 7. Compute, database and object storage

**EC2 (Elastic Compute Cloud):** AWS virtual servers. `campusboard-app` runs Ubuntu and hosts Flask, Gunicorn and Nginx.

**AMI (Amazon Machine Image):** A template used to launch an EC2 instance. It defines the operating system and may include preinstalled software. This project uses an Ubuntu Server AMI.

**Instance type:** Defines the virtual CPU, memory, network and other capacity available to an EC2 instance. A small burstable instance may be enough for a teaching application; actual capacity and price depend on the selected type and Region.

**EBS (Elastic Block Store):** Block storage volumes for EC2. The operating system, installed packages and local files are typically stored on EBS. EBS behaves like a disk attached to a server; S3 stores objects accessed through an API. An EBS volume may remain after EC2 termination, depending on its delete-on-termination setting.

**RDS (Relational Database Service):** A managed database service. AWS manages much of the database infrastructure. This project uses RDS for MySQL to store ideas and comments.

**DB subnet group:** Identifies the subnets in which RDS may place a database. It normally includes subnets in at least two AZs. `campusboard-db-subnet-group` contains the two private subnets.

**RDS endpoint:** The hostname used by a database client to connect to RDS. It is not a web address. A MySQL connection uses the endpoint hostname, port (normally `3306`), database name, username and password.

**S3 (Simple Storage Service):** Object storage. It stores files as objects in buckets and exposes them through AWS APIs. This project stores uploaded idea images in S3. MySQL stores the image object's key, not the image bytes.

**S3 bucket:** A container for S3 objects. Bucket names are globally unique within the AWS partition. This project's bucket is `dpcs-campusboard-1`.

**S3 object:** A stored file and its associated metadata, such as an uploaded PNG or JPEG.

**Object key:** The full name identifying an object inside a bucket. Example:

    images/0244c942026a4f04ba032ac6fdd14d08.png

S3 does not have real folders in the same sense as a computer filesystem. The slash-separated text is part of the object key.

**Prefix:** The beginning of an object key. `images/` groups this application's image objects in listings and IAM policy rules.

**Presigned URL:** A URL containing a time-limited signature that grants access to a specific S3 operation on a specific object. Flask generates one so a browser can display an image in a private bucket without making the bucket public. The URL's expiry does **not** delete the object. The object remains until explicitly deleted or removed by a lifecycle rule. A new presigned URL can be generated later.

**Boto3:** The AWS SDK for Python. Flask uses it to upload images and generate presigned URLs. On EC2, Boto3 can obtain credentials from the attached IAM role. Do not hard-code access keys in the application.

## 8. Application runtime and configuration

**Flask:** Python web framework that handles application routes, forms and responses.

**Gunicorn:** Production WSGI server that runs the Flask application. In this project it listens on `127.0.0.1:8000`.

**Nginx:** Web server and reverse proxy. It accepts browser requests on port 80 and forwards them to Gunicorn on the local machine.

**Reverse proxy:** A server that receives a client's request and forwards it to another server. Nginx is the public-facing entry point; Gunicorn runs behind it.

**Port:** Identifies a network service on a machine. A connection targets an IP address or hostname and a port.

| Port | Protocol/use | Project purpose |
|---:|---|---|
| 22 | SSH over TCP | Administrator connects to EC2 |
| 80 | HTTP over TCP | Browser connects to Nginx |
| 443 | HTTPS over TCP | Encrypted web traffic, optional extension |
| 8000 | HTTP/WSGI listener | Nginx connects to Gunicorn on localhost |
| 3306 | MySQL over TCP | EC2 connects to RDS |

Port 8000 should not be open to the public internet. Gunicorn listens on `127.0.0.1`, so only processes on EC2 can connect to it directly.

**Environment variable:** A configuration value supplied to a process at runtime. Examples: `DATABASE_URL`, `AWS_REGION`, `S3_BUCKET` and `SECRET_KEY`.

**`.env` file:** A convenient file containing environment-variable assignments. The application or service configuration loads these values at startup. It is not automatically secure: restrict its permissions and keep it out of Git. On EC2, systemd can load it using `EnvironmentFile`.

**Secret:** Sensitive information such as a database password or Flask signing key. Keep secrets out of source control and logs.

**Database URL:** Tells SQLAlchemy how to connect to a database. In this project it includes the MySQL driver, username, password, RDS endpoint, port and database name. Special characters in the password may need URL encoding.

**AWS CLI:** Tool for issuing AWS API requests from a terminal. It is useful for inspecting resources and testing permissions.

**AWS CLI versus AWS SDK:** The CLI is commonly used by a person in a terminal. Boto3 is used by Python code. A CLI command working on a developer's laptop does not prove EC2 has the same credentials, permissions or network access.

## 9. Security, reliability and cost

**Encryption at rest:** Protects stored data on services such as S3, RDS and EBS. S3 server-side encryption encrypts objects as AWS stores them.

**Encryption in transit:** Protects data while it travels over a network, usually with TLS/HTTPS. The workshop's basic Nginx setup uses HTTP; a public production deployment should use HTTPS.

**Backup:** A recoverable copy of data. RDS automated backups can support point-in-time recovery, subject to retention settings.

**Snapshot:** A point-in-time copy of data, such as an RDS database or EBS volume. Snapshots may remain after the original resource is deleted and can continue to incur charges.

**Availability:** The ability of a service to remain accessible. Multiple AZs can support availability, but two subnets alone do not make a single EC2 instance highly available.

**Scalability:** The ability to handle changes in workload by adding or changing resources. This workshop uses one EC2 instance; it is not an autoscaling or highly available architecture.

**Billing and budget:** AWS charges depend on resource type, Region, usage and current pricing. A budget can alert an account owner when spending reaches a threshold. It is not a hard spending cap and does not automatically stop resources.

**Cleanup:** Terminating EC2 does not automatically delete separate RDS databases, S3 buckets, snapshots, EBS volumes, IAM resources or other services. Review each service independently.

## 10. How a request moves through the system

### A. A user opens the home page

1. The browser sends an HTTP request to the EC2 public IP on port 80.
2. The Internet Gateway routes it into the VPC's public subnet.
3. The EC2 security group permits the HTTP request.
4. Nginx receives it and forwards it to Gunicorn on `127.0.0.1:8000`.
5. Gunicorn runs Flask.
6. Flask queries RDS over the VPC's private network on port 3306.
7. The response returns through Gunicorn and Nginx to the browser.

### B. A user publishes an idea with an image

1. The browser submits the form and image to Flask.
2. Flask validates the submitted fields and image.
3. Boto3 uses temporary credentials from the EC2 role to upload the image to S3 under `images/`.
4. S3 stores the image object.
5. Flask stores the idea details and S3 object key in RDS.
6. When the idea page is displayed, Flask generates a presigned URL.
7. The browser uses that URL to retrieve the private S3 object.

The database stores the S3 key, not the presigned URL. The URL is temporary; the object persists until deleted.

### C. EC2 connects to RDS

1. Flask uses the RDS endpoint hostname and MySQL port 3306.
2. VPC routing sends traffic to the RDS private address.
3. The RDS security group checks whether the source is the permitted EC2 security group.
4. MySQL checks the database credentials and privileges.

These are separate checks: the network rule permits the connection; MySQL authentication authorizes the database user.

## 11. Common confusions

| Confusion | Correct understanding |
|---|---|
| A public subnet makes every resource public. | No. It needs an internet route; the resource also needs public addressing and permissive security rules. |
| A private subnet cannot communicate with anything. | It can communicate within the VPC and with permitted services. It has no direct internet route in this design. |
| S3 is inside the VPC. | No. S3 is a regional AWS service accessed through its API. |
| The PEM file is an AWS access key. | No. It is an SSH private key for administrator access to EC2. |
| The EC2 role is the same as my CLI profile. | No. A local profile configures CLI access on your computer. The EC2 role supplies temporary credentials to software on EC2. |
| An IAM policy opens a network connection. | No. IAM controls AWS API permissions. Routes and security groups control network traffic. |
| RDS should allow the EC2 public IP. | Prefer the EC2 security group as the source of the RDS rule. |
| A presigned URL expiring deletes the image. | No. Only the URL expires. The S3 object remains until deleted. |
| The RDS endpoint is a browser URL. | No. It is a database hostname used by MySQL clients and applications. |
| An S3 object key is a filesystem path. | No. It is the object's name. Slashes make it appear folder-like in the Console. |
| If AWS CLI works on my laptop, it works on EC2. | Not necessarily. Credentials, roles, profiles and network paths may differ. |
| Two private subnets make the application highly available. | No. They satisfy the RDS subnet-group placement requirement. One EC2 instance remains a single point of failure. |
| A budget alert prevents overspending. | No. It sends a notification; it does not cap spending or stop resources. |

## 12. Quick reference: which mechanism does what?

| Need | Mechanism |
|---|---|
| Isolate the application's network | VPC |
| Divide the network into address ranges | Subnets |
| Decide where network traffic goes | Route tables |
| Connect a VPC to the internet | Internet Gateway |
| Permit or block traffic to an instance/database | Security groups |
| Control AWS API permissions | IAM policies and roles |
| Give EC2 software AWS credentials without stored permanent keys | EC2 IAM role |
| Log in to Ubuntu as administrator | SSH and PEM private key |
| Host the application | EC2 |
| Give users an address to reach it | Public IP, public DNS or domain |
| Keep a stable public IPv4 address | Elastic IP |
| Encrypt browser traffic | HTTPS and TLS certificate |
| Store structured ideas and comments | RDS MySQL |
| Store uploaded image files | S3 |
| Let a browser temporarily read a private image | Presigned URL |
| Call AWS services from Python | Boto3 |
| Route public web traffic to Flask | Nginx and Gunicorn |

## 13. The mental model

Think about the deployment through four separate questions:

1. **Where does it run?** EC2 runs the application. RDS runs the database service. S3 stores objects.
2. **How does traffic reach it?** VPCs, subnets, route tables, Internet Gateways, IP addresses and security groups determine network reachability.
3. **What is it allowed to do?** IAM roles and policies determine AWS API permissions. Database credentials separately determine what the application can do inside MySQL.
4. **Where does the data live?** Ideas and comments live in RDS. Image files live in S3. EC2's disk holds the operating system and application runtime, not the authoritative application data.

Network access, AWS permissions, database authentication and data storage are related, but they are not interchangeable.
