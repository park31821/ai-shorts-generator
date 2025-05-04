from elevenlabs import generate, set_api_key, Voice, VoiceSettings
from app.config import get_settings
import os
import tempfile

class ElevenLabsClient:
    def __init__(self):
        settings = get_settings()
        set_api_key(settings.elevenlabs_api_key)
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # 기본 음성 ID (Rachel)

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
                use_speaker_boost=True
            )

            # 음성 생성
            audio = generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id or self.default_voice_id,
                    settings=voice_settings
                )
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