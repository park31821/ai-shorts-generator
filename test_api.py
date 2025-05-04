from app.core.content_generator import ContentGenerator
from app.utils.sheets_utils import SheetsUtils

def test_sheets_integration():
    sheets_utils = SheetsUtils()
    generator = ContentGenerator()
    
    # 1. 시트의 현재 상태 확인
    print("\n1. 현재 시트 상태 확인")
    initial_topics = sheets_utils.get_pending_topics()
    print(f"처리 대기 중인 주제 수: {len(initial_topics)}")
    
    if len(initial_topics) > 0:
        # 2. 주제 처리
        print("\n2. 주제 처리 시작")
        generator.process_pending_topics()
        
        # 3. 처리 후 시트 상태 확인
        print("\n3. 주제 처리 후 시트 상태 확인")
        final_topics = sheets_utils.get_pending_topics()
        print(f"남은 처리 대기 주제 수: {len(final_topics)}")
    else:
        print("\n처리할 주제가 없습니다.")

if __name__ == "__main__":
    test_sheets_integration() 