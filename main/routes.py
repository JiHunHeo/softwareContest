import json
import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Post, Comment, User, Notice, UserLoginFail
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from flask_login import current_user, login_required, logout_user, login_user
from urllib.parse import urlparse
import pytz

logging.basicConfig(level=logging.DEBUG)

main = Blueprint('main', __name__, template_folder='templates')

MAX_LOGIN_ATTEMPTS = 5  # 최대 허용 로그인 실패 횟수
LOCKOUT_TIME = 10  # 계정 잠금 시간 (분)

def get_kst_time():
    kst = pytz.timezone('Asia/Seoul')
    return datetime.now(kst)

@main.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@main.route('/about')
def about():
    return render_template('about.html')
@main.route('/market')
def market():
    return render_template('market.html')

def get_commits_from_file(json_file):
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{json_file} 파일을 찾을 수 없습니다.")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON 파일을 읽는 중 에러 발생: {e}")
        return []

@main.route('/timeline')
def timeline():
    commits = get_commits_from_file("commits.json")  # JSON 파일에서 커밋 정보 읽기

    # 페이지네이션 계산
    page = int(request.args.get('page', 1))  # 현재 페이지 (기본값: 1)
    per_page = 10  # 페이지당 커밋 수
    total_pages = (len(commits) + per_page - 1) // per_page  # 전체 페이지 수 계산

    # 현재 페이지에 해당하는 커밋만 전달
    start = (page - 1) * per_page
    end = start + per_page
    paginated_commits = commits[start:end]

    return render_template(
        'timeline.html',
        commits=paginated_commits,
        page=page,
        total_pages=total_pages
    )

# 게시판별 게시글 목록
@main.route('/board/<board_type>')
def board(board_type):
    posts = Post.query.filter_by(board_type=board_type).all()
    return render_template('board.html', posts=posts, board_type=board_type)

# 게시글 작성
@main.route('/board/<board_type>/new', methods=['GET', 'POST'])
def new_post(board_type):
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        price = request.form.get('price')

        # 게시판 조회
        board = BoardType.query.filter_by(name=board_type).first_or_404()

        # 게시글 생성
        new_post = Post(
            title=title,
            content=content,
            author_id=1,  # 로그인된 사용자 ID로 변경 필요
            board_type_id=board.id,
            price=price,
            created_at=datetime.utcnow()
        )
        db.session.add(new_post)

        # 게시판의 게시글 수 증가
        board.post_count += 1
        db.session.commit()

        flash('게시글이 작성되었습니다!')
        return redirect(url_for('main.board', board_type=board_type))

    return render_template('new_post.html', board_type=board_type)

# 게시글 상세보기
@main.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)

    # 조회수 증가
    post.views += 1
    db.session.commit()

    comments = Comment.query.filter_by(post_id=post_id).all()
    return render_template('post_detail.html', post=post, comments=comments)

