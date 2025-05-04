from app.core.content_generator import ContentGenerator
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """콘텐츠 생성 프로세스를 실행합니다."""
    try:
        logger.info("콘텐츠 생성 프로세스 시작")
        
        # ContentGenerator 인스턴스 생성
        generator = ContentGenerator()
        
        # 대기 중인 주제 처리
        generator.process_pending_topics()
        
        logger.info("콘텐츠 생성 프로세스 완료")
        
    except Exception as e:
        logger.error(f"오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    main() 