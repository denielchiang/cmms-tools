from google.oauth2 import service_account
from googleapiclient.discovery import build

# Setup Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'cmms-service-account.json'  # Replace with your service account file

# Authenticate with the service account
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

# Folder ID of the shared folder containing the Google Sheets files
FOLDER_ID = '1Ke7N4YQuTRVTuTWKqsxB5crnhT7lYn1A'  # Replace with your specific folder ID

# Query to get only Google Sheets files in the specified folder
query = f"'{FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.spreadsheet'"

# Initialize file count and handle pagination
page_token = None
total_files = 0

while True:
    results = drive_service.files().list(
        q=query,
        spaces='drive',
        fields="nextPageToken, files(id, name)",
        pageToken=page_token
    ).execute()
    
    files = results.get('files', [])
    total_files += len(files)
    
    # Print the count of files retrieved in each page (for debugging purposes)
    print(f"Files retrieved in this page: {len(files)}")

    # Check if there is another page of results
    page_token = results.get('nextPageToken')
    if not page_token:
        break  # No more pages

# Final count
print(f"Total number of Google Sheets files in the folder: {total_files}")
