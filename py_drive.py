from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SERVICE_ACCOUNT = "./credentials.json"

SCOPES = ['https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT, scopes=SCOPES
)
service = build('drive', 'v3', credentials=credentials)

def upload_file(file_path, mime_type, folder_id=None):
    file_metadata = {'name': file_path.split('/')[-1]}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    media = MediaFileUpload(file_path, mimetype=mime_type)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f'File ID: {file.get("id")}')

# Example usage
# upload_file('./current.pdf', 'application/pdf')

def create_folder(name, parent_id=None):
    folder_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'

    }
    if parent_id:
        folder_metadata['parents'] = [parent_id]

    folder = service.files().create(body=folder_metadata, fields='id').execute()
    print(f'Folder ID: {folder.get("id")}')
    return folder.get('id')

# Example usage
folder_id = create_folder('New Folder Today', parent_id="1JtiUFBlXchgibYyMVTBLmWqSrvrapptg")