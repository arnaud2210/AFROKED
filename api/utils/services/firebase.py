import firebase_admin
from firebase_admin import credentials, storage
import config

cred = credentials.Certificate(config.BUCKET_CREDS)
firebase_admin.initialize_app(cred, {'storageBucket': config.STORAGE_BUCKET})

def upload_file(media_url):
    file_path = media_url
    bucket = storage.bucket() # storage bucket
    blob = bucket.blob(file_path)
    blob.upload_from_filename(file_path)
    blob.make_public()
    return blob.public_url