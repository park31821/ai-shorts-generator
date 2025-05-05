from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

# 상수 정의
SHEET_RANGE = 'A1:G100'
REQUIRED_COLUMNS = ['Topic', 'Data', 'Script', 'Voice', 'Video', 'Video Link', 'Status']
SHEETS_SCOPE = 'https://www.googleapis.com/auth/spreadsheets'

@dataclass
class TopicData:
    """주제 데이터를 저장하는 데이터 클래스"""
    row: int
    topic: str
    script: str
    voice: str
    video: str
    video_link: str
    data_status: str  # Data 열의 값
    status: str      # Status 열의 값
    column_indices: Dict[str, int]

class SheetsUtils:
    """Google Sheets API를 사용하여 스프레드시트를 관리하는 유틸리티 클래스"""
    
    def __init__(self):
        """SheetsUtils 인스턴스를 초기화합니다."""
        self.service = self._initialize_service()
        self.spreadsheet_id = self._get_spreadsheet_id()
        self.sheet_name = self.get_sheet_name()

    def _initialize_service(self) -> Any:
        """Google Sheets API 서비스를 초기화합니다.

        Returns:
            Any: Google Sheets API 서비스 객체

        Raises:
            ValueError: 환경 변수가 설정되지 않은 경우
            json.JSONDecodeError: JSON 파싱에 실패한 경우
        """
        credentials_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
        if not credentials_json:
            raise ValueError("GOOGLE_SHEETS_CREDENTIALS environment variable is not set")
        
        try:
            credentials_info = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=[SHEETS_SCOPE]
            )
            return build('sheets', 'v4', credentials=credentials)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse credentials JSON: {str(e)}")

    def _get_spreadsheet_id(self) -> str:
        """스프레드시트 ID를 가져옵니다.

        Returns:
            str: 스프레드시트 ID

        Raises:
            ValueError: 환경 변수가 설정되지 않은 경우
        """
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        if not spreadsheet_id:
            raise ValueError("SPREADSHEET_ID environment variable is not set")
        return spreadsheet_id

    def get_sheet_name(self) -> str:
        """스프레드시트의 첫 번째 시트 이름을 가져옵니다.

        Returns:
            str: 시트 이름

        Raises:
            HttpError: API 호출에 실패한 경우
        """
        try:
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            sheets = sheet_metadata.get('sheets', [])
            if not sheets:
                raise ValueError("No sheets found in the spreadsheet")
            return sheets[0]['properties']['title']
        except HttpError as e:
            raise ValueError(f"Failed to get sheet name: {str(e)}")

    def _get_column_indices(self, headers: List[str]) -> Dict[str, int]:
        """필요한 열의 인덱스를 가져옵니다.

        Args:
            headers: 헤더 행의 데이터

        Returns:
            Dict[str, int]: 열 이름과 인덱스의 매핑

        Raises:
            ValueError: 필수 열을 찾을 수 없는 경우
        """
        try:
            return {col: headers.index(col) for col in REQUIRED_COLUMNS}
        except ValueError as e:
            raise ValueError(f"Required column not found: {str(e)}")

    def _get_row_data(self, row: List[str], indices: Dict[str, int]) -> Dict[str, str]:
        """행 데이터를 안전하게 가져옵니다.

        Args:
            row: 행 데이터
            indices: 열 인덱스 매핑

        Returns:
            Dict[str, str]: 열 이름과 값의 매핑
        """
        return {
            col: row[idx] if len(row) > idx else ""
            for col, idx in indices.items()
        }

    def get_pending_topics(self) -> List[TopicData]:
        """처리가 필요한 주제 목록을 가져옵니다.

        Returns:
            List[TopicData]: 처리 대기 중인 주제 목록
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!{SHEET_RANGE}'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return []
            
            headers = values[0]
            print("Available headers:", headers)
            
            column_indices = self._get_column_indices(headers)
            pending_topics = []
            
            for row_idx, row in enumerate(values[1:], start=2):
                row_data = self._get_row_data(row, column_indices)
                
                # 스크립트 생성이 필요한 경우
                if (not row_data['Data'] or row_data['Data'] == '❌') or \
                   (row_data['Data'] == '✅' and not row_data['Script']):
                    pending_topics.append(TopicData(
                        row=row_idx,
                        topic=row_data['Topic'],
                        script=row_data['Script'],
                        voice=row_data['Voice'],
                        video=row_data['Video'],
                        video_link=row_data['Video Link'],
                        data_status=row_data['Data'],
                        status=row_data['Status'],
                        column_indices=column_indices
                    ))
                # 음성 생성이 필요한 경우
                elif row_data['Script'] and row_data['Data'] == '✅' and not row_data['Voice']:
                    pending_topics.append(TopicData(
                        row=row_idx,
                        topic=row_data['Topic'],
                        script=row_data['Script'],
                        voice=row_data['Voice'],
                        video=row_data['Video'],
                        video_link=row_data['Video Link'],
                        data_status=row_data['Data'],
                        status=row_data['Status'],
                        column_indices=column_indices
                    ))
            
            return pending_topics
            
        except HttpError as e:
            raise ValueError(f"Failed to get pending topics: {str(e)}")

    def update_row(self, topic_data: TopicData, script: str) -> None:
        """행을 업데이트합니다.

        Args:
            topic_data: 업데이트할 주제 데이터
            script: 새로 생성된 스크립트

        Raises:
            HttpError: API 호출에 실패한 경우
        """
        try:
            # 현재 행 데이터 가져오기
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A{topic_data.row}:G{topic_data.row}'
            ).execute()
            
            values = result.get('values', [[]])[0]
            current_row = values + [''] * (7 - len(values))  # A부터 G열까지
            
            # 데이터 업데이트
            current_row[topic_data.column_indices['Script']] = script
            current_row[topic_data.column_indices['Data']] = '✅'
            current_row[topic_data.column_indices['Status']] = "Script generated"
            
            # 스프레드시트 업데이트
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A{topic_data.row}:G{topic_data.row}',
                valueInputOption='RAW',
                body={'values': [current_row]}
            ).execute()
            
        except HttpError as e:
            raise ValueError(f"Failed to update row: {str(e)}")

    def append_row(self, topic: str) -> None:
        """새로운 행을 추가합니다.

        Args:
            topic: 추가할 주제

        Raises:
            HttpError: API 호출에 실패한 경우
        """
        try:
            # 헤더 정보 가져오기
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A1:G1'
            ).execute()
            
            headers = result.get('values', [[]])[0]
            column_indices = self._get_column_indices(headers)
            
            # 새로운 행 생성
            new_row = [''] * len(headers)
            new_row[column_indices['Topic']] = topic
            new_row[column_indices['Data']] = '✅'
            
            # 행 추가
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A:G',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': [new_row]}
            ).execute()
            
        except HttpError as e:
            raise ValueError(f"Failed to append row: {str(e)}")

    def update_voice_status(self, topic_data: TopicData, voice_status: str, status_message: str) -> None:
        """음성 생성 상태를 업데이트합니다.

        Args:
            topic_data: 업데이트할 주제 데이터
            voice_status: 음성 상태 (예: "✅")
            status_message: 상태 메시지

        Raises:
            HttpError: API 호출에 실패한 경우
        """
        try:
            # 현재 행 데이터 가져오기
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A{topic_data.row}:G{topic_data.row}'
            ).execute()
            
            values = result.get('values', [[]])[0]
            current_row = values + [''] * (7 - len(values))  # A부터 G열까지
            
            # 데이터 업데이트
            current_row[topic_data.column_indices['Voice']] = voice_status
            current_row[topic_data.column_indices['Status']] = status_message
            
            # 스프레드시트 업데이트
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A{topic_data.row}:G{topic_data.row}',
                valueInputOption='RAW',
                body={'values': [current_row]}
            ).execute()
            
        except HttpError as e:
            raise ValueError(f"Failed to update voice status: {str(e)}")

    def reset_voice_status(self, topic_data: TopicData) -> None:
        """음성 생성 상태를 초기화합니다.

        Args:
            topic_data: 초기화할 주제 데이터

        Raises:
            HttpError: API 호출에 실패한 경우
        """
        try:
            # 현재 행 데이터 가져오기
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A{topic_data.row}:G{topic_data.row}'
            ).execute()
            
            values = result.get('values', [[]])[0]
            current_row = values + [''] * (7 - len(values))  # A부터 G열까지
            
            # 데이터 업데이트
            current_row[topic_data.column_indices['Voice']] = ''
            current_row[topic_data.column_indices['Status']] = "Voice generation pending"
            
            # 스프레드시트 업데이트
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A{topic_data.row}:G{topic_data.row}',
                valueInputOption='RAW',
                body={'values': [current_row]}
            ).execute()
            
        except HttpError as e:
            raise ValueError(f"Failed to reset voice status: {str(e)}") 