import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

def test_google_sheets():
    try:
        # Load environment variables
        load_dotenv()
        
        # Get credentials from environment variable
        credentials_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
        if not credentials_json:
            raise ValueError("GOOGLE_SHEETS_CREDENTIALS environment variable is not set")
        
        print("Credentials JSON loaded successfully")
        
        # Parse credentials JSON
        try:
            credentials_info = json.loads(credentials_json)
            print("JSON parsing successful")
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print("First 100 characters of credentials_json:", credentials_json[:100])
            raise
        
        # Create credentials object
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        print("Credentials object created successfully")
        
        # Build the Sheets API service
        service = build('sheets', 'v4', credentials=credentials)
        print("Sheets API service built successfully")
        
        # Get spreadsheet ID from environment variable
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        if not spreadsheet_id:
            raise ValueError("SPREADSHEET_ID environment variable is not set")
        print(f"Spreadsheet ID: {spreadsheet_id}")

        # Get sheet names
        sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')
        sheet_name = sheets[0]['properties']['title']
        print(f"Using sheet name: {sheet_name}")
        
        # Test reading from the spreadsheet
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=f'{sheet_name}!A1:D10'  # Use actual sheet name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print('No data found.')
        else:
            print('Data found:')
            for row in values:
                print(row)
        
        print("\nGoogle Sheets API test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error testing Google Sheets API: {str(e)}")
        return False

if __name__ == "__main__":
    test_google_sheets() 