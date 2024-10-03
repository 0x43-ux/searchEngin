from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/process-url', methods=['POST'])
def process_url():
    # 클라이언트에서 받은 URL을 가져옴
    data = request.json
    url = data.get('url')

    # URL이 유효한지 확인
    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # URL에 GET 요청을 보냄
        response = requests.get(url)
        if response.status_code == 200:
            # BeautifulSoup으로 HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')

            # 예시로 제목(title)과 본문 첫 단락(p)을 추출
            title = soup.title.string if soup.title else 'No Title'
            first_paragraph = soup.find('p').text if soup.find('p') else 'No paragraph found'

            return jsonify({
                "url": url,
                "title": title,
                "first_paragraph": first_paragraph
            })
        else:
            return jsonify({"error": f"Failed to fetch URL, status code {response.status_code}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)