import os
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request  # <-- Add this line

SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive.file']

# Get credentials path from environment variable, default to 'credentials.json'
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")

def create_google_doc(title, content):
    creds = None
    # Token file stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists(GOOGLE_CREDENTIALS_PATH):
                flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                raise Exception(f"Google credentials not found at {GOOGLE_CREDENTIALS_PATH}")
        # Save the credentials for next run
        try:
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            # Log but don't crash if token can't be saved (common in cloud)
            logging.warning(f"Could not save token.json: {e}")

    try:
        service = build('docs', 'v1', credentials=creds)
        doc = service.documents().create(body={'title': title}).execute()
        doc_id = doc.get('documentId')
        requests = [{
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }]
        service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
        return f"https://docs.google.com/document/d/{doc_id}/edit"
    except Exception as e:
        logging.error(f"Google Docs API error: {e}")
        return {"error": "There was a problem creating your Google Doc. Please try again later."}