import firebase_admin
from firebase_admin import credentials, firestore
import json

# Firebase 서비스 계정 키 파일 경로
cred = credentials.Certificate('/Users/wonjoun/development/Zigle/etc../zigle-39981-firebase-adminsdk-d53fz-e9a25fa7d3.json')

# Firebase 앱 초기화
firebase_admin.initialize_app(cred)

# Firestore 클라이언트 가져오기
db = firestore.client()

# JSON 데이터를 Firestore에 저장 (100개씩 나누어 배치 처리)
def save_json_to_firestore_in_batches(json_file_path, batch_size=100):
    # JSON 파일 열기
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_count = len(data)
    batch = db.batch()  # Firestore의 배치 처리
    count = 0  # 처리된 문서 수

    # 데이터를 Firestore에 배치로 저장
    for item in data:
        try:
            doc_ref = db.collection("websites").document()  # 자동 문서 ID 생성
            batch.set(doc_ref, {
                "url": item["url"],
                "title": item["title"],
                "most_common_words": item["most_common_words"]
            })
            count += 1

            # 배치가 100개에 도달하면 커밋
            if count % batch_size == 0:
                batch.commit()
                print(f"{count} documents saved in batch.")
                batch = db.batch()  # 새로운 배치 시작

        except Exception as e:
            print(f"Error saving data for {item['url']}: {e}")

    # 남은 문서 처리
    if count % batch_size != 0:
        batch.commit()
        print(f"Remaining {count % batch_size} documents saved.")

    print(f"Total {count} documents processed out of {total_count}")

# JSON 파일 경로
json_file_path = '/Users/wonjoun/development/Zigle/backup/crawl_data.backup 복사본.json'

# JSON 데이터를 Firestore에 저장 (100개씩 나누어 배치 처리)
save_json_to_firestore_in_batches(json_file_path)