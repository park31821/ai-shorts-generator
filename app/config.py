from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    notion_api_key: str = os.getenv("NOTION_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")
    
    # Google Sheets
    google_sheets_credentials: str = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "")
    
    # Application Settings
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    port: int = int(os.getenv("PORT", "8000"))
    
    # Notion Database IDs
    notion_database_id: str = os.getenv("NOTION_DATABASE_ID", "")
    
    # Google Sheets
    spreadsheet_id: str = os.getenv("SPREADSHEET_ID", "")
    worksheet_name: str = os.getenv("WORKSHEET_NAME", "Sheet1")
    
    # YouTube Settings
    youtube_channel_id: str = os.getenv("YOUTUBE_CHANNEL_ID", "")
    youtube_playlist_id: str = os.getenv("YOUTUBE_PLAYLIST_ID", "")
    
    # Video Generation Settings
    video_width: int = int(os.getenv("VIDEO_WIDTH", "1080"))
    video_height: int = int(os.getenv("VIDEO_HEIGHT", "1920"))
    fps: int = int(os.getenv("FPS", "30"))

    # OpenAI Prompt Template
    openai_prompt_template: str = """
    당신은 유튜브 쇼츠용 스크립트를 작성하는 전문 작가입니다.
    주제: {title}

    다음 가이드라인에 따라 스크립트를 작성해주세요:

    1. 형식
    - 1분 영상 분량(250-300자)
    - 문장은 짧고 명확하게
    - 구어체로 작성 (예: "~했어요", "~이에요")
    - 아래의 섹션을 포함해서 작성해주세요:
    [INTRO]
    - "여러분"은 쓰지 않습니다.
    [BODY]
    [OUTRO]
    - (5초) 간단한 마무리

    2. 내용
    - 주제에 대한 흥미로운 역사나 과학적 사실
    - 검증 가능한 실제 사실만 포함
    - 흥미로운 숫자나 데이터를 자연스럽게 녹여서 설명 (최소 3개)
    - 시청자가 "오늘 새로운 걸 배웠다"고 느낄 수 있는 내용
    - 나열식 설명("첫째", "둘째" 등)은 피하고 자연스러운 스토리텔링으로 전개

    3. 톤앤매너
    - 친근하고 자연스러운 설명
    - 전문적이지만 어렵지 않게
    - 호기심을 자극하는 도입부
    - 핵심 포인트로 마무리

    위 가이드라인을 모두 충족하는 스크립트를 작성해주세요.
    각 섹션([INTRO], [BODY], [OUTRO])을 구분해서 작성해주세요.
    """

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings() 