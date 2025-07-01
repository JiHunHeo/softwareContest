from extensions import db
from flask_login import UserMixin
from datetime import datetime
import pytz

def generate_per_id():
    """회원가입 당시의 년월일시분초밀리초를 기반으로 고유 per_id 생성"""
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    return 'PERS' + now.strftime('%Y%m%d%H%M%S') + f"{now.microsecond // 1000:03d}"  # 밀리초 추가

def get_kst_time():
    """현재 시간을 한국 시간(KST)으로 반환"""
    kst = pytz.timezone('Asia/Seoul')
    return datetime.now(kst)

# 사용자 테이블
class User(db.Model, UserMixin):
    per_id = db.Column(db.String(24), primary_key=True, default=generate_per_id)    # 사용자 고유 ID
    user_id = db.Column(db.String(50), nullable=False, unique=True)                 # 로그인용 아이디
    email = db.Column(db.String(100), nullable=False, unique=True)                  # 이메일
    username = db.Column(db.String(50), nullable=False)                             # 사용자 이름
    nickname = db.Column(db.String(50), nullable=True)                              # 닉네임 (선택적)
    birthdate = db.Column(db.Date, nullable=False)                                  # 생년월일
    student_id = db.Column(db.String(20), nullable=False, unique=True)              # 학번
    phone_number = db.Column(db.String(15), nullable=False, unique=True)            # 휴대폰 번호
    address = db.Column(db.String(255), nullable=False)                             # 주소
    is_employed = db.Column(db.Boolean, default=False)                              # 직장인 여부
    security_question = db.Column(db.String(255), nullable=False)                   # 비밀번호 찾기 질문
    security_answer = db.Column(db.String(255), nullable=False)                     # 비밀번호 찾기 답변
    password = db.Column(db.String(200), nullable=False)                            # 비밀번호 (해싱된 값)
    created_at = db.Column(db.DateTime, default=get_kst_time)                       # 가입일
    updated_at = db.Column(db.DateTime, onupdate=get_kst_time)                      # 수정일
    last_login_at = db.Column(db.DateTime, nullable=True)                           # 마지막 로그인 시간
    last_login_ip = db.Column(db.String(45), nullable=True)                         # 마지막 로그인 IP
    is_admin = db.Column(db.Boolean, default=False)                                 # 관리자 여부
    is_locked = db.Column(db.Boolean, default=False)                                # 계정 잠금 여부
    lock_until = db.Column(db.DateTime, nullable=True)                              # 계정 잠금 해제 시간

    # 관계 설정
    posts = db.relationship('Post', backref='author', lazy=True)                    # 작성한 게시글
    comments = db.relationship('Comment', backref='author', lazy=True)              # 작성한 댓글

    # Flask-Login에서 사용자 고유 식별자로 사용할 값 반환
    def get_id(self):
        return self.per_id

# 게시글 테이블
class Post(db.Model):
    per_id = db.Column(db.String(24), db.ForeignKey('user.per_id'), primary_key=True)               # 게시글 작성자의 per_id
    title = db.Column(db.String(100), nullable=False)                                               # 게시글 제목
    content = db.Column(db.Text, nullable=False)                                                    # 게시글 내용
    board_type_id = db.Column(db.String(20), db.ForeignKey('board_type.per_id'), nullable=False)    # 게시판 유형 (BoardType 참조)
    price = db.Column(db.Float, nullable=True)                                                      # 중고 게시판의 가격 (선택적)
    status = db.Column(db.String(20), default='판매 중')                                            # 거래 상태 (중고 게시판 전용)
    views = db.Column(db.Integer, default=0)                                                        # 조회수
    created_at = db.Column(db.DateTime, default=get_kst_time)                                       # 작성일
    updated_at = db.Column(db.DateTime, onupdate=get_kst_time)                                      # 수정일

    # 관계 설정
    comments = db.relationship('Comment', backref='post', lazy=True)    # 게시글에 달린 댓글

# 댓글 테이블
class Comment(db.Model):
    per_id = db.Column(db.String(24), db.ForeignKey('user.per_id'), primary_key=True)   # 댓글 작성자의 per_id
    post_id = db.Column(db.String(24), db.ForeignKey('post.per_id'), nullable=False)    # 게시글 (Post 테이블 참조)
    content = db.Column(db.Text, nullable=False)                                        # 댓글 내용
    created_at = db.Column(db.DateTime, default=get_kst_time)                           # 작성일

# 공지사항 테이블
class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    # 기본 키 추가
    title = db.Column(db.String(200), nullable=False)                   # 공지사항 제목
    content = db.Column(db.Text, nullable=False)                        # 공지사항 내용
    source_url = db.Column(db.String(300), nullable=False)              # 출처 URL
    created_at = db.Column(db.DateTime, default=get_kst_time)           # 작성일
    
class BoardType(db.Model):
    per_id = db.Column(db.String(24), primary_key=True)             # 게시판 유형 ID
    name = db.Column(db.String(50), nullable=False, unique=True)    # 게시판 이름
    description = db.Column(db.String(255), nullable=True)          # 게시판 설명
    post_count = db.Column(db.Integer, default=0)                   # 게시판에 속한 게시글 수

    # 관계 설정
    posts = db.relationship('Post', backref='board', lazy=True)     # 게시판에 속한 게시글

# 실패 기록 테이블
class UserLoginFail(db.Model):
    per_id = db.Column(db.String(24), primary_key=True, default=generate_per_id)        # 고유 ID
    user_id = db.Column(db.String(24), db.ForeignKey('user.per_id'), nullable=False)    # 실패한 사용자 ID
    failed_at = db.Column(db.DateTime, default=get_kst_time)                            # 실패한 시간
    ip_address = db.Column(db.String(45), nullable=True)                                # 실패 요청의 IP 주소
    fail_count = db.Column(db.Integer, default=0)                                       # 현재 실패 횟수
    is_locked = db.Column(db.Boolean, default=False)                                    # 계정 잠금 상태