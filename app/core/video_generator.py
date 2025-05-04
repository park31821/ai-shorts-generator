import ffmpeg
import os
import tempfile
from app.config import get_settings
from typing import Dict, Any
import random
from PIL import Image, ImageDraw, ImageFont
import textwrap

class VideoGenerator:
    def __init__(self):
        settings = get_settings()
        self.width = settings.video_width
        self.height = settings.video_height
        self.fps = settings.fps

    async def generate_video(self, audio_file: str, content_data: Dict[str, Any]) -> str:
        try:
            # 임시 파일 생성
            temp_dir = tempfile.gettempdir()
            output_file = os.path.join(temp_dir, f"video_{hash(str(content_data))}.mp4")

            # 배경 이미지 생성
            background = self._create_background()
            background_path = os.path.join(temp_dir, "background.png")
            background.save(background_path)

            # 텍스트 오버레이 생성
            text_overlay = self._create_text_overlay(content_data)
            text_path = os.path.join(temp_dir, "text.png")
            text_overlay.save(text_path)

            # FFmpeg 명령어 구성
            stream = (
                ffmpeg
                .input(background_path, loop=1, t=self._get_audio_duration(audio_file))
                .filter('fps', fps=self.fps)
                .filter('scale', self.width, self.height)
                .overlay(
                    ffmpeg.input(text_path).filter('fade', 'in', 0.5).filter('fade', 'out', 0.5),
                    x='(W-w)/2',
                    y='(H-h)/2'
                )
                .output(
                    output_file,
                    acodec='aac',
                    audio_bitrate='192k',
                    vcodec='libx264',
                    video_bitrate='2500k',
                    preset='medium',
                    movflags='faststart'
                )
                .overwrite_output()
            )

            # 비디오 생성
            stream.run(capture_stdout=True, capture_stderr=True)

            # 임시 파일 정리
            os.remove(background_path)
            os.remove(text_path)

            return output_file

        except Exception as e:
            raise Exception(f"Failed to generate video: {str(e)}")

    def _create_background(self) -> Image.Image:
        # 랜덤 그라데이션 배경 생성
        image = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(image)

        # 랜덤 색상 선택
        color1 = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        color2 = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )

        # 그라데이션 그리기
        for y in range(self.height):
            r = int(color1[0] * (1 - y/self.height) + color2[0] * (y/self.height))
            g = int(color1[1] * (1 - y/self.height) + color2[1] * (y/self.height))
            b = int(color1[2] * (1 - y/self.height) + color2[2] * (y/self.height))
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        return image

    def _create_text_overlay(self, content_data: Dict[str, Any]) -> Image.Image:
        # 텍스트 오버레이 이미지 생성
        image = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # 폰트 설정
        try:
            font = ImageFont.truetype("Arial", 60)
        except:
            font = ImageFont.load_default()

        # 텍스트 줄바꿈
        title = content_data.get('title', '')
        wrapped_title = textwrap.fill(title, width=20)

        # 텍스트 그리기
        draw.text(
            (self.width/2, self.height/2),
            wrapped_title,
            font=font,
            fill=(255, 255, 255, 255),
            anchor="mm"
        )

        return image

    def _get_audio_duration(self, audio_file: str) -> float:
        # 오디오 파일 길이 가져오기
        probe = ffmpeg.probe(audio_file)
        return float(probe['format']['duration']) 