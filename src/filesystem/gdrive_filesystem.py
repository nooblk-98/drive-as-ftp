"""
Google Drive Filesystem for FTP
Implements filesystem operations for Google Drive
"""

import os
import io
import stat
import time
from datetime import datetime
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient.errors import HttpError


class GoogleDriveFileSystem:
    """Provides filesystem-like interface to Google Drive"""
    
    def __init__(self, service):
        self.service = service
        self._cache = {}
        self._cache_timeout = 60  # Cache timeout in seconds
    
    def _escape_query_value(self, value):
        """Escape special characters for Google Drive API query"""
        # Escape backslashes first, then single quotes
        value = value.replace('\\', '\\\\')
        value = value.replace("'", "\\'")
        return value
    
    def _get_file_by_path(self, path):
        """Get file/folder by path"""
        if path == '/' or path == '':
            return {'id': 'root', 'name': '/', 'mimeType': 'application/vnd.google-apps.folder'}
        
        parts = path.strip('/').split('/')
        parent_id = 'root'
        
        for part in parts:
            escaped_part = self._escape_query_value(part)
            query = f"name='{escaped_part}' and '{parent_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType, size, modifiedTime, createdTime)"
            ).execute()
            
            files = results.get('files', [])
            if not files:
                return None
            
            parent_id = files[0]['id']
            file_info = files[0]
        
        return file_info
    
    def _get_file_by_id(self, file_id):
        """Get file metadata by ID"""
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size, modifiedTime, createdTime, parents"
            ).execute()
            return file
        except HttpError:
            return None
    
    def list_directory(self, path):
        """List files in a directory"""
        file_info = self._get_file_by_path(path)
        if not file_info:
            return []
        
        if file_info['mimeType'] != 'application/vnd.google-apps.folder':
            return []
        
        query = f"'{file_info['id']}' in parents and trashed=false"
        results = self.service.files().list(
            q=query,
            fields="files(id, name, mimeType, size, modifiedTime, createdTime)",
            pageSize=1000
        ).execute()
        
        return results.get('files', [])
    
    def get_file_stats(self, path):
        """Get file statistics (size, mtime, etc.)"""
        file_info = self._get_file_by_path(path)
        if not file_info:
            return None
        
        is_dir = file_info['mimeType'] == 'application/vnd.google-apps.folder'
        size = int(file_info.get('size', 0)) if not is_dir else 0
        
        # Parse modification time
        mtime_str = file_info.get('modifiedTime', file_info.get('createdTime'))
        if mtime_str:
            mtime = datetime.fromisoformat(mtime_str.replace('Z', '+00:00')).timestamp()
        else:
            mtime = time.time()
        
        return {
            'size': size,
            'mtime': mtime,
            'isdir': is_dir,
            'name': file_info['name'],
            'id': file_info['id']
        }
    
    def read_file(self, path):
        """Read file content"""
        file_info = self._get_file_by_path(path)
        if not file_info or file_info['mimeType'] == 'application/vnd.google-apps.folder':
            return None
        
        request = self.service.files().get_media(fileId=file_info['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        fh.seek(0)
        return fh
    
    def write_file(self, path, file_obj):
        """Write file content"""
        parts = path.strip('/').split('/')
        filename = parts[-1]
        parent_path = '/' + '/'.join(parts[:-1]) if len(parts) > 1 else '/'
        
        # Get parent folder
        parent_info = self._get_file_by_path(parent_path)
        if not parent_info:
            return False
        
        # Check if file exists
        existing_file = self._get_file_by_path(path)
        
        file_metadata = {'name': filename}
        media = MediaFileUpload(file_obj, resumable=True)
        
        try:
            if existing_file:
                # Update existing file
                self.service.files().update(
                    fileId=existing_file['id'],
                    media_body=media
                ).execute()
            else:
                # Create new file
                file_metadata['parents'] = [parent_info['id']]
                self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
            return True
        except HttpError as e:
            print(f"Error writing file: {e}")
            return False
    
    def delete_file(self, path):
        """Delete a file"""
        file_info = self._get_file_by_path(path)
        if not file_info:
            return False
        
        try:
            self.service.files().delete(fileId=file_info['id']).execute()
            return True
        except HttpError:
            return False
    
    def create_directory(self, path):
        """Create a directory"""
        parts = path.strip('/').split('/')
        dirname = parts[-1]
        parent_path = '/' + '/'.join(parts[:-1]) if len(parts) > 1 else '/'
        
        parent_info = self._get_file_by_path(parent_path)
        if not parent_info:
            return False
        
        file_metadata = {
            'name': dirname,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_info['id']]
        }
        
        try:
            self.service.files().create(body=file_metadata, fields='id').execute()
            return True
        except HttpError:
            return False
    
    def rename_file(self, old_path, new_path):
        """Rename a file"""
        file_info = self._get_file_by_path(old_path)
        if not file_info:
            return False
        
        new_name = new_path.strip('/').split('/')[-1]
        
        try:
            self.service.files().update(
                fileId=file_info['id'],
                body={'name': new_name}
            ).execute()
            return True
        except HttpError:
            return False
