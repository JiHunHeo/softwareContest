from flask import Flask
import os  # Railway에서 제공하는 PROT 환경 변수 사용을 위한 import

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>경진대회</title>
        <link rel="stylesheet" href="/static/style.css">
        <script src="/static/script.js" defer></script>
        <link rel="icon" href="/static/favicon.png" type="image/png"> <!-- 파비콘 추가 -->
    </head>
    <body>
        <h1>우선 배포를 위해 코드를 수정하였습니다 !</h1>
        <h1>과제 제출 퐈이팅입니다 !!!</h1>
        <h1>학우 여러분 반갑습니다!</h1>
        <h1>팀장입니다 !</h1>
        <h1>박민희입니다 !</h1>
        <h1>강기동입니다 !</h1>
        <h1>김태형입니다 !</h1>
        <h1>김남영입니다 !</h1>
        <h1>25년 4월 7일 기준 깃헙 작업자 명단 ^^</h1>
        <h1 id="blinking-text" class="blink">경진대회 준비에 박차를 가해봅시다!</h1>
        <button onclick="stopBlinking()">반짝임 멈추기</button>
        <button onclick="startBlinking()">다시 반짝이게</button>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Railway에서 제공하는 PORT 환경 변수 사용
    app.run(host='0.0.0.0', port=port)
