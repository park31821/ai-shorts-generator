from app.utils.sheets_utils import SheetsUtils, TopicData
from app.core.openai_client import OpenAIClient
from app.core.elevenlabs_client import ElevenLabsClient
from typing import Dict, Any
import re
import os
import logging
from googleapiclient.errors import HttpError
from openai import OpenAIError

# 로깅 설정
logger = logging.getLogger(__name__)

class ContentGenerator:
    """콘텐츠 생성을 관리하는 클래스"""
    
    def __init__(self):
        """ContentGenerator 인스턴스를 초기화합니다."""
        self.sheets_utils = SheetsUtils()
        self.openai_client = OpenAIClient()
        self.elevenlabs_client = ElevenLabsClient()
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)

    def _remove_section_tags(self, script: str) -> str:
        """스크립트에서 섹션 태그를 제거합니다.

        Args:
            script: 원본 스크립트

        Returns:
            str: 섹션 태그가 제거된 스크립트
        """
        # [INTRO], [BODY], [OUTRO] 태그 제거
        script = re.sub(r'\[INTRO\]|\[BODY\]|\[OUTRO\]', '', script)
        # 빈 줄 제거 및 정리
        script = re.sub(r'\n\s*\n', '\n', script)
        return script.strip()

    def _generate_voice(self, topic_data: TopicData) -> None:
        """주제에 대한 음성을 생성합니다.

        Args:
            topic_data: 주제 데이터

        Raises:
            Exception: 음성 생성에 실패한 경우
        """
        try:
            logger.info(f"음성 생성 시작: {topic_data.topic}")
            
            # 주제별 디렉토리 생성
            topic_dir = os.path.join(self.data_dir, re.sub(r'[^\w\s-]', '', topic_data.topic).strip().replace(' ', '_'))
            os.makedirs(topic_dir, exist_ok=True)
            logger.info(f"디렉토리 생성: {topic_dir}")

            # 음성 파일 경로 설정
            voice_file = os.path.join(topic_dir, "voice.mp3")
            logger.info(f"음성 파일 경로: {voice_file}")

            # 음성 생성
            logger.info("ElevenLabs API 호출 시작")
            self.elevenlabs_client.generate_audio(
                text=topic_data.script,
                output_path=voice_file
            )
            logger.info("음성 파일 생성 완료")

            # 스프레드시트 업데이트
            logger.info("스프레드시트 업데이트 시작")
            self.sheets_utils.update_voice_status(topic_data, "✅", "Voice generated")
            logger.info("스프레드시트 업데이트 완료")

        except Exception as e:
            logger.error(f"음성 생성 실패: {str(e)}")
            raise Exception(f"Failed to generate voice: {str(e)}")

    def process_pending_topics(self) -> None:
        """대기 중인 모든 주제를 처리하고 스크립트를 생성합니다.

        Raises:
            ValueError: Google Sheets API 호출 실패 시
            Exception: OpenAI API 호출 실패 시
        """
        try:
            pending_topics = self.sheets_utils.get_pending_topics()
            logger.info(f"처리할 주제 수: {len(pending_topics)}")
        except HttpError as e:
            logger.error(f"Failed to get pending topics: {str(e)}")
            raise ValueError(f"Failed to get pending topics: {str(e)}")
        
        for topic_data in pending_topics:
            try:
                logger.info(f"주제 처리 시작: {topic_data.topic}")
                logger.info(f"현재 상태 - Script: {bool(topic_data.script)}, Data: {topic_data.data_status}, Voice: {topic_data.voice}")

                # 스크립트가 없고 Data가 ✅인 경우 스크립트 생성
                if not topic_data.script and topic_data.data_status == "✅":
                    logger.info("스크립트 생성 시작")
                    content_data = {
                        'title': topic_data.topic,
                        'content': '',
                        'tags': []
                    }
                    try:
                        script = self.openai_client.generate_script(content_data)
                        cleaned_script = self._remove_section_tags(script)
                        self.sheets_utils.update_row(topic_data, cleaned_script)
                        logger.info("스크립트 생성 및 업데이트 완료")
                    except OpenAIError as e:
                        logger.error(f"Failed to generate script: {str(e)}")
                        raise Exception(f"Failed to generate script: {str(e)}")
                    except HttpError as e:
                        logger.error(f"Failed to update row: {str(e)}")
                        raise ValueError(f"Failed to update row: {str(e)}")

                # 스크립트가 있고 Data가 ✅이고 Voice가 비어있는 경우 음성 생성
                elif topic_data.script and topic_data.data_status == "✅" and not topic_data.voice:
                    logger.info("음성 생성 조건 충족")
                    self._generate_voice(topic_data)
                else:
                    logger.info("처리 조건 미충족")
                
            except Exception as e:
                logger.error(f"Error processing topic {topic_data.topic}: {str(e)}")
                raise

    def add_topic(self, topic: str) -> None:
        """새로운 주제를 스프레드시트에 추가합니다.

        Args:
            topic: 추가할 주제

        Raises:
            ValueError: Google Sheets API 호출 실패 시
        """
        try:
            self.sheets_utils.append_row(topic)
        except HttpError as e:
            logger.error(f"Failed to append row: {str(e)}")
            raise ValueError(f"Failed to append row: {str(e)}")

    def reset_voice_status(self) -> None:
        """모든 주제의 음성 생성 상태를 초기화합니다.
        
        Raises:
            Exception: 음성 상태 초기화 실패 시
        """
        try:
            logger.info("음성 상태 초기화 시작")
            pending_topics = self.sheets_utils.get_pending_topics()
            
            for topic_data in pending_topics:
                if topic_data.script and topic_data.data_status == "✅":
                    logger.info(f"주제 음성 상태 초기화: {topic_data.topic}")
                    try:
                        self.sheets_utils.reset_voice_status(topic_data)
                    except HttpError as e:
                        logger.error(f"Failed to reset voice status: {str(e)}")
                        raise Exception(f"Failed to reset voice status: {str(e)}")
            
            logger.info("음성 상태 초기화 완료")
            
        except Exception as e:
            logger.error(f"음성 상태 초기화 실패: {str(e)}")
            raise 