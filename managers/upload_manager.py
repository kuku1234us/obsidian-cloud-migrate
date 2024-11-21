import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from managers.config_manager import ConfigManager
from utils.logger import Logger


class UploadManager:
    def __init__(self):
        """Initialize UploadManager with configuration and logging"""
        self.config_manager = ConfigManager()
        self.logger = Logger()
        self._s3_client = None
        self._bucket_name = None
        self._subfolder = None

    @property
    def s3_client(self):
        """Lazy initialization of S3 client"""
        if self._s3_client is None:
            aws_access_key = self.config_manager.get("aws_access_key_id")
            aws_secret_key = self.config_manager.get("aws_secret_access_key")
            aws_region = self.config_manager.get("aws_region")
            
            self._s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
        return self._s3_client

    @property
    def bucket_name(self):
        """Get S3 bucket name from config"""
        if self._bucket_name is None:
            self._bucket_name = self.config_manager.get("s3_bucket_name")
        return self._bucket_name

    @property
    def subfolder(self):
        """Get S3 subfolder from config"""
        if self._subfolder is None:
            self._subfolder = self.config_manager.get("s3_subfolder", "obsidian_attachments/").strip('/')
        return self._subfolder

    def upload_file(self, file_path, object_name=None):
        """
        Upload a file to S3 bucket in the configured subfolder
        
        Args:
            file_path (str): Local path to the file to upload
            object_name (str, optional): S3 object name. If not specified, file_path's basename is used
            
        Returns:
            tuple: (bool, str) - (Success status, Message or error description)
        """
        try:
            # Use file basename if object_name not provided
            if object_name is None:
                object_name = os.path.basename(file_path)

            # Construct the full S3 key with subfolder
            s3_key = f"{self.subfolder}/{object_name}"

            # Upload the file
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            
            success_msg = f"Successfully uploaded '{file_path}' to S3 bucket '{self.bucket_name}' as '{s3_key}'"
            self.logger.info(success_msg)
            return True, success_msg

        except FileNotFoundError as e:
            error_msg = f"File not found: {file_path}"
            self.logger.error(error_msg)
            return False, error_msg
        except NoCredentialsError as e:
            error_msg = "AWS credentials not found or invalid"
            self.logger.error(error_msg)
            return False, error_msg
        except ClientError as e:
            error_msg = f"AWS S3 error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error during upload: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def upload_file_with_progress(self, file_path, object_name=None, progress_callback=None):
        """
        Upload a file to S3 bucket with progress tracking
        
        Args:
            file_path (str): Local path to the file to upload
            object_name (str, optional): S3 object name. If not specified, file_path's basename is used
            progress_callback (callable, optional): Function to call with bytes uploaded
            
        Returns:
            tuple: (bool, str) - (Success status, Message or error description)
        """
        try:
            # Use file basename if object_name not provided
            if object_name is None:
                object_name = os.path.basename(file_path)

            # Construct the full S3 key with subfolder
            s3_key = f"{self.subfolder}/{object_name}"
            
            # Get file size for progress tracking
            file_size = os.path.getsize(file_path)
            
            # Create a callback class for tracking upload progress
            class ProgressCallback:
                def __init__(self, callback):
                    self._callback = callback
                    self._bytes_uploaded = 0
                
                def __call__(self, bytes_amount):
                    self._bytes_uploaded += bytes_amount
                    if self._callback:
                        self._callback(self._bytes_uploaded)
            
            # Create progress callback if needed
            callback = ProgressCallback(progress_callback) if progress_callback else None
            
            # Upload the file with progress tracking
            self.s3_client.upload_file(
                file_path, 
                self.bucket_name, 
                s3_key,
                Callback=callback
            )
            
            success_msg = f"Successfully uploaded '{file_path}' to S3 bucket '{self.bucket_name}' as '{s3_key}'"
            self.logger.info(success_msg)
            return True, success_msg

        except FileNotFoundError as e:
            error_msg = f"File not found: {file_path}"
            self.logger.error(error_msg)
            return False, error_msg
        except NoCredentialsError as e:
            error_msg = "AWS credentials not found or invalid"
            self.logger.error(error_msg)
            return False, error_msg
        except ClientError as e:
            error_msg = f"AWS S3 error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error during upload: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def upload_files(self, file_paths, object_names=None):
        """
        Upload multiple files to S3 bucket
        
        Args:
            file_paths (list): List of local file paths to upload
            object_names (list, optional): List of S3 object names. If not specified, file basenames are used
            
        Returns:
            dict: Dictionary mapping file paths to (success, message) tuples
        """
        results = {}
        
        if object_names is None:
            object_names = [None] * len(file_paths)
        
        for file_path, object_name in zip(file_paths, object_names):
            results[file_path] = self.upload_file(file_path, object_name)
        
        return results

    def get_cloudfront_url(self, object_name):
        """
        Get the CloudFront URL for an uploaded object
        
        Args:
            object_name (str): The name of the uploaded object
            
        Returns:
            str: The complete CloudFront URL for the object
        """
        # Get CloudFront base URL from config
        cloudfront_base_url = self.config_manager.get("cloudfront_base_url")
        if not cloudfront_base_url:
            raise ValueError("CloudFront base URL not configured")
        
        # Ensure base URL ends with '/' and object name doesn't start with '/'
        cloudfront_base_url = cloudfront_base_url.rstrip('/') + '/'
        object_name = object_name.lstrip('/')
        
        # Combine CloudFront base URL with subfolder and object name
        if self.subfolder:
            return f"{cloudfront_base_url}{self.subfolder}/{object_name}"
        return f"{cloudfront_base_url}{object_name}"
