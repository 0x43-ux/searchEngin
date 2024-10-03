from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 모든 도메인에 대해 CORS 허용

@app.route('/proxy', methods=['POST'])
def proxy():
    # 클라이언트에서 받은 요청 데이터
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # 대상 URL로 GET 요청
        response = requests.get(url)

        # 대상 서버의 응답을 클라이언트로 반환
        return jsonify({
            "status": response.status_code,
            "content": response.text
        })
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)