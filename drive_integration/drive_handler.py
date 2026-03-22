import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

class DriveHandler:
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self):
        self.creds = None
        self.TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.pickle')
        self.CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), 'client_secret.json')
        
        # Root folder ID (Optional)
        self.PARENT_ID = os.getenv('PARENT_DRIVE_FOLDER_ID')
        
        # Load existing credentials if available
        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE, 'rb') as token:
                self.creds = pickle.load(token)
                
        # If there are no valid credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.CLIENT_SECRET_FILE):
                    print(f"ERROR: {self.CLIENT_SECRET_FILE} not found. Please provide OAuth credentials.")
                    self.service = None
                    return
                # Trigger local server flow
                flow = InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRET_FILE, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.TOKEN_FILE, 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('drive', 'v3', credentials=self.creds)

    def download_file(self, file_id):
        """Downloads a file's content as bytes."""
        if not self.service: return None
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        return fh.getvalue()

    def create_folder(self, folder_name, parent_id=None):
        if not self.service: return None
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        file = self.service.files().create(body=file_metadata, fields='id').execute()
        return file.get('id')

    def initialize_event_folders(self, event_name):
        """Creates the main event folder and all required subfolders."""
        if not self.service: return None
        
        # Main Event folder (Parented to our shared root folder)
        print(f"DEBUG: Creating event folder with root parent: {self.PARENT_ID}")
        root_id = self.create_folder(event_name, parent_id=self.PARENT_ID)
        if not root_id: return None
        print(f"DEBUG: Root Folder Created: {root_id}")
        
        subfolders = [
            'Budget',
            'Resources',
            'Posters',
            'Content',
            'Event_Pictures',
            'Event_Videos'
        ]
        
        folder_ids = {'root': root_id}
        for sub in subfolders:
            folder_ids[sub] = self.create_folder(sub, root_id)
            
        return folder_ids

    def upload_file(self, file_path, file_name, folder_id):
        """Uploads a file to a specific folder and returns its web view link."""
        if not self.service: return None, None
        
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(file_path, resumable=True)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        # Set permissions to anyone with link (optional, depends on needs)
        # self.service.permissions().create(
        #     fileId=file.get('id'),
        #     body={'role': 'reader', 'type': 'anyone'}
        # ).execute()
        
        return file.get('id'), file.get('webViewLink')

    def upload_file_from_stream(self, file_stream, file_name, mime_type, folder_id):
        """Uploads a file from a binary stream (e.g. Flask's request.files)."""
        if not self.service: return None, None
        
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        from googleapiclient.http import MediaIoBaseUpload
        media = MediaIoBaseUpload(file_stream, mimetype=mime_type, resumable=True)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        return file.get('id'), file.get('webViewLink')

# Singleton instance
drive_handler = DriveHandler()
