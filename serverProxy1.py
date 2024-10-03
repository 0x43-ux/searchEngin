import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return '''
        <form action="/proxy" method="get">
            URL to Proxy: <input name="url" type="text">
            <input type="submit" value="Go">
        </form>
    '''

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "URL is required."

    try:
        # 원본 URL로 요청
        response = requests.get(url)
        return response.content
    except Exception as e:
        return f"Error occurred: {str(e)}"

if __name__ == '__main__':
    app.run()