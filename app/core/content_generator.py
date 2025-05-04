from app.utils.sheets_utils import SheetsUtils, TopicData
from app.core.openai_client import OpenAIClient
from typing import Dict, Any
import re

class ContentGenerator:
    """콘텐츠 생성을 관리하는 클래스"""
    
    def __init__(self):
        """ContentGenerator 인스턴스를 초기화합니다."""
        self.sheets_utils = SheetsUtils()
        self.openai_client = OpenAIClient()

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

    def process_pending_topics(self) -> None:
        """대기 중인 모든 주제를 처리하고 스크립트를 생성합니다."""
        pending_topics = self.sheets_utils.get_pending_topics()
        
        for topic_data in pending_topics:
            try:
                # Generate script using OpenAI
                content_data = {
                    'title': topic_data.topic,
                    'content': '',  # Not needed for our current prompt
                    'tags': []  # Not needed for our current prompt
                }
                script = self.openai_client.generate_script(content_data)
                
                # Remove section tags from the script
                cleaned_script = self._remove_section_tags(script)
                
                # Update the spreadsheet
                self.sheets_utils.update_row(topic_data, cleaned_script)
                
            except Exception as e:
                print(f"Error processing topic {topic_data.topic}: {str(e)}")
                continue

    def add_topic(self, topic: str) -> None:
        """새로운 주제를 스프레드시트에 추가합니다.

        Args:
            topic: 추가할 주제
        """
        try:
            self.sheets_utils.append_row(topic)
        except Exception as e:
            print(f"Error adding topic '{topic}': {str(e)}") 