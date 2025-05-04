import unittest
from unittest.mock import patch, MagicMock
from app.core.content_generator import ContentGenerator
from app.utils.sheets_utils import SheetsUtils, TopicData
from app.core.openai_client import OpenAIClient
from googleapiclient.errors import HttpError
from openai import OpenAIError

class TestContentGenerator(unittest.TestCase):
    """ContentGenerator 테스트 클래스"""

    def setUp(self):
        """테스트 설정"""
        self.content_generator = ContentGenerator()
        self.mock_topic_data = TopicData(
            row=2,
            topic="테스트 주제",
            script="",
            voice="",
            video="",
            video_link="",
            status="",
            column_indices={'Topic': 0, 'Data': 1, 'Script': 2, 'Voice': 3, 'Video': 4, 'Video Link': 5, 'Status': 6}
        )

    @patch('app.utils.sheets_utils.SheetsUtils.get_pending_topics')
    @patch('app.core.openai_client.OpenAIClient.generate_script')
    @patch('app.utils.sheets_utils.SheetsUtils.update_row')
    def test_process_pending_topics(self, mock_update_row, mock_generate_script, mock_get_pending_topics):
        """process_pending_topics 메서드 테스트"""
        # Mock 설정
        mock_get_pending_topics.return_value = [self.mock_topic_data]
        mock_generate_script.return_value = """
[INTRO]
테스트 도입부입니다.

[BODY]
테스트 본문입니다.

[OUTRO]
테스트 마무리입니다.
"""

        # 테스트 실행
        self.content_generator.process_pending_topics()

        # 검증
        mock_get_pending_topics.assert_called_once()
        mock_generate_script.assert_called_once()
        mock_update_row.assert_called_once()

    @patch('app.utils.sheets_utils.SheetsUtils.append_row')
    def test_add_topic(self, mock_append_row):
        """add_topic 메서드 테스트"""
        # 테스트 실행
        self.content_generator.add_topic("새로운 주제")

        # 검증
        mock_append_row.assert_called_once_with("새로운 주제")

    @patch('app.utils.sheets_utils.SheetsUtils.get_pending_topics')
    def test_process_pending_topics_sheets_error(self, mock_get_pending_topics):
        """Sheets API 에러 처리 테스트"""
        # Mock 설정 - Sheets API 에러 발생
        mock_get_pending_topics.side_effect = HttpError(
            resp=MagicMock(status=500),
            content=b'Internal Server Error'
        )

        # 테스트 실행 및 검증
        with self.assertRaises(ValueError) as context:
            self.content_generator.process_pending_topics()
        
        self.assertIn("Failed to get pending topics", str(context.exception))

    @patch('app.utils.sheets_utils.SheetsUtils.get_pending_topics')
    @patch('app.core.openai_client.OpenAIClient.generate_script')
    def test_process_pending_topics_openai_error(self, mock_generate_script, mock_get_pending_topics):
        """OpenAI API 에러 처리 테스트"""
        # Mock 설정
        mock_get_pending_topics.return_value = [self.mock_topic_data]
        mock_generate_script.side_effect = OpenAIError("API Error")

        # 테스트 실행 및 검증
        with self.assertRaises(Exception) as context:
            self.content_generator.process_pending_topics()
        
        self.assertIn("Failed to generate script", str(context.exception))

    @patch('app.utils.sheets_utils.SheetsUtils.get_pending_topics')
    @patch('app.core.openai_client.OpenAIClient.generate_script')
    @patch('app.utils.sheets_utils.SheetsUtils.update_row')
    def test_process_pending_topics_update_error(self, mock_update_row, mock_generate_script, mock_get_pending_topics):
        """스프레드시트 업데이트 에러 처리 테스트"""
        # Mock 설정
        mock_get_pending_topics.return_value = [self.mock_topic_data]
        mock_generate_script.return_value = "테스트 스크립트"
        mock_update_row.side_effect = HttpError(
            resp=MagicMock(status=500),
            content=b'Internal Server Error'
        )

        # 테스트 실행 및 검증
        with self.assertRaises(ValueError) as context:
            self.content_generator.process_pending_topics()
        
        self.assertIn("Failed to update row", str(context.exception))

    @patch('app.utils.sheets_utils.SheetsUtils.append_row')
    def test_add_topic_error(self, mock_append_row):
        """주제 추가 에러 처리 테스트"""
        # Mock 설정 - Sheets API 에러 발생
        mock_append_row.side_effect = HttpError(
            resp=MagicMock(status=500),
            content=b'Internal Server Error'
        )

        # 테스트 실행 및 검증
        with self.assertRaises(ValueError) as context:
            self.content_generator.add_topic("새로운 주제")
        
        self.assertIn("Failed to append row", str(context.exception))

if __name__ == '__main__':
    unittest.main() 