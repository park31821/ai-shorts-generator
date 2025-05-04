from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from app.core.video_generator import VideoGenerator
from app.core.notion_client import NotionClient
from app.core.google_sheets import GoogleSheetsClient
from app.core.openai_client import OpenAIClient
from app.core.elevenlabs_client import ElevenLabsClient
from app.core.youtube_client import YouTubeClient
from app.core.content_generator import ContentGenerator

router = APIRouter()

class GenerateRequest(BaseModel):
    content_id: str
    use_notion: bool = True
    use_google_sheets: bool = False
    voice_id: Optional[str] = None
    style: Optional[str] = None

class StatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    message: Optional[str] = None

@router.post("/generate")
async def generate_shorts(request: GenerateRequest, background_tasks: BackgroundTasks):
    try:
        # 콘텐츠 데이터 가져오기
        content_data = None
        if request.use_notion:
            notion_client = NotionClient()
            content_data = await notion_client.get_content(request.content_id)
        elif request.use_google_sheets:
            sheets_client = GoogleSheetsClient()
            content_data = await sheets_client.get_content(request.content_id)
        
        if not content_data:
            raise HTTPException(status_code=404, detail="Content not found")

        # 스크립트 생성
        openai_client = OpenAIClient()
        script = await openai_client.generate_script(content_data)

        # 음성 합성
        elevenlabs_client = ElevenLabsClient()
        audio_file = await elevenlabs_client.generate_voice(script, request.voice_id)

        # 영상 생성
        video_generator = VideoGenerator()
        video_file = await video_generator.generate_video(audio_file, content_data)

        # YouTube 업로드
        youtube_client = YouTubeClient()
        video_url = await youtube_client.upload_video(video_file)

        return {"status": "success", "video_url": video_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    # 작업 상태 조회 로직 구현
    return StatusResponse(
        job_id=job_id,
        status="completed",
        progress=100.0
    )

@router.get("/history")
async def get_history():
    # 생성된 영상 목록 조회 로직 구현
    return []

@router.post("/process-topics")
async def process_topics():
    """Process all pending topics and generate scripts."""
    try:
        generator = ContentGenerator()
        await generator.process_pending_topics()
        return {"message": "Topics processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 