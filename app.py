from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>경진대회</title>
        <link rel="stylesheet" href="/static/style.css">
        <script src="/static/script.js" defer></script>
    </head>
    <body>
        <h1>학우 여러분 반갑습니다!</h1>
        <h1>팀장입니다 !</h1>
        <h1>박민희입니다 !</h1>
        <h1 id="blinking-text" class="blink">경진대회 준비에 박차를 가해봅시다!</h1>
        <button onclick="stopBlinking()">반짝임 멈추기</button>
        <button onclick="startBlinking()">다시 반짝이게</button>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)