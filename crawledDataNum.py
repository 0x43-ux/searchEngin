import firebase_admin
from firebase_admin import credentials, firestore

# Firebase 서비스 계정 키 파일 경로
cred = credentials.Certificate('/Users/wonjoun/development/Zigle/etc../zigle-39981-firebase-adminsdk-d53fz-e9a25fa7d3.json')

# Firebase 앱 초기화
firebase_admin.initialize_app(cred)

# Firestore 클라이언트 가져오기
db = firestore.client()

# 특정 컬렉션의 문서 수를 세는 함수
def count_documents_in_collection(collection_name):
    # Firestore에서 컬렉션의 모든 문서 가져오기
    docs = db.collection(collection_name).stream()
    
    # 문서 개수 세기
    count = sum(1 for _ in docs)
    
    print(f"Total number of documents in '{collection_name}' collection: {count}")
    return count

# 'websites' 컬렉션의 문서 개수 확인
collection_name = 'websites'
count_documents_in_collection(collection_name)