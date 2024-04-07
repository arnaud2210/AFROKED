import os
import json
import sys


def load_env_from_json():
    json_file_path = os.path.dirname(__file__) + f"/static/config-dev.json"

    with open(json_file_path, 'r') as json_file:
        env_data = json.load(json_file)
    
    for key, value in env_data.items():
        os.environ[key] = str(value)

load_env_from_json()

SHORT_BASE_URL = os.getenv("SHORT_BASE_URL")
SERVER_HOST = os.getenv("SERVER_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")
DB_LINK = os.getenv("DB_LINK")
DB_PROD_LINK = os.getenv("DB_PROD_LINK")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ENVIRONMENT = os.getenv("ENVIRONMENT")
API_PORT = os.getenv("API_PORT")
BUCKET_CREDS = os.getenv("bucket_creds")
STORAGE_BUCKET = os.getenv("storage_bucket")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_FROM = os.getenv("SMTP_FROM")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
