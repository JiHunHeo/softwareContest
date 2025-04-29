from auth import db  # db 연결 가져오기

class User(db.Model):
    __tablename__ = 'user'  # 테이블명 명시

    per_id = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    is_employed = db.Column(db.Boolean, default=False)
    security_question = db.Column(db.String(255), nullable=False)
    security_answer = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    is_admin = db.Column(db.Boolean, default=False)
