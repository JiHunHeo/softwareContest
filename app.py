from flask import Flask
import os  # Railway에서 제공하는 PROT 환경 변수 사용을 위한 import
from main.routes import main  # Blueprint import

app = Flask(__name__)
app.register_blueprint(main)  # Blueprint 등록

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Railway에서 제공하는 PORT 환경 변수 사용
    app.run(host='0.0.0.0', port=port)
