from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from extensions import db
from flask_migrate import Migrate
from main.routes import main
from models import User, Post, Comment, Notice
from flask_moment import Moment
from datetime import datetime
import pytz

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # 세션 암호화를 위한 키 설정

# MySQL 데이터베이스 설정
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_port = os.getenv('DB_PORT')

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:TIGtaUYtJUmbbtEXAGwWyuReGQNSCowP@metro.proxy.rlwy.net:56996/railway'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
print("+++++++++++++++++++++++")
print(app.config['SQLALCHEMY_DATABASE_URI'])
db.init_app(app)

# Flask-Migrate 초기화
migrate = Migrate(app, db)

# Flask-Login 초기화
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'  # 로그인 페이지 경로 설정

# Flask-Moment 초기화
moment = Moment(app)

# 사용자 로드 함수
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(main)

@app.template_filter('momentjs')
def momentjs_filter(value, timezone='Asia/Seoul'):
    if value is None:
        return ''
    kst = pytz.timezone(timezone)
    local_time = value.astimezone(kst)
    return local_time.strftime('%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 테이블 생성
    app.run(host='0.0.0.0', port=5000, debug=True)
