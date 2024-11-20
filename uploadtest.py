import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from managers.config_manager import ConfigManager


def upload_file_to_s3(file_name, bucket_name, object_name=None):
    # Initialize ConfigManager to load configuration
    config_manager = ConfigManager()
    config_manager.load_config()

    # Retrieve AWS credentials and region from configuration
    aws_access_key = config_manager.get("aws_access_key_id")
    aws_secret_key = config_manager.get("aws_secret_access_key")
    aws_region = config_manager.get("aws_region")

    # Create an S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )

    # Upload the file to a subfolder 'obsidian_attachments'
    if object_name is None:
        object_name = file_name.split("\\")[-1]  # Extract the filename for object_name
    object_name = f"obsidian_attachments/{object_name}"  # Add subfolder to the object name

    try:
        s3.upload_file(file_name, bucket_name, object_name)
        print(f"File '{file_name}' uploaded successfully to S3 bucket '{bucket_name}' in subfolder 'obsidian_attachments' as '{object_name}'")
    except FileNotFoundError:
        print("The file was not found.")
    except NoCredentialsError:
        print("Credentials not available.")
    except ClientError as e:
        print(f"Failed to upload file: {e}")


if __name__ == "__main__":
    # Specify the file to upload and the S3 bucket name
    file_to_upload = "D:\\projects\\obsidiancloudmigrate\\assets\\appicon.png"
    bucket_name = "gbacbucket"  # Replace with your bucket name

    # Upload the file to S3
    upload_file_to_s3(file_to_upload, bucket_name)
