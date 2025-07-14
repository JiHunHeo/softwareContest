from extensions import db
from flask_login import UserMixin
from datetime import datetime
import pytz

def get_kst_time():
    """현재 시간을 한국 시간(KST)으로 반환"""
    kst = pytz.timezone('Asia/Seoul')
    return datetime.now(kst)

# 간단한 사용자 테이블
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=get_kst_time)
    is_admin = db.Column(db.Boolean, default=False)

    # 관계 설정
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

    def get_id(self):
        return str(self.id)

# 게시글 테이블
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    board_type = db.Column(db.String(50), default='일반')
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=get_kst_time)

    # 관계 설정
    comments = db.relationship('Comment', backref='post', lazy=True)

# 댓글 테이블
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=get_kst_time)

# 공지사항 테이블
class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=get_kst_time)
