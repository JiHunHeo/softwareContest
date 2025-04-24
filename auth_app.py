from flask import Flask, request, jsonify #Flask 웹 서버, 요청처리, JSON 응답용
from flask_sqlalchemy import SQLAlchemy
import bcrypt #비밀번호 암호화용 라이브러리

# Flask 앱 초기화
app = Flask(__name__)

# 데이터베이스 설정 (레일웨이 url 연결)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:TIGtaUYtJUmbbtEXAGwWyuReGQNSCowP@metro.proxy.rlwy.net:56996/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # SQLAlchemy 이벤트 추적 기능 비활성화

# SQLAlchemy로 DB 연결
db = SQLAlchemy(app)

# User 모델 정의
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 사용자 고유 ID (자동 증가)
    username = db.Column(db.String(50), unique=True, nullable=False) # 사용자 이름 (중복 불가, 필수)
    email = db.Column(db.String(100), unique=True, nullable=False) # 이메일 (중복 불가, 필수)
    password = db.Column(db.String(255), nullable=False) # 암호화된 비밀번호

# 회원가입 라우트
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() # JSON 형식으로 요청 데이터 받기
    username = data['username']
    email = data['email']
    password = data['password']

    # 비밀번호 암호화
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # 새 유저 DB에 저장
    new_user = User(username=username, email=email, password=hashed_pw.decode('utf-8'))
    db.session.add(new_user) # DB에 추가
    db.session.commit() # 저장

    return jsonify({'message': '회원가입 성공!'}) # 클라이언트에게 성공 메시지 반환

# 기본 홈 라우트 (서버 상태 확인 위해 넣어둠)
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

    # 사용자 존재 & 비밀번호 일치 확인
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'message': '로그인 성공!'})
    else:
        return jsonify({'message': '아이디 또는 비밀번호가 틀렸습니다.'}), 401

# ID 찾기 API (이메일로 ID 찾기)
@app.route('/find_id', methods=['POST'])
def find_id():
    data = request.get_json()
    email = data['email']

    # 이메일로 사용자 조회
    user = User.query.filter_by(email=email).first()

    if user:
        return jsonify({'username': user.username})  # 아이디 반환
    else:
        # 이메일 등록 안 되어 있을 경우
        return jsonify({'message': '등록된 이메일이 없습니다.'}), 404

# 비밀번호 재설정 API
@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data['email']
    username = data['username']
    new_password = data['new_password']

    # 이메일 + 아이디로 사용자 조회
    user = User.query.filter_by(email=email, username=username).first()

    if user:
        # 새 비밀번호 암호화 후 DB 업데이트
        hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.password = hashed_pw.decode('utf-8')
        db.session.commit()
        return jsonify({'message': '비밀번호가 성공적으로 변경되었습니다.'})
    else:
        # 정보 불일치 시
        return jsonify({'message': '이메일 또는 아이디가 일치하지 않습니다.'}), 404



# 서버 시작
if __name__ == '__main__':
    # Flask 애플리케이션 컨텍스트 내에서 DB 테이블 생성
    # 테이블이 이미 존재하면 생성하지 않음
    with app.app_context():   
        db.create_all()       # 테이블 생성
    app.run(debug=True) # 디버그 모드로 서버 실행 (나중에 삭제해야함/임시)