@main.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    content = request.form['content']
    new_comment = Comment(
        content=content,
        author_id=1,  # 로그인된 사용자 ID로 변경 필요
        post_id=post_id,
        created_at=datetime.utcnow()
    )
    db.session.add(new_comment)
    db.session.commit()

    flash('댓글이 작성되었습니다!')
    return redirect(url_for('main.post_detail', post_id=post_id))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            user_id = request.form['user_id']
            email = request.form['email']  # 이메일 추가
            username = request.form['username']
            nickname = request.form.get('nickname')  # 닉네임 추가 (선택적)
            birthdate = request.form['birthdate']
            student_id = request.form['student_id']
            phone_number = request.form['phone_number']
            address = request.form['address']
            is_employed = 'is_employed' in request.form
            security_question = request.form['security_question']
            security_answer = request.form['security_answer']
            password = request.form['password']

            # 비밀번호 해싱
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            # 사용자 추가
            new_user = User(
                user_id=user_id,
                email=email,  # 이메일 저장
                username=username,
                nickname=nickname,  # 닉네임 저장
                birthdate=birthdate,
                student_id=student_id,
                phone_number=phone_number,
                address=address,
                is_employed=is_employed,
                security_question=security_question,
                security_answer=security_answer,
                password=hashed_password
            )
            db.session.add(new_user)
            db.session.commit()

            flash('회원가입이 완료되었습니다!')
            return redirect(url_for('main.index'))  # 메인 페이지로 리다이렉트
        except Exception as e:
            db.session.rollback()
            print(f"에러 발생: {e}")
            flash('회원가입 중 문제가 발생했습니다. 다시 시도해주세요.')
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        user = User.query.filter_by(user_id=user_id).first()

        if user:
            # 계정 잠금 상태 확인
            if user.is_locked:
                if user.lock_until and datetime.utcnow() < user.lock_until:
                    remaining_time = (user.lock_until - datetime.utcnow()).seconds // 60
                    flash(f"계정이 잠겨 있습니다. {remaining_time}분 후에 다시 시도하세요.")
                    return redirect(url_for('main.login'))
                else:
                    # 잠금 해제 및 실패 기록 초기화
                    user.is_locked = False
                    user.lock_until = None
                    UserLoginFail.query.filter_by(user_id=user.per_id).delete()
                    db.session.commit()

            # 비밀번호 검증
            if user and check_password_hash(user.password, password):
                UserLoginFail.query.filter_by(user_id=user.per_id).delete()
                db.session.commit()

                # 로그인 성공
                user.last_login_at = get_kst_time()  # 마지막 로그인 시간 갱신
                user.last_login_ip = request.remote_addr  # 마지막 로그인 IP 기록
                user.is_locked = False  # 계정 잠금 해제
                user.lock_until = None

                # 실패 기록 초기화
                UserLoginFail.query.filter_by(user_id=user.per_id).delete()

                login_user(user)
                flash('로그인 성공!')
                return redirect(url_for('main.index'))
            else:
                # 로그인 실패 처리
                failed_attempts = UserLoginFail.query.filter(
                    UserLoginFail.user_id == user.per_id,
                    UserLoginFail.failed_at >= datetime.utcnow() - timedelta(minutes=LOCKOUT_TIME)
                ).count()

                if failed_attempts + 1 >= MAX_LOGIN_ATTEMPTS:
                    # 계정 잠금
                    user.is_locked = True
                    user.lock_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_TIME)
                    db.session.commit()
                    flash(f"로그인 실패 횟수가 초과되었습니다. 계정이 {LOCKOUT_TIME}분 동안 잠깁니다.")
                else:
                    # 실패 기록 저장
                    failed_attempt = UserLoginFail.query.filter_by(user_id=user.per_id, failed_at=get_kst_time()).first()

                    if failed_attempt:
                        # 동일한 실패 기록이 이미 존재하면 업데이트하지 않음
                        logging.debug(f"Duplicate login fail record for User ID: {user.per_id}")
                    else:
                        # 새로운 실패 기록 생성
                        failed_attempt = UserLoginFail(
                            user_id=user.per_id,
                            ip_address=request.remote_addr,
                            fail_count=failed_attempts + 1,
                            is_locked=False,
                            failed_at=get_kst_time()
                        )
                        db.session.add(failed_attempt)

                    db.session.commit()
                    logging.debug(f"User ID: {user.per_id}, Failed Attempts: {failed_attempt.fail_count}")

                    flash(f"로그인 실패. {failed_attempts + 1}/{MAX_LOGIN_ATTEMPTS}회 시도했습니다.")

                return redirect(url_for('main.login'))
        else:
            flash('존재하지 않는 사용자입니다.')
            return redirect(url_for('main.login'))

    return render_template('login.html')

@main.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('로그아웃되었습니다.')
    return redirect(url_for('main.index'))

