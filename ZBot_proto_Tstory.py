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

# 기존에 저장된 크롤링할 링크들을 불러오기 (없으면 빈 리스트 생성)
def load_links_to_crawl():
    if os.path.exists(links_json_file):
        with open(links_json_file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("Warning: Links to crawl JSON file is empty or corrupted, returning an empty list.")
                return []
    return []

# 크롤링할 링크를 저장하는 함수
def save_links_to_crawl(links):
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

# 단어 빈도 계산 함수 (불용어 제거)
def word_frequency(text):
    words = re.findall(r'\b\w+\b', text.lower())
    filtered_words = [word for word in words if word not in set(['the', 'and', 'is', 'in', 'at', 'of', 'on', 'a', 'to'])]
    word_counts = Counter(filtered_words)
    return [{word: count} for word, count in word_counts.most_common(5)]

# 웹 크롤링 함수
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
    links_to_crawl = load_links_to_crawl()  # 파일에서 크롤링할 링크 불러오기

    while links_to_crawl:
        url = links_to_crawl.pop(0)  # 리스트에서 첫 번째 링크를 가져옴
        new_links = crawl_website(url, crawl_data)
        if new_links:
            links_to_crawl.extend(new_links)  # 새로운 링크들을 추가
            save_links_to_crawl(links_to_crawl)  # 새로운 링크들을 파일에 저장


        # 크롤링할 링크가 더 이상 없으면 종료
        if not links_to_crawl:
            print("No more links to crawl. Exiting.")
            break

# 초기 링크 설정
initial_link = 'https://section.blog.naver.com/ThemePost.naver?directoryNo=0&activeDirectorySeq=0&currentPage=1'
save_links_to_crawl([initial_link])

# 크롤러 실행
run_crawler()