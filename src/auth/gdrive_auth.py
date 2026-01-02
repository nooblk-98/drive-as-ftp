"""
Google Drive Authentication Module
Handles OAuth2 authentication with Google Drive API
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import io

# If modifying these scopes, delete the token.json file.
SCOPES = ['https://www.googleapis.com/auth/drive']


class GoogleDriveAuth:
    """Handles Google Drive authentication and service initialization"""
    
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.creds = None
        self.service = None
    
    def authenticate(self):
        """Authenticates with Google Drive and returns the service object"""
        # The token.json stores the user's access and refresh tokens
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file '{self.credentials_file}' not found. "
                        "Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                use_console = os.getenv('OAUTH_CONSOLE', '').lower() in ('1', 'true', 'yes')
                if use_console:
                    # Prefer console flow for remote servers to avoid localhost redirects.
                    if hasattr(flow, 'run_console'):
                        self.creds = flow.run_console()
                    else:
                        auth_url, _ = flow.authorization_url(prompt='consent')
                        print("Open this URL in your browser and authorize the app:")
                        print(auth_url)
                        code = input("Enter the authorization code: ").strip()
                        flow.fetch_token(code=code)
                        self.creds = flow.credentials
                else:
                    try:
                        self.creds = flow.run_local_server(port=0)
                    except Exception as exc:
                        print(
                            "Local browser authentication failed, "
                            "falling back to console flow."
                        )
                        print(f"Reason: {exc}")
                        self.creds = flow.run_local_server(port=0, open_browser=False)
            
            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('drive', 'v3', credentials=self.creds)
        return self.service
    
    def get_service(self):
        """Returns the authenticated Google Drive service"""
        if not self.service:
            self.authenticate()
        return self.service
