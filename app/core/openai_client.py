from openai import OpenAI
from app.config import get_settings
from typing import Dict, Any

class OpenAIClient:
    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_script(self, content_data: Dict[str, Any]) -> str:
        try:
            settings = get_settings()
            # 프롬프트 구성
            prompt = settings.openai_prompt_template.format(
                title=content_data.get('title', '')
            )

            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a professional YouTube shorts script writer. Always write in Korean and focus on delivering educational content in an engaging way. Use [INTRO], [BODY], and [OUTRO] section markers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise Exception(f"Failed to generate script with OpenAI: {str(e)}")

    def generate_hashtags(self, content_data: Dict[str, Any]) -> list:
        try:
            prompt = f"""
            다음 내용을 바탕으로 유튜브 쇼츠에 적합한 해시태그 5-10개를 생성해주세요.
            
            제목: {content_data.get('title', '')}
            내용: {content_data.get('content', '')}
            기존 태그: {', '.join(content_data.get('tags', []))}
            """

            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a social media expert specializing in hashtag generation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )

            # 해시태그 추출 및 정리
            hashtags = response.choices[0].message.content.strip().split('\n')
            hashtags = [tag.strip() for tag in hashtags if tag.strip()]
            hashtags = [tag if tag.startswith('#') else f'#{tag}' for tag in hashtags]

            return hashtags

        except Exception as e:
            raise Exception(f"Failed to generate hashtags with OpenAI: {str(e)}") 