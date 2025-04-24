from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import bcrypt

# Flask 앱 초기화
app = Flask(__name__)

# 데이터베이스 설정 (레일웨이 url 연결)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:TIGtaUYtJUmbbtEXAGwWyuReGQNSCowP@metro.proxy.rlwy.net:56996/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy로 DB 연결
db = SQLAlchemy(app)

# User 모델 정의
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# 회원가입 라우트
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']

    # 비밀번호 암호화
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # 새 유저 DB에 저장
    new_user = User(username=username, email=email, password=hashed_pw.decode('utf-8'))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': '회원가입 성공!'})

# 기본 홈 라우트
@app.route('/')
def home():
    return 'Hello, Flask!'

# 로그인 라우트
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # 유저 조회
    user = User.query.filter_by(username=username).first()

    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'message': '로그인 성공!'})
    else:
        return jsonify({'message': '아이디 또는 비밀번호가 틀렸습니다.'}), 401

@app.route('/find_id', methods=['POST'])
def find_id():
    data = request.get_json()
    email = data['email']

    user = User.query.filter_by(email=email).first()

    if user:
        return jsonify({'username': user.username})
    else:
        return jsonify({'message': '등록된 이메일이 없습니다.'}), 404

@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data['email']
    username = data['username']
    new_password = data['new_password']

    user = User.query.filter_by(email=email, username=username).first()

    if user:
        hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.password = hashed_pw.decode('utf-8')
        db.session.commit()
        return jsonify({'message': '비밀번호가 성공적으로 변경되었습니다.'})
    else:
        return jsonify({'message': '이메일 또는 아이디가 일치하지 않습니다.'}), 404



# 서버 시작
if __name__ == '__main__':
    with app.app_context():   
        db.create_all()       # 테이블 생성
    app.run(debug=True)


