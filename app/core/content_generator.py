from app.utils.sheets_utils import SheetsUtils
from app.core.openai_client import OpenAIClient
from typing import Dict, Any

class ContentGenerator:
    def __init__(self):
        self.sheets_utils = SheetsUtils()
        self.openai_client = OpenAIClient()

    def process_pending_topics(self) -> None:
        """Process all pending topics and generate scripts."""
        pending_topics = self.sheets_utils.get_pending_topics()
        
        for topic_data in pending_topics:
            try:
                # Generate script using OpenAI
                content_data = {
                    'title': topic_data['topic'],
                    'content': '',  # Not needed for our current prompt
                    'tags': []  # Not needed for our current prompt
                }
                script = self.openai_client.generate_script(content_data)
                
                # Update the spreadsheet
                self.sheets_utils.update_row(
                    row=topic_data['row'],
                    script=script,
                    data_idx=topic_data['data_idx'],
                    script_idx=topic_data['script_idx'],
                    voice_idx=topic_data['voice_idx'],
                    video_idx=topic_data['video_idx'],
                    video_link_idx=topic_data['video_link_idx'],
                    status_idx=topic_data['status_idx']
                )
            except Exception as e:
                print(f"Error processing topic {topic_data['topic']}: {str(e)}")
                continue

    def add_topic(self, topic: str) -> None:
        """Add a new topic to the spreadsheet with Data column set to '✅'."""
        try:
            self.sheets_utils.append_row(topic)
        except Exception as e:
            print(f"Error adding topic '{topic}': {str(e)}") 