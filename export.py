from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import re
import time
import ssl

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

# Query to get only Google Sheets files in the specified folder
query = f"'{FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.spreadsheet'"

# Use pagination to retrieve all files
page_token = None

# Set a maximum number of retries
MAX_RETRIES = 3

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
        mime_type = file.get('mimeType')
        
        print(f"Processing file - ID: {file_id}, Name: {file_name}, MIME Type: {mime_type}")

        # Only attempt to export Google Sheets files
        if mime_type == 'application/vnd.google-apps.spreadsheet':
            # Safe file name for saving
            safe_file_name = re.sub(r'[\\/*?:"<>|]', "_", file_name)
            csv_file_path = os.path.join(DOWNLOAD_PATH, f"{safe_file_name}.csv")

            # Retry mechanism
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    # Export Google Sheets file as CSV
                    request = drive_service.files().export_media(fileId=file_id, mimeType='text/csv')
                    csv_content = request.execute().decode('utf-8')

                    # Save CSV content to a file
                    with open(csv_file_path, 'w', encoding='utf-8') as f:
                        f.write(csv_content)
                    
                    print(f"CSV file saved: {csv_file_path}")
                    break  # Exit the retry loop if successful
                except ssl.SSLError as e:
                    print(f"SSL error on attempt {attempt} for file {file_name}: {e}")
                    if attempt < MAX_RETRIES:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        print(f"Failed to download {file_name} after {MAX_RETRIES} attempts")
                except Exception as e:
                    print(f"Failed to download {file_name}: {e}")
                    break  # Break on non-SSL errors

    # Check if there is another page of results
    page_token = results.get('nextPageToken')
    if not page_token:
        break  # No more pages
