from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import re

# Setup Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'cmms-service-account.json'

# Authenticate with the service account
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

# Folder ID of the shared folder containing the Google Sheets files
FOLDER_ID = '1Ke7N4YQuTRVTuTWKqsxB5crnhT7lYn1A'
DOWNLOAD_PATH = '/Users/denielchiang/Develop/room3327/python/members/raw'

# Ensure the download path exists
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# Retrieve local file base names
local_files = {os.path.splitext(file)[0] for file in os.listdir(DOWNLOAD_PATH) if file.endswith('.csv')}
print("Local files:", local_files)  # Debug: Print all local file base names

# Query to get only Google Sheets files in the specified folder
query = f"'{FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.spreadsheet'"

# Use pagination to retrieve all files
page_token = None
missing_files = []

while True:
    results = drive_service.files().list(
        q=query,
        spaces='drive',
        fields="nextPageToken, files(id, name, mimeType)",
        pageToken=page_token
    ).execute()
    
    files = results.get('files', [])

    if not files:
        print('No Google Sheets files found in the folder.')
        break

    # Process each file in the current page of results
    for file in files:
        file_id = file['id']
        file_name = file['name']
        
        # Safe file name for local use (removing special characters)
        safe_file_name = re.sub(r'[\\/*?:"<>|]', "_", file_name)
        google_drive_base_name = os.path.splitext(safe_file_name)[0]  # Get the base name without extension

        # Print Google Drive base name for verification
        print("Google Drive file base name:", google_drive_base_name)

        # Check if this file is missing locally
        if google_drive_base_name not in local_files:
            missing_files.append((file_id, safe_file_name))
    
    # Check if there is another page of results
    page_token = results.get('nextPageToken')
    if not page_token:
        break  # No more pages

# Final report
if missing_files:
    print(f"Missing files found: {len(missing_files)}")
    for file_id, safe_file_name in missing_files:
        print(f"Missing file: {safe_file_name}")
        
        # Optional: Download the missing file
        try:
            request = drive_service.files().export_media(fileId=file_id, mimeType='text/csv')
            csv_content = request.execute().decode('utf-8')
            
            # Save CSV content to a file
            csv_file_path = os.path.join(DOWNLOAD_PATH, f"{safe_file_name}.csv")
            with open(csv_file_path, 'w', encoding='utf-8') as f:
                f.write(csv_content)
            
            print(f"Downloaded missing file: {csv_file_path}")
        except Exception as e:
            print(f"Failed to download {safe_file_name}: {e}")
else:
    print("All files are accounted for locally. No downloads necessary.")
