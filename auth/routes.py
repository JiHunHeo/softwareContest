from flask import Blueprint, request, jsonify  # Flask 블루프린트, 요청/응답 처리용
from datetime import datetime  # 날짜 및 시간 처리용
import bcrypt  # 비밀번호 암호화용 라이브러리
from auth.models import User, db  # User 모델과 데이터베이스 객체 import

# auth 블루프린트 생성
auth = Blueprint('auth', __name__)


# 기본 홈 라우트 (서버 살아있는지 확인용)
@auth.route('/')
def home():
    return 'Hello, Flask!'


# 회원가입 API
@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()  # JSON 데이터 받아오기

    # 클라이언트에서 보낸 데이터 꺼내기
    user_id = data['user_id']
    email = data['email']
    username = data['username']
    birthdate = datetime.strptime(data['birthdate'], "%Y-%m-%d").date()  # 문자열 → 날짜 객체로 변환
    student_id = data['student_id']
    phone_number = data['phone_number']
    address = data['address']
    is_employed = data['is_employed']  # True / False
    security_question = data['security_question']
    security_answer = data['security_answer']
    password = data['password']

    # 중복 체크 (아이디, 이메일, 휴대폰번호, 학번)
    if User.query.filter_by(user_id=user_id).first():
        return jsonify({'message': '이미 사용 중인 아이디입니다.'}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({'message': '이미 등록된 이메일입니다.'}), 409
    if User.query.filter_by(phone_number=phone_number).first():
        return jsonify({'message': '이미 등록된 휴대폰 번호입니다.'}), 409
    if User.query.filter_by(student_id=student_id).first():
        return jsonify({'message': '이미 등록된 학번입니다.'}), 409

    # per_id 생성 (PERS + 년월일시분초 + 밀리초까지)
    now = datetime.now()
    per_id = "PERS" + now.strftime("%Y%m%d%H%M%S%f")[:20]  # 최대 20자리 맞춤

    # 비밀번호 암호화
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # 새 사용자 객체 생성
    new_user = User(
        per_id=per_id,
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
        password=hashed_pw.decode('utf-8')  # 저장할 때 문자열로 저장
    )

    # 데이터베이스에 추가 및 저장
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': '회원가입 성공!', 'per_id': per_id})


# 로그인 API
@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # 입력한 사용자 이름으로 사용자 조회
    user = User.query.filter_by(username=username).first()

    # 비밀번호 비교 (암호화된 비밀번호와 비교)
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'message': '로그인 성공!'})
    else:
        return jsonify({'message': '아이디 또는 비밀번호가 틀렸습니다.'}), 401


# ID 찾기 API (이메일로 찾기)
@auth.route('/find_id', methods=['POST'])
def find_id():
    data = request.get_json()
    email = data['email']

    # 이메일로 사용자 조회
    user = User.query.filter_by(email=email).first()

    if user:
        return jsonify({'username': user.username})  # 사용자 아이디 반환
    else:
        return jsonify({'message': '등록된 이메일이 없습니다.'}), 404


# 비밀번호 재설정 API
@auth.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data['email']
    username = data['username']
    new_password = data['new_password']

    # 이메일 + 사용자 이름이 일치하는 사용자 조회
    user = User.query.filter_by(email=email, username=username).first()

    if user:
        # 새 비밀번호 암호화 후 저장
        hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.password = hashed_pw.decode('utf-8')
        db.session.commit()
        return jsonify({'message': '비밀번호가 성공적으로 변경되었습니다.'})
    else:
        return jsonify({'message': '이메일 또는 아이디가 일치하지 않습니다.'}), 404
