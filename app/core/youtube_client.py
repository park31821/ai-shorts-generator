from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from app.config import get_settings
import json
import os

class YouTubeClient:
    def __init__(self):
        settings = get_settings()
        credentials_dict = json.loads(settings.google_sheets_credentials)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_dict,
            scopes=['https://www.googleapis.com/auth/youtube.upload']
        )
        self.youtube = build('youtube', 'v3', credentials=credentials)
        self.channel_id = settings.youtube_channel_id
        self.playlist_id = settings.youtube_playlist_id

    async def upload_video(self, video_file: str, title: str = None, description: str = None, tags: list = None) -> str:
        try:
            # 비디오 메타데이터 설정
            body = {
                'snippet': {
                    'title': title or 'AI Generated Shorts',
                    'description': description or 'Generated using AI Shorts Generator',
                    'tags': tags or [],
                    'categoryId': '22'  # People & Blogs
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False
                }
            }

            # 비디오 파일 업로드
            media = MediaFileUpload(
                video_file,
                mimetype='video/mp4',
                resumable=True
            )

            # 업로드 요청
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            # 업로드 실행
            response = request.execute()

            # 플레이리스트에 추가
            if self.playlist_id:
                self.youtube.playlistItems().insert(
                    part='snippet',
                    body={
                        'snippet': {
                            'playlistId': self.playlist_id,
                            'resourceId': {
                                'kind': 'youtube#video',
                                'videoId': response['id']
                            }
                        }
                    }
                ).execute()

            return f"https://youtube.com/watch?v={response['id']}"

        except Exception as e:
            raise Exception(f"Failed to upload video to YouTube: {str(e)}")

    async def get_video_status(self, video_id: str) -> dict:
        try:
            response = self.youtube.videos().list(
                part='status',
                id=video_id
            ).execute()

            if not response['items']:
                raise Exception(f"Video {video_id} not found")

            return response['items'][0]['status']

        except Exception as e:
            raise Exception(f"Failed to get video status from YouTube: {str(e)}") 