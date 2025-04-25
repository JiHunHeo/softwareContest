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
# 사용자(User) 테이블 모델 정의
# User 모델 정의
# 사용자(User) 테이블 모델 정의
class User(db.Model):
    __tablename__ = 'users' 
    # 로그인 아이디 (Primary Key, 중복 불가, 필수 입력)
    user_id = db.Column(db.String(50), primary_key=True, nullable=False)
    
    # 사용자 이름 (필수 입력)
    username = db.Column(db.String(50), nullable=False)

    # 이메일 (중복 불가, 필수 입력)
    email = db.Column(db.String(100), unique=True, nullable=False)
    
    # 생년월일 (형식: YYYY-MM-DD, 필수 입력)
    birthdate = db.Column(db.Date, nullable=False)
    
    # 학번 (중복 불가, 필수 입력)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    
    # 휴대폰 번호 (중복 불가, 필수 입력)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    
    # 주소 (필수 입력)
    address = db.Column(db.String(255), nullable=False)
    
    # 직장인 여부 (True: 직장인, False: 학생 등 / 기본값: False)
    is_employed = db.Column(db.Boolean, default=False)
    
    # 비밀번호 찾기 질문 (필수 입력)
    security_question = db.Column(db.String(255), nullable=False)
    
    # 비밀번호 찾기 답변 (필수 입력)
    security_answer = db.Column(db.String(255), nullable=False)
    
    # 암호화된 비밀번호 (필수 입력)
    password = db.Column(db.String(200), nullable=False)
    
    # 가입일 (자동 저장, 현재 시간 기준)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # 관리자 여부 (기본값: 일반 사용자 False)
    is_admin = db.Column(db.Boolean, default=False)


#회원가입 라우트
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # 필수 항목 받기
    # 사용자가 직접 입력한 로그인 아이디 (중복 체크 대상)
    user_id = data['user_id']

    # 이메일 (중복 체크 대상, 예: 'minhee@example.com')
    email = data['email']

    # 사용자 이름 (예: '박민희')
    username = data['username']

    # 생년월일 (형식: 'YYYY-MM-DD', 예: '1995-05-15')
    birthdate = data['birthdate']

    # 학번 (중복 체크 대상, 예: '20250001')
    student_id = data['student_id']

    # 휴대폰 번호 (중복 체크 대상, 예: '01012345678')
    phone_number = data['phone_number']

    # 주소 (예: '서울특별시 강남구')
    address = data['address']

    # 직장인 여부 (True: 직장인, False: 학생 등, Boolean 값)
    is_employed = data['is_employed']

    # 비밀번호 찾기 질문 (예: '내 고향은?')
    security_question = data['security_question']

    # 비밀번호 찾기 답변 (예: '울산')
    security_answer = data['security_answer']

    # 사용자가 입력한 비밀번호 (암호화 후 DB에 저장)
    password = data['password']


    # 중복 검사 (user_id, phone_number, student_id)
    if User.query.filter_by(user_id=user_id).first():
        return jsonify({'message': '이미 사용 중인 아이디입니다.'}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({'message': '이미 등록된 이메일입니다.'}), 409
    if User.query.filter_by(phone_number=phone_number).first():
        return jsonify({'message': '이미 등록된 휴대폰 번호입니다.'}), 409
    if User.query.filter_by(student_id=student_id).first():
        return jsonify({'message': '이미 등록된 학번입니다.'}), 409

    # 비밀번호 암호화
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # 새 유저 저장
    new_user = User(
        user_id=user_id,
        username=username,
        email=email,
        birthdate=birthdate,
        student_id=student_id,
        phone_number=phone_number,
        address=address,
        is_employed=is_employed,
        security_question=security_question,
        security_answer=security_answer,
        password=hashed_pw.decode('utf-8')
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': '회원가입 성공!'})


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


