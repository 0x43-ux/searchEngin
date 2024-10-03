import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import json
import os

# 불용어 리스트 통합 (영어와 한국어)
english_stopwords = set(['the', 'and', 'is', 'in', 'at', 'of', 'on', 'a', 'to'])
korean_stopwords = set(['이', '그리고', '것', '수', '등', '저', '그', '는', '를', '에', '가', '의', '을', '은', '들', '이다', '인', '할', '한', '이것'])
combined_stopwords = english_stopwords.union(korean_stopwords)

# 건너뛸 도메인 리스트
skip_domains = ['support.google.com', 'apple.com']

# 파일 경로
links_json_file = 'links_to_crawl.json'
results_json_file = 'crawl_data.json'

# 이미 방문한 URL을 추적할 집합 (JSON 파일에서 색인된 URL도 포함)
visited_urls = set()

# 기존에 저장된 색인된 URL 불러오기
def load_indexed_urls():
    if os.path.exists(results_json_file):
        with open(results_json_file, 'r', encoding='utf-8') as f:
            try:
                indexed_data = json.load(f)
                for entry in indexed_data:
                    visited_urls.add(entry['url'])  # 이미 색인된 URL을 visited_urls에 추가
            except json.JSONDecodeError:
                print("Warning: Indexed JSON file is empty or corrupted.")
    print(f"Loaded {len(visited_urls)} indexed URLs.")

# 기존에 저장된 링크들을 불러오기 (없으면 빈 리스트 생성)
def load_links_to_crawl():
    if os.path.exists(links_json_file):
        with open(links_json_file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("Warning: JSON file is empty or corrupted, returning an empty list.")
                return []
    return []

# 크롤링할 링크를 저장하는 함수
def save_links_to_crawl(links):
    if os.path.exists(links_json_file):
        with open(links_json_file, 'r', encoding='utf-8') as f:
            existing_links = json.load(f)
    else:
        existing_links = []

    # 중복되지 않은 새 링크만 추가
    for link in links:
        if link not in existing_links and link not in visited_urls:  # 이미 색인된 URL을 제외
            existing_links.append(link)

    # 파일에 저장
    with open(links_json_file, 'w', encoding='utf-8') as f:
        json.dump(existing_links, f, ensure_ascii=False, indent=4)

# 분석 결과를 JSON 파일로 저장하는 함수
def save_crawl_data(data):
    if os.path.exists(results_json_file):
        with open(results_json_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    else:
        existing_data = []
    
    # 새로운 데이터 추가
    existing_data.extend(data)
    
    # 파일에 저장
    with open(results_json_file, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)

# 단어 빈도 계산 함수 (불용어 제거)
def word_frequency(text):
    words = re.findall(r'\b\w+\b', text.lower())
    filtered_words = [word for word in words if word not in combined_stopwords]
    word_counts = Counter(filtered_words)
    return [{word: count} for word, count in word_counts.most_common(5)]

# 한글 포함 여부를 확인하는 함수
def contains_korean(text):
    korean_pattern = re.compile(r'[\u3131-\uD79D]+')  # 한글 유니코드 범위
    return bool(korean_pattern.search(text))

# URL 정규화 함수 (올바르지 않은 문자를 제거)
def normalize_url(url):
    return url.split(')')[0].strip()

# 특정 도메인 건너뛰기 함수
def should_skip_url(url):
    for domain in skip_domains:
        if domain in url:
            return True
    return False

# 웹 크롤링 함수 (한글이 있는 경우만 색인)
def crawl_website(url):
    if should_skip_url(url):
        print(f"Skipping URL: {url} (Domain in skip list)")
        return []  # 건너뛸 URL은 크롤링하지 않음
    
    if url in visited_urls:
        print(f"Skipping URL: {url} (Already indexed)")
        return []  # 이미 색인된 URL은 건너뛰기

    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Crawling URL: {url}")
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()

            # 한글이 포함되어 있는지 확인
            if not contains_korean(text):
                print(f"Skipping URL: {url} (No Korean text found)")
                return []  # 한글이 없으면 크롤링하지 않음
            
            title = soup.title.string if soup.title else 'No Title'
            word_counts = word_frequency(text)
            
            page_data = {
                'url': url,
                'title': title,
                'most_common_words': word_counts
            }
            #crawl_data.append(page_data)
            visited_urls.add(url)  # 색인된 URL을 기록

            # 새 링크를 추가적으로 수집
            new_links = []
            links = soup.find_all('a')
            for link in links:
                href = link.get('href')
                if href and href.startswith('http'):
                    href = normalize_url(href)  # URL 정규화 처리
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
    load_indexed_urls()  # 기존에 색인된 URL을 불러오기
    links_to_crawl = load_links_to_crawl()  # 파일에서 크롤링할 링크 불러오기

    while links_to_crawl:
        url = links_to_crawl.pop(0)  # 리스트에서 첫 번째 링크를 가져옴
        if url not in visited_urls:
            new_links = crawl_website(url)
            if new_links:
                save_links_to_crawl(new_links)  # 새로운 링크들을 파일에 저장
            save_crawl_data(crawl_data)  # 크롤링 결과를 파일에 저장
            crawl_data.clear()  # 메모리 절약을 위해 데이터를 저장한 후 리스트 초기화

        # 크롤링할 링크가 더 이상 없으면 종료
        if not links_to_crawl:
            print("No more links to crawl. Exiting.")
            break

# 처음에 수집할 링크를 파일에 저장
initial_link = 'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=안유진'
save_links_to_crawl([initial_link])

# 크롤러 실행
run_crawler()