import firebase_admin
from firebase_admin import credentials, storage

cred = credentials.Certificate("../../services/mbuckets-a6fe3-685e26c8f1a2.json")
firebase_admin.initialize_app(cred, {'storageBucket': "mbuckets-a6fe3.appspot.com"})

def upload_file(media_url):
    file_path = media_url
    bucket = storage.bucket() # storage bucket
    blob = bucket.blob(file_path)
    blob.upload_from_filename(file_path)
    blob.make_public()
    return blob.public_url