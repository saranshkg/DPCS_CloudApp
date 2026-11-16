# 5. AWS Fundamentals: Regions, VPCs, Subnets and Routing

This section prepares the network in which the application and database will run. The target architecture is:

- Flask application on an Ubuntu EC2 instance in a public subnet.
- MySQL on Amazon RDS in private subnets.
- Images in a private S3 bucket. S3 is an AWS service outside the VPC, not a resource placed inside a subnet.
- EC2 reaches RDS over the VPC's private network and reaches S3 through the AWS API.

Do not launch the EC2 instance or create the RDS database until the network design is clear.

## 5.1 AWS region

An AWS Region is a geographic area containing multiple Availability Zones (AZs). Resources such as EC2 instances, RDS databases and S3 buckets have region-specific configuration.

For this workshop, use **Asia Pacific (Mumbai), `ap-south-1`** for EC2 and RDS. The S3 bucket used during local testing is also in `ap-south-1`.

Keep the same region selected in the AWS Console throughout the deployment. A region mismatch can cause endpoint and connectivity errors.

## 5.2 Virtual Private Cloud

A VPC is an isolated virtual network in an AWS Region. EC2 and RDS instances are attached to subnets in a VPC.

Create one VPC for the application.

Suggested configuration:

| Setting | Value |
|---|---|
| Name | `campusboard-vpc` |
| IPv4 CIDR | `10.0.0.0/16` |
| IPv6 CIDR | No IPv6 for this exercise |
| Tenancy | Default |

The CIDR block defines the private IP address range available inside the VPC.

## 5.3 Subnets

A subnet is a range of IP addresses inside a VPC. A subnet belongs to one Availability Zone.

Create three subnets:

| Name | AZ | IPv4 CIDR | Purpose |
|---|---|---|---|
| `campusboard-public-a` | `ap-south-1a` | `10.0.1.0/24` | EC2 application server |
| `campusboard-private-a` | `ap-south-1a` | `10.0.11.0/24` | RDS |
| `campusboard-private-b` | `ap-south-1b` | `10.0.12.0/24` | RDS subnet group |

Use the actual AZ names available in your account if these names are unavailable. The two private subnets must be in different AZs because an RDS DB subnet group requires subnets in at least two AZs.

Enable **Auto-assign public IPv4 address** for the public subnet. Do not enable it for the private subnets.

A public subnet is not public merely because of its name. Its route table must provide a route to an Internet Gateway.

## 5.4 Internet Gateway

An Internet Gateway (IGW) allows resources in a VPC to communicate with the internet when their subnet routes and security rules permit it.

1. Open **VPC → Internet gateways**.
2. Create an Internet Gateway named `campusboard-igw`.
3. Attach it to `campusboard-vpc`.

An IGW does not automatically make every subnet public. The subnet's route table determines whether internet-bound traffic is routed through it.

## 5.5 Route tables

A route table determines where network traffic from a subnet is sent.

**Create the public route table:**

1. Go to **VPC → Route tables → Create route table**.
2. Name: `campusboard-public-rt`.
3. Select VPC: `campusboard-vpc`.
4. Click **Create route table**.
5. Select the new route table and open **Routes → Edit routes → Add route**.
6. Add the following routes:

| Destination | Target |
|---|---|
| `10.0.0.0/16` | `local` |
| `0.0.0.0/0` | `campusboard-igw` |

7. Save changes.
8. Open **Subnet associations → Edit subnet associations**.
9. Select `campusboard-public-a` (`10.0.1.0/24`).
10. Save associations.

**Create the private route table:**

1. Go to **VPC → Route tables → Create route table**.
2. Name: `campusboard-private-rt`.
3. Select VPC: `campusboard-vpc`.
4. Click **Create route table**.
5. Select the new route table and open **Routes**.
6. Verify that it contains only the local VPC route:

| Destination | Target |
|---|---|
| `10.0.0.0/16` | `local` |

7. Open **Subnet associations → Edit subnet associations**.
8. Select both `campusboard-private-a` (`10.0.11.0/24`) and `campusboard-private-b` (`10.0.12.0/24`).
9. Save associations.

The RDS database does not need to initiate connections to the public internet. Do not add an Internet Gateway route to the private route table. A NAT Gateway is not required for this architecture.

## 5.6 Security groups

A security group is a stateful virtual firewall attached to an AWS resource. It controls inbound and outbound traffic.

Route tables and security groups serve completely different functions in cloud networking (such as in AWS or Azure): route tables direct where traffic goes (like a GPS), while security groups decide who is allowed in or out (like a firewall).

Create two security groups in `campusboard-vpc`.

### EC2 security group: `campusboard-ec2-sg`

Inbound rules:

| Type | Protocol | Port | Source | Purpose |
|---|---|---:|---|---|
| SSH | TCP | 22 | Your current public IP `/32` | Administrative SSH access |
| HTTP | TCP | 80 | `0.0.0.0/0` | Public web traffic |

Do not use `0.0.0.0/0` as the SSH source. If your public IP changes, update the SSH rule.

Outbound: retain the default allow-all rule for this workshop. The instance needs outbound access for package installation and AWS API calls.

### RDS security group: `campusboard-rds-sg`

Inbound rule:

| Type | Protocol | Port | Source | Purpose |
|---|---|---:|---|---|
| MySQL/Aurora | TCP | 3306 | `campusboard-ec2-sg` | Allow only the application server to connect |

Select the EC2 security group as the source. Do not enter the EC2 public IP or allow port 3306 from `0.0.0.0/0`.

Outbound: retain the default rule.

## 5.7 Verify the network before continuing

Check all of the following in the VPC Console:

- `campusboard-vpc` exists with CIDR `10.0.0.0/16`.
- The public subnet is in one AZ and the two private subnets are in different AZs.
- The public route table has `0.0.0.0/0` routed to the Internet Gateway.
- The private route table has no Internet Gateway route.
- The EC2 security group allows SSH only from your IP and HTTP on port 80.
- The RDS security group allows TCP 3306 only from the EC2 security group.

## 5.8 Architecture to keep in mind

```text
Internet
   |
Internet Gateway
   |
Public subnet: 10.0.1.0/24
   |
EC2: Flask + Gunicorn + Nginx
   |
   +---- Private VPC connection ----> RDS MySQL
   |
   +---- AWS API -------------------> S3 bucket
```

S3 is not inside `campusboard-vpc`. The EC2 instance accesses it using AWS credentials supplied through an IAM role.

Proceed to Section 6 only after the VPC, subnets, route tables, Internet Gateway and security groups are in place.
