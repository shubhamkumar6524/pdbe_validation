import boto3
from botocore.client import BaseClient
from loguru import logger

class S3ClientWrapper:

    def __init__(self, client) -> None:
        self.s3_client: BaseClient = client

    def upload_file_from_s3(self, bucket_name, file_key, file_object):
        try:
            logger.info(
                f"Uploading file to S3. Bucket: '{bucket_name}', file_key: '{file_key}',"
            )
            result = self.s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=file_object
            )
            logger.info(
                f"Uploading successful. Bucket: '{bucket_name}', file_key: '{file_key}',"
            )
            return result
        except Exception as e:
            raise Exception(
                f"Error while uploading file. Bucket: {bucket_name}, file: {file_key}, Reason: {str(e)}"
                ) from e
        

    def download_file_from_s3(self, bucket_name, file_key):
        try:
            logger.info(
                f"Downloading file from S3. Bucket: '{bucket_name}', file_key: '{file_key}',"
            )
            result = self.s3_client.get_object(Bucket=bucket_name, Key=file_key)
            logger.info(
                f"Download successful. Bucket: '{bucket_name}', file_key: '{file_key}',"
            )
            return result
        except Exception as e:
            raise Exception(
                f"Error while downloading file. Bucket: {bucket_name}, file: {file_key}, Reason: {str(e)}"
                ) from e
            
s3_client_wrapper = S3ClientWrapper(boto3.client("s3"))