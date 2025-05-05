from elevenlabs import generate, set_api_key, Voice, VoiceSettings
from app.config import get_settings
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

class ElevenLabsClient:
    def __init__(self):
        settings = get_settings()
        set_api_key(settings.elevenlabs_api_key)
        self.default_voice_id = "Xb7hH8MSUJpSbSDYk0k2"  # 기본 음성 ID (Rachel)

    def generate_audio(self, text: str, output_path: str, voice_id: str = None) -> None:
        """텍스트를 음성으로 변환하여 파일로 저장합니다.

        Args:
            text: 변환할 텍스트
            output_path: 저장할 파일 경로
            voice_id: 사용할 음성 ID (기본값: None)

        Raises:
            Exception: 음성 생성 실패 시
        """
        try:
            logger.info(f"음성 생성 시작 - 텍스트 길이: {len(text)}")
            
            # 음성 설정
            voice_settings = VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True,
                speed=1.15  # 음성 속도 설정
            )

            # 음성 생성
            logger.info("ElevenLabs API 호출")
            audio = generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id or self.default_voice_id,
                    settings=voice_settings
                ),
                model="eleven_multilingual_v2"
            )

            # 오디오 파일 저장
            logger.info(f"음성 파일 저장: {output_path}")
            with open(output_path, "wb") as f:
                f.write(audio)
            
            logger.info("음성 파일 생성 완료")

        except Exception as e:
            logger.error(f"음성 생성 실패: {str(e)}")
            raise Exception(f"Failed to generate voice with ElevenLabs: {str(e)}")

    async def generate_voice(self, text: str, voice_id: str = None) -> str:
        try:
            # 임시 파일 생성
            temp_dir = tempfile.gettempdir()
            output_file = os.path.join(temp_dir, f"voice_{hash(text)}.mp3")

            # 음성 설정
            voice_settings = VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True,
                speed=1.15  # 음성 속도 설정
            )

            # 음성 생성
            audio = generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id or self.default_voice_id,
                    settings=voice_settings
                ),
                model="eleven_multilingual_v2"
            )

            # 오디오 파일 저장
            with open(output_file, "wb") as f:
                f.write(audio)

            return output_file

        except Exception as e:
            raise Exception(f"Failed to generate voice with ElevenLabs: {str(e)}")

    async def list_voices(self) -> list:
        try:
            from elevenlabs import voices
            available_voices = voices()
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": voice.category
                }
                for voice in available_voices
            ]
        except Exception as e:
            raise Exception(f"Failed to list voices from ElevenLabs: {str(e)}") 