import requests
from bs4 import BeautifulSoup
import json
import os
from collections import Counter
import re

# 파일 경로
links_json_file = 'links_to_crawl.json'
crawl_data_file = 'crawl_data.json'

# 크롤링된 데이터를 불러오기 (없으면 빈 리스트 생성)
def load_crawl_data():
    if os.path.exists(crawl_data_file):
        with open(crawl_data_file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("Warning: Crawl data JSON file is empty or corrupted, returning an empty list.")
                return []
    return []

# 크롤링된 데이터를 저장하는 함수
def save_crawl_data(crawl_data):
    with open(crawl_data_file, 'w', encoding='utf-8') as f:
        json.dump(crawl_data, f, ensure_ascii=False, indent=4)

# 크롤링할 링크들을 파일에서 하나씩 가져오기
def pop_link_from_file():
    if os.path.exists(links_json_file):
        with open(links_json_file, 'r+', encoding='utf-8') as f:
            try:
                links = json.load(f)
                if links:
                    url = links.pop(0)  # 첫 번째 링크 가져오기
                    f.seek(0)  # 파일의 시작 위치로 이동
                    f.truncate()  # 파일을 비우고
                    json.dump(links, f, ensure_ascii=False, indent=4)  # 남은 링크들을 다시 파일에 저장
                    return url
            except json.JSONDecodeError:
                print("Warning: Links to crawl JSON file is empty or corrupted.")
    return None

# 크롤링할 새 링크를 파일에 추가하는 함수
def append_links_to_file(new_links):
    if os.path.exists(links_json_file):
        with open(links_json_file, 'r+', encoding='utf-8') as f:
            try:
                links = json.load(f)
            except json.JSONDecodeError:
                links = []
    else:
        links = []

    links.extend(new_links)  # 새로운 링크 추가

    with open(links_json_file, 'w', encoding='utf-8') as f:
        json.dump(links, f, ensure_ascii=False, indent=4)

# URL 정규화 함수 (올바르지 않은 문자를 제거)
def normalize_url(url):
    return url.split(')')[0].strip()

# 필요 없는 문자를 제거하는 함수
def clean_text(text):
    # HTML 태그와 스크립트 및 스타일 내용 제거
    cleaned_text = re.sub(r'\s+', ' ', text)  # 불필요한 공백 제거
    cleaned_text = re.sub(r'[^a-zA-Z0-9가-힣\s]', '', cleaned_text)  # 특수문자 제거 (한글, 영문, 숫자만 남김)
    return cleaned_text.strip()

# 한글 포함 여부를 확인하는 함수
def contains_korean(text):
    korean_pattern = re.compile(r'[\u3131-\uD79D]+')  # 한글 유니코드 범위
    return bool(korean_pattern.search(text))

# 단어 빈도 계산 함수 (불용어 제거)
def word_frequency(text):
    words = re.findall(r'\b\w+\b', text.lower())
    filtered_words = [word for word in words if word not in set(['the', 'and', 'is', 'in', 'at', 'of', 'on', 'a', 'to'])]
    word_counts = Counter(filtered_words)
    return [{word: count} for word, count in word_counts.most_common(5)]

# 웹 크롤링 함수 (한국어가 있는 경우만 크롤링)
def crawl_website(url, crawl_data):
    # 이미 크롤링된 URL인지 확인
    if any(entry['url'] == url for entry in crawl_data):
        print(f"Skipping URL: {url} (Already crawled)")
        return []

    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Crawling URL: {url}")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 텍스트를 추출하고 필요 없는 문자 제거
            raw_text = soup.get_text()
            clean_text_content = clean_text(raw_text)

            # 한국어가 포함되지 않은 경우 크롤링 건너뛰기
            if not contains_korean(clean_text_content):
                print(f"Skipping URL: {url} (No Korean text found)")
                return []

            # 페이지의 단어 빈도 계산
            word_counts = word_frequency(clean_text_content)
            title = soup.title.string if soup.title else 'No Title'

            # 크롤링된 데이터를 crawl_data에 추가
            page_data = {
                'url': url,
                'title': title,
                'most_common_words': word_counts
            }
            crawl_data.append(page_data)
            save_crawl_data(crawl_data)  # 저장

            # 새 링크 수집
            new_links = []
            links = soup.find_all('a')
            for link in links:
                href = link.get('href')
                if href and href.startswith('http'):
                    href = normalize_url(href)
                    new_links.append(href)
            
            return new_links
        else:
            print(f"Failed to fetch {url}, status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"An error occurred while crawling {url}: {e}")
        return []

# 크롤링 실행
def run_crawler():
    crawl_data = load_crawl_data()  # 이미 크롤링된 데이터 불러오기

    while True:
        url = pop_link_from_file()  # 파일에서 크롤링할 링크 가져오기
        if not url:
            print("No more links to crawl. Exiting.")
            break
        
        new_links = crawl_website(url, crawl_data)
        if new_links:
            append_links_to_file(new_links)  # 새로운 링크들을 파일에 저장

# 초기 링크 설정
initial_link = 'https://news.google.com/home?hl=ko&gl=KR&ceid=KR:ko'
append_links_to_file([initial_link])  # 초기 링크를 파일에 저장

# 크롤러 실행
run_crawler()