from app.utils.sheets_utils import SheetsUtils, TopicData
from app.core.openai_client import OpenAIClient
from typing import Dict, Any

class ContentGenerator:
    """콘텐츠 생성을 관리하는 클래스"""
    
    def __init__(self):
        """ContentGenerator 인스턴스를 초기화합니다."""
        self.sheets_utils = SheetsUtils()
        self.openai_client = OpenAIClient()

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
                
                # Update the spreadsheet
                self.sheets_utils.update_row(topic_data, script)
                
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