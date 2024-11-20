# How to Get AWS Credentials (Access Keys)

This document provides step-by-step instructions to obtain the **Access Key ID** and **Secret Access Key** required to connect your Python application to AWS services like S3.

## Step 1: Log in to AWS Management Console

1. Go to the [AWS Management Console](https://aws.amazon.com/).
2. Log in with your AWS account credentials.

## Step 2: Navigate to IAM (Identity and Access Management)

1. In the **Services** menu, search for and select **IAM**.
2. IAM is where you manage access to AWS services and set up security credentials for users and applications.

## Step 3: Create an IAM User

1. Click on **Users** in the left sidebar.
2. Click the **Add users** button.
3. Enter a **User name** (e.g., `obsidiancloud-user`).
4. Under **Select AWS credential type**, check the box for **Programmatic access**. This will allow the user to generate an access key.

## Step 4: Set Permissions

1. Choose **Attach policies directly** to assign permissions to the user.
2. Search for and select the **AmazonS3FullAccess** policy to provide full access to S3. This allows the application to upload and retrieve files.
3. You can also create a custom policy if you want more granular control over access.

## Step 5: Review and Create User

1. Click **Next: Tags**. Tags are optional, so you can skip this step.
2. Click **Next: Review** to review the settings.
3. Click **Create user**.

## Step 6: Download Access Keys

1. After creating the user, you will see the **Access Key ID** and **Secret Access Key**.
2. Click on **Download .csv** to save the keys to your computer. Alternatively, you can copy and paste them to a secure location.

**Important**: The **Secret Access Key** will not be displayed again, so make sure to download or save it securely.

## Step 7: Secure Your Credentials

- Store the credentials in a secure file (e.g., `.env`) or use a secure credential manager.
- Do **not** hard-code the credentials in your Python code.

### Example `.env` File

You can store your credentials in an `.env` file to easily load them into your Python script:

```
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=your_aws_region
```

### Step 8: Using Credentials in Your Python Application

To load credentials from the `.env` file, you can use the `python-dotenv` library:

```python
import os
from dotenv import load_dotenv
import boto3

# Load environment variables
load_dotenv()

aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region = os.getenv("AWS_REGION")

# Create an S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=region
)
```

## Summary

- Log in to the AWS Management Console and create a new **IAM user** with programmatic access.
- Attach the **AmazonS3FullAccess** policy to give the user permissions for S3.
- Save the **Access Key ID** and **Secret Access Key** securely.
- Use the credentials in your Python application to connect to AWS services securely.

This setup ensures that your Python tool can upload files to S3 while keeping your credentials secure.
