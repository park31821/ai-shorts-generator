from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.config import get_settings
from typing import Dict, Any
import json

class GoogleSheetsClient:
    def __init__(self):
        settings = get_settings()
        credentials_dict = json.loads(settings.google_sheets_credentials)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_dict,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        self.service = build('sheets', 'v4', credentials=credentials)
        self.spreadsheet_id = settings.spreadsheet_id
        self.worksheet_name = settings.worksheet_name

    async def get_content(self, content_id: str) -> Dict[str, Any]:
        try:
            range_name = f'{self.worksheet_name}!A:Z'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                raise Exception("No data found in spreadsheet")

            # 헤더 행 찾기
            headers = values[0]
            content_row = None
            
            # content_id와 일치하는 행 찾기
            for row in values[1:]:
                if row[0] == content_id:
                    content_row = row
                    break

            if not content_row:
                raise Exception(f"Content with ID {content_id} not found")

            # 헤더와 값을 매핑하여 딕셔너리 생성
            content_data = {}
            for i, header in enumerate(headers):
                if i < len(content_row):
                    content_data[header] = content_row[i]
                else:
                    content_data[header] = None

            return content_data

        except Exception as e:
            raise Exception(f"Failed to fetch content from Google Sheets: {str(e)}")

    async def list_contents(self) -> list:
        try:
            range_name = f'{self.worksheet_name}!A:Z'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return []

            headers = values[0]
            contents = []

            for row in values[1:]:
                content = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        content[header] = row[i]
                    else:
                        content[header] = None
                contents.append(content)

            return contents

        except Exception as e:
            raise Exception(f"Failed to list contents from Google Sheets: {str(e)}") 