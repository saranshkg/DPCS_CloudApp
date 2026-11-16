# Campus Ideas Board: Cloud Deployment Workshop

A small Flask application deployed on AWS to learn how web hosting, networking, databases and object storage fit together.

## What we are building

```text
Browser
   |
   | Public IP / DNS, HTTP
   v
EC2 (Ubuntu)
Nginx -> Gunicorn (WSGI) -> Flask
   |                 |
   |                 +------> S3 (uploaded images)
   |
   +------------------------> RDS MySQL (ideas and comments)
```

## Restaurant analogy
```
Customer
   |
   | Visits restaurant, places order
   v
Restaurant
Kitchen server -> Head chef -> Cooking team
   |                 |
   |                 +------> Pantry (ingredients and supplies)
   |
   +------------------------> Order register (orders and customer details)
```

The application is developed and tested locally first, then hosted on EC2. RDS stores structured data; S3 stores images.

## Guide map

| Guide | What it covers |
|---|---|
| 01. Prerequisites | Python, Git, MySQL, AWS CLI and required accounts/tools |
| 02. Local MySQL setup | Install MySQL, start the service, create the database and user |
| 03. Application setup | Flask project structure, application code and dependencies |
| 04. Local testing | Run the app and test ideas, comments and image uploads locally |
| 05. AWS fundamentals | Regions, VPC, subnets, route tables, Internet Gateway and security groups |
| 06. EC2 deployment | Launch Ubuntu, public IP, SSH/PEM, Gunicorn and Nginx |
| 07. RDS MySQL | DB subnet group, managed database, credentials and security groups |
| 08. S3 and IAM role | Private bucket access from EC2 using an IAM instance role |
| 09. Integration | Connect the deployed application to RDS and S3 |
| 10. Verification | Test the live application and confirm data persistence |
| 11. Security and costs | IAM, secrets, network access, billing and budgets |
| 12. Cleanup | Safely remove AWS resources after the workshop |

## Reference guides

- `AWS_DEPLOYMENT_GLOSSARY_REVISED.md`: hosting, public IPs, DNS, domains, VPCs, subnets, IAM, PEM keys, EC2, RDS, S3, ports, request flow and common confusions.
- `MYSQL_CHEATSHEET.md`: quick reference for MySQL commands, database and user setup, connecting, inspecting tables and basic queries.

## Learning path

```text
LOCAL DEVELOPMENT
      |
      v
Prerequisites -> Local MySQL -> Flask application
      |
      v
Local end-to-end testing
      |
      v
AWS NETWORK FOUNDATION
Region -> VPC -> Subnets -> Routes -> Internet Gateway
      |
      v
HOST THE APPLICATION
EC2 -> Public IP -> SSH/PEM -> Gunicorn -> Nginx
      |
      v
CONNECT MANAGED SERVICES
RDS MySQL <--- EC2 ---> S3
                  |
             IAM instance role
      |
      v
INTEGRATE AND VERIFY
Database connection -> Image upload/retrieval -> Browser tests
      |
      v
SECURITY, COSTS AND CLEANUP
```

## Final architecture

```text
                         USERS
                           |
                    Public IP / DNS
                           |
                         HTTP
                           |
                    Internet Gateway
                           |
                 VPC: campusboard-vpc
                           |
                 Public subnet: EC2
                  Nginx -> Gunicorn
                           |
                 Flask application
                    /           \
                   /             \
             RDS MySQL           S3 bucket
          ideas and comments   uploaded images
              private          private objects
```

The numbered guides walk through the hands-on work. The glossary explains the concepts behind the architecture. The MySQL cheatsheet is a quick command reference.

Additional Reference:
    1. https://aws.plainenglish.io/ec2-s3-and-rds-explained-simply-the-only-aws-services-beginners-need-first-acd8f7abf655
    2. https://builder.aws.com/content/3J4yG8bIskkSxO1bkTXakLI7u2t/ec2-s3-and-rds-explained-like-youre-renting-an-apartment
    3. https://www.geeksforgeeks.org/cloud-computing/top-aws-services/
    4. https://www.geeksforgeeks.org/devops/aws-tutorial/