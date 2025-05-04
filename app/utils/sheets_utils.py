from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import os
from typing import List, Dict, Any

class SheetsUtils:
    def __init__(self):
        # Load credentials from environment variable
        credentials_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
        if not credentials_json:
            raise ValueError("GOOGLE_SHEETS_CREDENTIALS environment variable is not set")
        
        # Parse credentials JSON
        credentials_info = json.loads(credentials_json)
        
        # Create credentials object
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        # Build the Sheets API service
        self.service = build('sheets', 'v4', credentials=credentials)
        self.spreadsheet_id = os.getenv('SPREADSHEET_ID')
        if not self.spreadsheet_id:
            raise ValueError("SPREADSHEET_ID environment variable is not set")

    def get_sheet_name(self) -> str:
        """Get the name of the first sheet in the spreadsheet."""
        sheet_metadata = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')
        return sheets[0]['properties']['title']

    def get_pending_topics(self) -> List[Dict[str, Any]]:
        """Get topics that need script generation (where Data column is '❌' or empty, or where Data is '✅' but Script is empty)."""
        sheet_name = self.get_sheet_name()
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f'{sheet_name}!A1:G100'  # A부터 G열까지 가져오도록 수정
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return []
        
        # Find column indices
        headers = values[0]
        print("Available headers:", headers)  # 헤더 정보 출력
        
        try:
            topic_idx = headers.index('Topic')
            data_idx = headers.index('Data')
            script_idx = headers.index('Script')
            voice_idx = headers.index('Voice')
            video_idx = headers.index('Video')
            video_link_idx = headers.index('Video Link')
            status_idx = headers.index('Status')
        except ValueError as e:
            print(f"Error finding column: {str(e)}")
            return []
        
        pending_topics = []
        for row_idx, row in enumerate(values[1:], start=2):  # start=2 because of 1-based indexing and header row
            # 모든 열의 데이터를 안전하게 가져오기
            topic = row[topic_idx] if len(row) > topic_idx else ""
            data = row[data_idx] if len(row) > data_idx else ""
            script = row[script_idx] if len(row) > script_idx else ""
            voice = row[voice_idx] if len(row) > voice_idx else ""
            video = row[video_idx] if len(row) > video_idx else ""
            video_link = row[video_link_idx] if len(row) > video_link_idx else ""
            status = row[status_idx] if len(row) > status_idx else ""
            
            # Data 열이 비어있거나 '❌'인 경우, 또는 Data가 '✅'이지만 Script가 비어있는 경우 처리
            if (not data or data == '❌') or (data == '✅' and not script):
                pending_topics.append({
                    'row': row_idx,
                    'topic': topic,
                    'script': script,
                    'voice': voice,
                    'video': video,
                    'video_link': video_link,
                    'status': status,
                    'script_idx': script_idx,
                    'data_idx': data_idx,
                    'voice_idx': voice_idx,
                    'video_idx': video_idx,
                    'video_link_idx': video_link_idx,
                    'status_idx': status_idx
                })
        
        return pending_topics

    def update_row(self, row: int, script: str, data_idx: int, script_idx: int, voice_idx: int, video_idx: int, video_link_idx: int, status_idx: int) -> None:
        """Update a row with the generated script and mark Data column as '✅'."""
        sheet_name = self.get_sheet_name()
        
        # 현재 행의 데이터를 가져옴
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f'{sheet_name}!A{row}:G{row}'
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return
        
        # 현재 행의 데이터를 리스트로 변환
        current_row = values[0]
        
        # 필요한 열이 없는 경우 빈 문자열로 채움
        while len(current_row) < 7:  # A부터 G열까지
            current_row.append("")
        
        # 스크립트 업데이트
        current_row[script_idx] = script
        # Data 열을 '✅'로 표시
        current_row[data_idx] = '✅'
        # Status 열을 "Script generated"로 업데이트
        current_row[status_idx] = "Script generated"
        
        # 업데이트할 범위와 값 설정
        range_name = f'{sheet_name}!A{row}:G{row}'
        body = {
            'values': [current_row]
        }
        
        # 스프레드시트 업데이트
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

    def append_row(self, topic: str) -> None:
        """Append a new row with the given topic and set Data column to '✅'."""
        sheet_name = self.get_sheet_name()
        
        # 현재 헤더 정보 가져오기
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f'{sheet_name}!A1:G1'
        ).execute()
        
        headers = result.get('values', [[]])[0]
        
        # 각 열의 인덱스 찾기
        try:
            topic_idx = headers.index('Topic')
            data_idx = headers.index('Data')
            script_idx = headers.index('Script')
            voice_idx = headers.index('Voice')
            video_idx = headers.index('Video')
            video_link_idx = headers.index('Video Link')
            status_idx = headers.index('Status')
        except ValueError as e:
            print(f"Error finding column: {str(e)}")
            return
        
        # 새로운 행 데이터 생성 (모든 열을 빈 문자열로 초기화)
        new_row = [''] * len(headers)
        
        # Topic과 Data 열 설정
        new_row[topic_idx] = topic
        new_row[data_idx] = '✅'
        
        # 스프레드시트에 행 추가
        range_name = f'{sheet_name}!A:G'
        body = {
            'values': [new_row]
        }
        
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute() 