from notion_client import Client
from app.config import get_settings
from typing import Dict, Any

class NotionClient:
    def __init__(self):
        settings = get_settings()
        self.client = Client(auth=settings.notion_api_key)
        self.database_id = settings.notion_database_id

    async def get_content(self, content_id: str) -> Dict[str, Any]:
        try:
            response = self.client.pages.retrieve(page_id=content_id)
            return {
                "title": response["properties"]["Title"]["title"][0]["text"]["content"],
                "content": response["properties"]["Content"]["rich_text"][0]["text"]["content"],
                "tags": [tag["name"] for tag in response["properties"]["Tags"]["multi_select"]],
                "created_time": response["created_time"]
            }
        except Exception as e:
            raise Exception(f"Failed to fetch content from Notion: {str(e)}")

    async def list_contents(self) -> list:
        try:
            response = self.client.databases.query(
                database_id=self.database_id,
                sorts=[{
                    "property": "Created time",
                    "direction": "descending"
                }]
            )
            return response["results"]
        except Exception as e:
            raise Exception(f"Failed to list contents from Notion: {str(e)}") 