@main.route('/crawl_notices')
def crawl_notices():
    json_file_path = os.path.join(os.getcwd(), 'notice_urls.json')

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            notice_urls = json.load(f)

        for url in notice_urls:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 현재 URL의 도메인 추출
            parsed_url = urlparse(url)
            base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

            # 공지사항 데이터 추출
            notices = soup.find('table', class_='board-table horizon1').find('tbody').find_all('tr')
            for notice in notices:
                # 제목 추출
                title_tag = notice.find('td', class_='td-subject').find('a')
                title = title_tag.text.strip()

                # 불필요한 공백 및 줄바꿈 제거
                title = " ".join(title.split())

                # 제목 길이 제한
                MAX_TITLE_LENGTH = 1000
                if len(title) > MAX_TITLE_LENGTH:
                    title = title[:MAX_TITLE_LENGTH]

                # 작성일 추출
                date = notice.find('td', class_='td-date').text.strip()

                # 링크 추출
                source_url = title_tag['href']
                if not source_url.startswith('http'):
                    source_url = f"{base_domain}{source_url}"

                # 중복 데이터 방지
                with db.session.no_autoflush:
                    if not Notice.query.filter_by(title=title, source_url=source_url).first():
                        new_notice = Notice(
                            title=title,
                            content=date,
                            source_url=source_url,
                            created_at=datetime.utcnow()
                        )
                        db.session.add(new_notice)

        db.session.commit()
        flash('공지사항이 업데이트되었습니다!')
    except FileNotFoundError:
        flash('notice_urls.json 파일을 찾을 수 없습니다.')
    except json.JSONDecodeError:
        flash('notice_urls.json 파일의 형식이 잘못되었습니다.')
    except requests.exceptions.RequestException as e:
        flash(f'크롤링 중 오류가 발생했습니다: {e}')

    return redirect(url_for('main.index'))

@main.route('/notices')
def notices():
    # 공지사항 데이터 조회
    notices = Notice.query.order_by(Notice.created_at.desc()).all()
    return render_template('notices.html', notices=notices)

@main.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)

    if user:
        db.session.delete(user)
        db.session.commit()
        flash('회원 탈퇴가 완료되었습니다.')
        logout_user()  # 세션 종료
        return redirect(url_for('main.index'))
    else:
        flash('사용자를 찾을 수 없습니다.')
        return redirect(url_for('main.profile'))

@main.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        user_id = request.form['user_id']
        security_answer = request.form['security_answer']

        # 사용자 조회
        user = User.query.filter_by(user_id=user_id).first()

        if user and user.security_answer == security_answer:
            flash('본인 확인이 완료되었습니다. 비밀번호를 재설정하세요.')
            return redirect(url_for('main.reset_password', user_id=user.id))
        else:
            flash('아이디 또는 답변이 일치하지 않습니다.')
            return redirect(url_for('main.forgot_password'))

    return render_template('forgot_password.html')

@main.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
def reset_password(user_id):
    user = User.query.get(user_id)

    if not user:
        flash('사용자를 찾을 수 없습니다.')
        return redirect(url_for('main.forgot_password'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

        user.password = hashed_password
        db.session.commit()

        flash('비밀번호가 성공적으로 변경되었습니다.')
        return redirect(url_for('main.login'))

    return render_template('reset_password.html', user=user)

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    # 게시판 조회
    board = BoardType.query.get(post.board_type_id)

    # 게시글 삭제
    db.session.delete(post)

    # 게시판의 게시글 수 감소
    if board and board.post_count > 0:
        board.post_count -= 1

    db.session.commit()
    flash('게시글이 삭제되었습니다!')
    return redirect(url_for('main.board', board_type=board.name))

@main.route('/samplegrid')
def samplegrid():
    
    # 그리드 컬럼 선언
    columns = [
        {"label": "제목", "key": "title"},
        {"label": "내용", "key": "content"},
        {"label": "날짜", "key": "date"}
    ]
    # 그리드 샘플 json 데이터
    data = get_commits_from_file("gridsampledata.json")

    return render_template('samplegrid.html', table_id="samplegrid", columns=columns, data=data)
