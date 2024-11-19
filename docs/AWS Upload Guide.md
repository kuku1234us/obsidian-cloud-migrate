# Step-by-Step Instructions for Uploading Files to AWS S3 with Python

## Step 1: Set Up AWS Credentials

To upload to an AWS S3 bucket, you'll need to have access credentials. Follow these steps to set up your credentials:

### 1.1 Create an IAM User

1. Go to the AWS Management Console: [https://aws.amazon.com/](https://aws.amazon.com/).
2. Navigate to the **IAM** (Identity and Access Management) service.
3. Click **Users** > **Add User**.
4. Provide a **User name** (e.g., `s3-upload-user`).
5. Select **Programmatic access** for access type.
6. Click **Next** and attach the policy **AmazonS3FullAccess** to provide necessary permissions.
7. Complete the setup and make sure to save the **Access Key ID** and **Secret Access Key** provided. You'll use these credentials to connect with your S3 bucket.

### 1.2 Install the AWS CLI (Optional)

If you haven't done so, install the AWS CLI to configure your credentials:

```bash
pip install awscli
```

Then, configure your credentials using the command:

```bash
aws configure
```

You will be prompted for your **Access Key ID**, **Secret Access Key**, **region**, and output format. You can leave the output format as `json` or blank.

## Step 2: Set Up Python Environment

You'll need the AWS SDK for Python (`boto3`) to interact with your S3 bucket.

### 2.1 Install boto3

Install the required library:

```bash
pip install boto3
```

## Step 3: Write the Python Code to Upload Files to S3

Below is a simple Python program that will upload a file to your S3 bucket:

```python
import boto3
from botocore.exceptions import NoCredentialsError

# AWS Credentials (replace with your Access Key and Secret Key)
aws_access_key = "<Your_Access_Key_ID>"
aws_secret_key = "<Your_Secret_Access_Key>"

# S3 bucket name and file to upload
bucket_name = "<Your_S3_Bucket_Name>"
file_to_upload = "local-file.txt"  # Path to your local file
s3_object_name = "uploaded-file.txt"  # Name to be used for the file in S3

# Create an S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)

# Upload the file to S3
try:
    s3.upload_file(file_to_upload, bucket_name, s3_object_name)
    print(f"File '{file_to_upload}' uploaded successfully to S3 bucket '{bucket_name}' as '{s3_object_name}'")
except FileNotFoundError:
    print("The file was not found.")
except NoCredentialsError:
    print("Credentials not available.")
```

### Explanation of Code:

- **aws_access_key** and **aws_secret_key**: Use the credentials obtained when setting up your IAM user.
- **bucket_name**: The name of your S3 bucket.
- **file_to_upload**: The local file you want to upload.
- **s3_object_name**: The name to use for the uploaded file in the S3 bucket.
- The `boto3.client` is used to create an S3 client, and the `upload_file` method uploads the file.

## Step 4: Get the S3 File URL

Once your file is uploaded to S3, you can generate the URL to access it.

- By default, S3 bucket objects are **private**. You need to make them public to generate a public URL.

### 4.1 Make the File Public

1. Navigate to your **S3 bucket** in the AWS Console.
2. Locate the uploaded file.
3. Click on the **Permissions** tab and select **Make public**.

### 4.2 Construct the File URL

The URL format for accessing the file in an S3 bucket is:

```
https://<bucket_name>.s3.<region>.amazonaws.com/<s3_object_name>
```

For example, if you upload `uploaded-file.txt` to a bucket named `my-bucket` in the `us-west-2` region, the URL would be:

```
https://my-bucket.s3.us-west-2.amazonaws.com/uploaded-file.txt
```

## Summary

- **Set up AWS credentials** using IAM.
- **Install `boto3`** to interact with S3 from Python.
- Write a simple script to **upload your file**.
- Make your file **public** to get a shareable URL.

This basic setup allows you to programmatically upload files to AWS S3, which is the first step towards automating your media file migration with your Python tool.
