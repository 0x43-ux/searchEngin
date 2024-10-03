import firebase_admin
from firebase_admin import credentials, firestore
import json

# Firebase 서비스 계정 키 파일 경로
cred = credentials.Certificate('/Users/wonjoun/development/Zigle/etc../zigle-39981-firebase-adminsdk-d53fz-e9a25fa7d3.json')

# Firebase 앱 초기화
firebase_admin.initialize_app(cred)

# Firestore 클라이언트 가져오기
db = firestore.client()

# JSON 파일을 읽어서 Firestore에 저장하는 함수
def save_json_to_firestore(json_file_path):
    # JSON 파일 열기
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)  # JSON 데이터 파싱

    # Firestore에 저장하기
    for item in data:
        doc_ref = db.collection("websites").document()  # 자동으로 문서 ID 생성
        doc_ref.set({
            "url": item["url"],  # URL을 필드로 저장
            "title": item["title"],
            "most_common_words": item["most_common_words"]
        })
        print(f"Data for {item['url']} saved successfully.")

# 예시 JSON 파일 경로
json_file_path = 'crawl_data.backup 복사본.json'

# JSON 파일 Firestore에 저장
save_json_to_firestore(json_file_path)