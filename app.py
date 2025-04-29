from flask import Flask
import os  # Railway에서 제공하는 PROT 환경 변수 사용을 위한 import
from main.routes import main  # Blueprint import
from auth.routes import auth  # 추가된 블루프린트 import
from auth import db           # DB import

app = Flask(__name__)

# db를 실제로 연결해주는 코드
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:TIGtaUYtJUmbbtEXAGwWyuReGQNSCowP@metro.proxy.rlwy.net:56996/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # SQLAlchemy 이벤트 추적 기능 비활성화
db.init_app(app)  # Flask 앱과 db를 연결

# 블루프린트 등록
app.register_blueprint(main)  # Blueprint 등록
app.register_blueprint(auth)  # 새로 auth 등록


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Railway에서 제공하는 PORT 환경 변수 사용
    app.run(host='0.0.0.0', port=port)


