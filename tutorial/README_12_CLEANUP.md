# 12. Cleanup: Remove AWS Resources Safely

AWS resources can continue to incur charges after the application is no longer being used. Follow this order to remove the deployment.

**Warning:** This procedure permanently deletes the deployed database and uploaded images if you choose to delete them. Export anything you need before continuing.

## 12.1 Record anything you need to keep

Before deleting resources:
- Export database records if they are required.
- Download any S3 images that need to be retained.
- Save application logs or screenshots needed for assessment.
- Record the final architecture and resource configuration if required.

Do not proceed until the required data has been saved outside the AWS resources being deleted.

## 12.2 Stop the application

Connect to EC2:

    ssh -i campusboard-key.pem ubuntu@EC2_PUBLIC_IP

Stop and disable the application service:

    sudo systemctl stop campusboard
    sudo systemctl disable campusboard

Stop Nginx:

    sudo systemctl stop nginx
    sudo systemctl disable nginx

Exit SSH.

## 12.3 Delete the RDS database

1. Open **RDS → Databases**.
2. Select `campusboard-db`.
3. Choose **Actions → Delete**.
4. If you need a final backup, create one before deletion.
5. Review the deletion options carefully.
6. Confirm deletion.

Automated backups and manual snapshots may remain after the DB instance is deleted and can continue to incur storage charges. Review and delete snapshots that are no longer needed.

Wait until the database is fully deleted before removing its subnet group or security group.

## 12.4 Empty and delete the S3 bucket

S3 buckets cannot be deleted while they contain objects.

If the images are no longer needed:

1. Open **S3 → Buckets → dpcs-campusboard-1**.
2. Review the contents of the bucket.
3. Select the objects and delete them.
4. If bucket versioning was enabled, delete object versions and delete markers as well.
5. Delete the empty bucket.

If the bucket is shared with another project or contains files that must be retained, do not delete it. Remove only the objects belonging to this application, or leave the bucket in place.

## 12.5 Terminate the EC2 instance

1. Open **EC2 → Instances**.
2. Select `campusboard-app`.
3. Choose **Instance state → Terminate instance**.
4. Confirm termination.

Check the attached EBS volumes. The root volume is normally deleted on termination when its delete-on-termination setting is enabled. Delete any detached volumes that are no longer required.

Release any Elastic IP address that was allocated but is no longer in use. An automatically assigned public IPv4 address is released when the instance is terminated.

## 12.6 Remove IAM resources

After the EC2 instance is terminated:

1. Open **IAM → Roles**.
2. Delete `campusboard-ec2-role`.
3. Open **IAM → Policies**.
4. Delete `CampusBoardS3ImagesPolicy`, if no other role uses it.

AWS will prevent deletion of a customer-managed policy while it remains attached to a role. Detach it or delete the role first.

Do not delete IAM users, roles or policies that belong to other projects or account administration.

## 12.7 Remove network resources

After EC2 and RDS are deleted:

1. Delete `campusboard-rds-sg` if no resource uses it.
2. Delete `campusboard-ec2-sg` if no resource uses it.
3. Delete `campusboard-db-subnet-group` in the RDS Console.
4. Disassociate and delete the custom route tables, if they are no longer needed.
5. Detach `campusboard-igw` from `campusboard-vpc`, then delete the Internet Gateway.
6. Delete the three subnets.
7. Delete `campusboard-vpc`.

AWS will block deletion of a VPC while dependent resources or network interfaces remain. Inspect the error message and remove the remaining dependency rather than repeatedly retrying.

Do not delete the default VPC or shared network resources.

## 12.8 Review billing

Open **Billing and Cost Management** and review:
- EC2 instances and EBS volumes.
- RDS instances, backups and snapshots.
- S3 storage and requests.
- Elastic IP addresses or public IPv4 charges.
- NAT Gateways, if any were created.
- CloudWatch log groups.
- Data transfer.

Billing data may take time to reflect resource deletion. Check again after the next billing update.

## 12.9 Cleanup checklist

- [ ] Required database data has been exported.
- [ ] Required S3 images have been downloaded.
- [ ] Flask and Nginx services have been stopped.
- [ ] RDS instance has been deleted.
- [ ] Unneeded RDS snapshots and backups have been deleted.
- [ ] S3 bucket has been emptied and deleted, if appropriate.
- [ ] EC2 instance has been terminated.
- [ ] Unused EBS volumes and Elastic IPs have been removed.
- [ ] Unused IAM role and policy have been deleted.
- [ ] Unused security groups and network resources have been deleted.
- [ ] Billing has been reviewed.

## 12.10 Final reminder

Deleting the EC2 instance does not automatically delete the RDS database, S3 bucket, snapshots, detached EBS volumes or other separately billed resources. Review each service independently.
