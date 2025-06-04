import os
import re
from app.config import settings
from app.shared.s3 import s3_client_wrapper

SEPARATOR = "/"

class S3Utils:

    @staticmethod
    def upload_file(file_name: str, folder_name: str, file_object: any):
        return s3_client_wrapper.upload_file_from_s3(
        settings.get_s3_bucket_name(),
        S3Utils.get_file_path(file_name, folder_name),
        file_object)

    @staticmethod
    def download_file(file_name: str, folder_name: str):
        return s3_client_wrapper.download_file_from_s3(
        settings.get_s3_bucket_name(),
        S3Utils.get_file_path(file_name, folder_name))

    @staticmethod
    def download_file_from_root(file_path: str):
        return s3_client_wrapper.download_file_from_s3(
        settings.get_s3_bucket_name(),
        file_path
        )
        
    @staticmethod
    def get_file_path(file_name: str, folder_name: str) -> str:
        if folder_name == settings.get_s3_help_folder_name():
            return settings.get_s3_help_folder_name() + SEPARATOR + file_name
        elif folder_name == settings.get_s3_guides_faq_files_folder():
            return settings.get_s3_guides_faq_files_folder() + SEPARATOR + file_name
        elif folder_name == settings.get_s3_workday_articles_inbound_folder():
            return settings.get_s3_workday_articles_inbound_folder() + SEPARATOR + file_name
        else:
            raise ValueError(f"Invalid folder type, Choose {settings.get_s3_help_folder_name()} or {settings.get_s3_guides_faq_files_folder()}.")
        
    @staticmethod
    def get_folder_prefix(folder_name: str) -> str:
        if folder_name == settings.get_s3_help_folder_name():
            return settings.get_s3_help_folder_name()
        elif folder_name == settings.get_s3_guides_faq_files_folder():
            return settings.get_s3_guides_faq_files_folder()
        else:
            raise ValueError(f"Invalid folder type. Choose {settings.get_s3_help_folder_name()} or {settings.get_s3_guides_faq_files_folder()}.")
        
    @staticmethod
    def list_files_in_folder(folder_name: str):
        bucket_name = settings.get_s3_bucket_name()
        folder_path = S3Utils.get_folder_prefix(folder_name)
        response = s3_client_wrapper.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
        if 'Contents' in response:
            files = [content['Key'] for content in response['Contents']]
            # Strip the folder path from the file names
            stripped_files = [file.replace(folder_path + "/", "") for file in files]
            return stripped_files
        else:
            return []
    
    ## For New Data ingestion
    @staticmethod
    def upload_file_v1(file_name: str, prefix_folder: str, file_object: any):
        return s3_client_wrapper.upload_file_from_s3(
        settings.get_s3_bucket_name(),
        S3Utils.get_file_path_v1(file_name, prefix_folder),
        file_object)

    @staticmethod
    def download_file_v1(file_name: str, prefix_folder: str):
        return s3_client_wrapper.download_file_from_s3(
        settings.get_s3_bucket_name(),
        S3Utils.get_file_path_v1(file_name, prefix_folder))

    @staticmethod
    def get_file_path_v1(file_name: str, prefix_folder: str) -> str:
        return prefix_folder + SEPARATOR + file_name

    @staticmethod
    def get_folder_prefix_v1(folder_name: str) -> str:
        if folder_name == settings.get_s3_inbound_folder():
            return settings.get_s3_inbound_folder()
        elif folder_name == settings.get_s3_outbound_folder():
            return settings.get_s3_outbound_folder()
        else:
            raise ValueError(f"Invalid folder type. Choose {settings.get_s3_inbound_folder()}.")

    @staticmethod
    def list_files_in_folder_v1(folder_name: str) -> list[str]:
        bucket_name = settings.get_s3_bucket_name()
        folder_path = folder_name
        response = s3_client_wrapper.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
        if 'Contents' in response:
            files = [content['Key'] for content in response['Contents']]
            # Strip the folder path from the file names
            stripped_files = [file.replace(folder_path + "/", "") for file in files]
            return stripped_files
        else:
            return []