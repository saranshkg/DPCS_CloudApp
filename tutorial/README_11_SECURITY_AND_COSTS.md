# 11. Security and Costs

This section reviews the security boundaries and AWS charges created by the deployment. Complete it before leaving resources running.

## 11.1 Security groups

Security groups should implement the minimum network access required.

| Resource | Inbound access | Do not allow |
|---|---|---|
| EC2 | TCP 22 from your IP; TCP 80 from users | SSH from `0.0.0.0/0` |
| RDS | TCP 3306 from `campusboard-ec2-sg` | MySQL from the public internet |
| S3 | No public access required | Public read or write access |

RDS should have **Public access: No**. The RDS security group should refer to the EC2 security group as its source.

## 11.2 IAM permissions

The EC2 application should use an IAM instance role.

- Attach only the S3 permissions required by the application.
- Restrict object permissions to the bucket's `images/` prefix.
- Do not store long-term AWS access keys in `.env`, source code or Git.
- Do not use the AWS account root user for application access.
- Do not attach broad administrator policies to the EC2 role.

The IAM policy in Section 8 is intended for this application. Remove actions the application does not use.

## 11.3 Application secrets

Keep these values out of source control:
- Flask `SECRET_KEY`.
- RDS application password.
- Any AWS credentials, if they are used for a separate administrative task.

Check that `.env` is ignored by Git:

    git check-ignore .env

If the command prints `.env`, Git is ignoring the file. If it prints nothing, add `.env` to `.gitignore`:

    echo ".env" >> .gitignore

Check whether a secret was accidentally committed:

    git status --short
    git ls-files .env

If `.env` was committed, removing it from the latest working tree is not enough. Remove it from Git tracking and rotate any credentials that were exposed.

## 11.4 SSH access

- Restrict inbound TCP 22 to the administrator's current public IP.
- Do not share private key files.
- Do not paste private keys or passwords into chat, tickets or source code.
- Remove or update the SSH rule when the administrator's IP changes.
- Use a managed access method such as AWS Systems Manager Session Manager for a longer-lived deployment, if configured.

## 11.5 HTTP and HTTPS

The workshop deployment uses HTTP on port 80 to keep the initial setup small. HTTP traffic is not encrypted.

For a real public deployment:
- Register or use a domain name.
- Configure HTTPS with a valid TLS certificate.
- Redirect HTTP to HTTPS.
- Keep the certificate renewal process operational.
- Consider AWS Certificate Manager with an Application Load Balancer, or a suitable Nginx certificate setup.

Do not collect passwords or sensitive personal information over the workshop's HTTP deployment.

## 11.6 Application-level limitations

The Campus Ideas Board does not implement authentication. Contributors type their names.

Consequences:
- A user can enter another person's name.
- There is no reliable user identity or ownership check.
- There is no account recovery or access control.
- Names and comments should be treated as user-supplied content.

For a public deployment, add authentication, input validation, moderation and abuse controls before treating contributor names as identities.

Also review:
- Maximum image upload size.
- Allowed image file types.
- Escaping of user-generated text in templates.
- Rate limiting or spam controls.
- Error handling that does not expose stack traces to visitors.

## 11.7 S3 access and presigned URLs

Keep the bucket private. The application generates presigned URLs to let browsers retrieve individual objects for a limited time.

A presigned URL:
- Grants temporary access to the specified object.
- Expires after the configured duration.
- Does not delete the object when it expires.
- Should not be posted publicly or stored in application logs.

The application should generate a fresh URL when a page is rendered or when an image is requested, rather than storing an expired URL in the database. Store the object key in RDS.

## 11.8 Cost sources

AWS pricing varies by Region, resource configuration, usage and account eligibility. Check the current Mumbai Region prices before launching resources.

| Resource | What can incur charges |
|---|---|
| EC2 | Instance running time, EBS storage, public IPv4 address and data transfer |
| RDS | DB instance running time, allocated storage, backups and data transfer |
| S3 | Stored object volume, requests and data transfer |
| NAT Gateway | Hourly charge and data processing, if created |
| CloudWatch | Log ingestion, retention and metrics beyond included allowances |
| Data transfer | Internet egress and some cross-AZ or cross-Region traffic |

A small instance or free-tier label does not mean every associated resource is free. Eligibility and free-tier terms depend on the account and current AWS offer.

## 11.9 Cost controls

Before deployment:
1. Open **Billing and Cost Management**.
2. Review the account's free-tier eligibility and current usage.
3. Create a budget with an email alert at a low amount suitable for the exercise.
4. Review the EC2, RDS and S3 resources after the workshop.
5. Avoid creating a NAT Gateway for this architecture unless there is a specific need.

A budget alert is a notification, not a hard spending cap. It does not automatically stop resources.

## 11.10 Security and cost checkpoint

- [ ] RDS is private and not publicly accessible.
- [ ] Port 3306 is allowed only from the EC2 security group.
- [ ] SSH is restricted to the administrator's IP.
- [ ] S3 Block Public Access is enabled.
- [ ] EC2 uses an IAM role with limited S3 permissions.
- [ ] `.env` is not committed to Git.
- [ ] No long-term AWS keys are stored on EC2.
- [ ] A budget alert is configured.
- [ ] The team knows which resources must be deleted after the exercise.
