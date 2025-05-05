import unittest
from unittest.mock import patch, MagicMock
from app.core.content_generator import ContentGenerator
from app.utils.sheets_utils import TopicData
from googleapiclient.errors import HttpError
from openai import OpenAIError

class TestContentGenerator(unittest.TestCase):
    """ContentGenerator 테스트 클래스"""

    def setUp(self):
        """테스트를 위한 기본 설정"""
        self.generator = ContentGenerator()
        
        # 테스트용 TopicData 생성
        self.topic_data = TopicData(
            row=2,
            topic="테스트 주제",
            script="",  # 스크립트 생성 테스트를 위해 빈 문자열로 설정
            voice="",
            video="",
            video_link="",
            data_status="✅",
            status="",
            column_indices={
                'Topic': 0,
                'Data': 1,
                'Script': 2,
                'Voice': 3,
                'Video': 4,
                'Video Link': 5,
                'Status': 6
            }
        )

    @patch('app.utils.sheets_utils.SheetsUtils.get_pending_topics')
    @patch('app.core.openai_client.OpenAIClient.generate_script')
    @patch('app.utils.sheets_utils.SheetsUtils.update_row')
    def test_process_pending_topics(self, mock_update_row, mock_generate_script, mock_get_topics):
        """process_pending_topics 메서드 테스트"""
        # Mock 설정
        mock_get_topics.return_value = [self.topic_data]
        mock_generate_script.return_value = "테스트 스크립트"
        mock_update_row.return_value = None

        # 테스트 실행
        self.generator.process_pending_topics()

        # 검증
        mock_get_topics.assert_called_once()
        mock_generate_script.assert_called_once_with({
            'title': self.topic_data.topic,
            'content': '',
            'tags': []
        })
        mock_update_row.assert_called_once()

    @patch('app.utils.sheets_utils.SheetsUtils.append_row')
    def test_add_topic(self, mock_append_row):
        """add_topic 메서드 테스트"""
        # 테스트 실행
        self.generator.add_topic("새로운 주제")

        # 검증
        mock_append_row.assert_called_once_with("새로운 주제")

    @patch('app.utils.sheets_utils.SheetsUtils.get_pending_topics')
    def test_process_pending_topics_sheets_error(self, mock_get_topics):
        """Sheets API 에러 처리 테스트"""
        # Mock 설정 - Sheets API 에러 발생
        mock_get_topics.side_effect = HttpError(
            resp=MagicMock(status=500),
            content=b'Internal Server Error'
        )

        # 테스트 실행 및 검증
        with self.assertRaises(ValueError) as context:
            self.generator.process_pending_topics()
        
        self.assertIn("Failed to get pending topics", str(context.exception))

    @patch('app.utils.sheets_utils.SheetsUtils.get_pending_topics')
    @patch('app.core.openai_client.OpenAIClient.generate_script')
    def test_process_pending_topics_openai_error(self, mock_generate_script, mock_get_topics):
        """OpenAI API 에러 처리 테스트"""
        # Mock 설정
        mock_get_topics.return_value = [self.topic_data]
        mock_generate_script.side_effect = OpenAIError("API Error")

        # 테스트 실행 및 검증
        with self.assertRaises(Exception) as context:
            self.generator.process_pending_topics()
        
        self.assertIn("Failed to generate script", str(context.exception))

    @patch('app.utils.sheets_utils.SheetsUtils.get_pending_topics')
    @patch('app.core.openai_client.OpenAIClient.generate_script')
    @patch('app.utils.sheets_utils.SheetsUtils.update_row')
    def test_process_pending_topics_update_error(self, mock_update_row, mock_generate_script, mock_get_topics):
        """스프레드시트 업데이트 에러 처리 테스트"""
        # Mock 설정
        mock_get_topics.return_value = [self.topic_data]
        mock_generate_script.return_value = "테스트 스크립트"
        mock_update_row.side_effect = HttpError(MagicMock(), b"API Error")

        # 테스트 실행 및 검증
        with self.assertRaises(ValueError) as context:
            self.generator.process_pending_topics()
        
        self.assertIn("Failed to update row", str(context.exception))

    @patch('app.utils.sheets_utils.SheetsUtils.append_row')
    def test_add_topic_error(self, mock_append_row):
        """주제 추가 에러 처리 테스트"""
        # Mock 설정
        mock_append_row.side_effect = HttpError(MagicMock(), b"API Error")

        # 테스트 실행 및 검증
        with self.assertRaises(ValueError) as context:
            self.generator.add_topic("새로운 주제")
        
        self.assertIn("Failed to append row", str(context.exception))

    @patch('app.utils.sheets_utils.SheetsUtils.get_pending_topics')
    @patch('app.core.elevenlabs_client.ElevenLabsClient.generate_audio')
    @patch('app.utils.sheets_utils.SheetsUtils.update_voice_status')
    def test_process_pending_topics_voice_generation(self, mock_update_voice, mock_generate_audio, mock_get_topics):
        """음성 생성 프로세스 테스트"""
        # Mock 설정
        topic_data = TopicData(
            row=2,
            topic="테스트 주제",
            script="테스트 스크립트입니다.",  # 스크립트가 있는 상태
            voice="",
            video="",
            video_link="",
            data_status="✅",
            status="",
            column_indices={
                'Topic': 0,
                'Data': 1,
                'Script': 2,
                'Voice': 3,
                'Video': 4,
                'Video Link': 5,
                'Status': 6
            }
        )
        mock_get_topics.return_value = [topic_data]
        mock_generate_audio.return_value = None
        mock_update_voice.return_value = None

        # 테스트 실행
        self.generator.process_pending_topics()

        # 검증
        mock_get_topics.assert_called_once()
        mock_generate_audio.assert_called_once()
        mock_update_voice.assert_called_once_with(
            topic_data,
            "✅",
            "Voice generated"
        )

    @patch('app.utils.sheets_utils.SheetsUtils.get_pending_topics')
    @patch('app.core.elevenlabs_client.ElevenLabsClient.generate_audio')
    def test_process_pending_topics_voice_generation_error(self, mock_generate_audio, mock_get_topics):
        """음성 생성 실패 테스트"""
        # Mock 설정
        topic_data = TopicData(
            row=2,
            topic="테스트 주제",
            script="테스트 스크립트입니다.",  # 스크립트가 있는 상태
            voice="",
            video="",
            video_link="",
            data_status="✅",
            status="",
            column_indices={
                'Topic': 0,
                'Data': 1,
                'Script': 2,
                'Voice': 3,
                'Video': 4,
                'Video Link': 5,
                'Status': 6
            }
        )
        mock_get_topics.return_value = [topic_data]
        mock_generate_audio.side_effect = Exception("음성 생성 실패")

        # 테스트 실행 및 검증
        with self.assertRaises(Exception) as context:
            self.generator.process_pending_topics()
        
        self.assertEqual(str(context.exception), "Failed to generate voice: 음성 생성 실패")

    @patch('app.utils.sheets_utils.SheetsUtils.get_pending_topics')
    @patch('app.utils.sheets_utils.SheetsUtils.reset_voice_status')
    def test_reset_voice_status(self, mock_reset_voice, mock_get_topics):
        """음성 상태 초기화 테스트"""
        # Mock 설정
        topic_data = TopicData(
            row=2,
            topic="테스트 주제",
            script="테스트 스크립트입니다.",  # 스크립트가 있는 상태
            voice="",
            video="",
            video_link="",
            data_status="✅",
            status="",
            column_indices={
                'Topic': 0,
                'Data': 1,
                'Script': 2,
                'Voice': 3,
                'Video': 4,
                'Video Link': 5,
                'Status': 6
            }
        )
        mock_get_topics.return_value = [topic_data]
        mock_reset_voice.return_value = None

        # 테스트 실행
        self.generator.reset_voice_status()

        # 검증
        mock_get_topics.assert_called_once()
        mock_reset_voice.assert_called_once_with(topic_data)

    @patch('app.utils.sheets_utils.SheetsUtils.get_pending_topics')
    @patch('app.utils.sheets_utils.SheetsUtils.reset_voice_status')
    def test_reset_voice_status_error(self, mock_reset_voice, mock_get_topics):
        """음성 상태 초기화 실패 테스트"""
        # Mock 설정
        topic_data = TopicData(
            row=2,
            topic="테스트 주제",
            script="테스트 스크립트입니다.",  # 스크립트가 있는 상태
            voice="",
            video="",
            video_link="",
            data_status="✅",
            status="",
            column_indices={
                'Topic': 0,
                'Data': 1,
                'Script': 2,
                'Voice': 3,
                'Video': 4,
                'Video Link': 5,
                'Status': 6
            }
        )
        mock_get_topics.return_value = [topic_data]
        mock_reset_voice.side_effect = HttpError(MagicMock(), b"API Error")

        # 테스트 실행 및 검증
        with self.assertRaises(Exception) as context:
            self.generator.reset_voice_status()
        
        self.assertIn("Failed to reset voice status", str(context.exception))

    @patch('app.utils.sheets_utils.SheetsUtils.get_pending_topics')
    def test_process_pending_topics_no_topics(self, mock_get_topics):
        """처리할 주제가 없는 경우 테스트"""
        # Mock 설정
        mock_get_topics.return_value = []

        # 테스트 실행
        self.generator.process_pending_topics()

        # 검증
        mock_get_topics.assert_called_once()

    @patch('app.utils.sheets_utils.SheetsUtils.get_pending_topics')
    @patch('app.core.elevenlabs_client.ElevenLabsClient.generate_audio')
    def test_process_pending_topics_invalid_conditions(self, mock_generate_audio, mock_get_topics):
        """음성 생성 조건이 맞지 않는 경우 테스트"""
        # Mock 설정
        topic_data = TopicData(
            row=2,
            topic="테스트 주제",
            script="테스트 스크립트입니다.",
            voice="✅",  # 이미 음성이 생성된 경우
            video="",
            video_link="",
            data_status="✅",
            status="",
            column_indices={
                'Topic': 0,
                'Data': 1,
                'Script': 2,
                'Voice': 3,
                'Video': 4,
                'Video Link': 5,
                'Status': 6
            }
        )
        mock_get_topics.return_value = [topic_data]

        # 테스트 실행
        self.generator.process_pending_topics()

        # 검증
        mock_get_topics.assert_called_once()
        mock_generate_audio.assert_not_called()

if __name__ == '__main__':
    unittest.main() 