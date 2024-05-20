import boto3
import streamlit as st

AWS_ACCESS_KEY = st.secrets["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = st.secrets["AWS_SECRET_KEY"]



# get the folder names from the s3 bucket
def get_folders_from_s3() -> list[str]:
    bucket_name='qucoursify'
    prefix='qu-super-editor'
    s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    folders = [content["Key"] for content in response["Contents"] if content["Key"].endswith("/") and content["Key"] != prefix + "/"]
    # remove the prefix from the folder names
    folders = [folder.replace(prefix + "/", "") for folder in folders]
    # remove the trailing slash from the folder names
    folders = [folder[:-1] for folder in folders]
    return folders

# get all the file names for each folder from the s3 bucket. map them so that the files are grouped by folder
def get_files_by_folder_from_s3() -> dict[str, list[str]]:
    bucket_name='qucoursify'
    prefix='qu-super-editor'
    s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    files = [content["Key"] for content in response["Contents"]]
    folders = [content["Key"] for content in response["Contents"] if content["Key"].endswith("/")]
    files_by_folder = {}
    for folder in folders:
        files_by_folder[folder] = [file for file in files if file.startswith(folder)]
    # delete the key qu-super-editor/
    del files_by_folder["qu-super-editor/"]
    # remove "qu-super-editor/" from all the keys
    files_by_folder = {key.replace("qu-super-editor/", ""): value for key, value in files_by_folder.items()}
    # remove the folder name from the list of files
    files_by_folder = {key: [value for value in value if value != prefix+"/"+key] for key, value in files_by_folder.items()}
    # remove the trailing slash from the folder names
    files_by_folder = {key[:-1]: value for key, value in files_by_folder.items()}
    return files_by_folder

# get the content of a file from the s3 bucket
def get_file_content_from_s3(key: str) -> str:
    bucket_name='qucoursify'
    s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    response = s3.get_object(Bucket=bucket_name, Key=key)
    content = response["Body"].read().decode("utf-8")
    return content

# save the content of a file to the s3 bucket
def save_file_content_to_s3(content: str, key: str) -> dict[str, str]:
    bucket_name='qucoursify'
    s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    response = s3.put_object(Bucket=bucket_name, Key=key, Body=content)
    return response

