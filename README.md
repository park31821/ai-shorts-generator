# AI Shorts Generator

AI를 활용한 유튜브 쇼츠 콘텐츠 자동 생성 시스템입니다.

## 주요 기능

- Google Sheets와 연동하여 콘텐츠 주제 관리
- OpenAI를 활용한 스크립트 자동 생성
- ElevenLabs를 활용한 음성 생성
- Notion과 연동하여 콘텐츠 관리
- YouTube API를 통한 자동 업로드

## 기술 스택

- Python 3.9+
- FastAPI
- OpenAI API
- Google Sheets API
- ElevenLabs API
- Notion API
- YouTube API

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/yourusername/ai-shorts-generator.git
cd ai-shorts-generator
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 열어 필요한 API 키와 설정값을 입력
```

## 사용 방법

1. 서버 실행
```bash
uvicorn app.main:app --reload
```

2. API 엔드포인트
- `POST /api/process-topics`: Google Sheets의 주제를 처리하여 스크립트 생성

## 프로젝트 구조

```
ai-shorts-generator/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   ├── content_generator.py
│   │   ├── notion_client.py
│   │   ├── openai_client.py
│   │   └── youtube_client.py
│   ├── utils/
│   │   └── sheets_utils.py
│   └── main.py
├── tests/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## 라이선스

MIT License

## 기여 방법

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request 