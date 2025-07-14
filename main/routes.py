import json
import os
import logging
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Post, Comment, User, Notice, UserLoginFail, BoardType
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
    """메인 페이지 - 새 디자인으로 리다이렉트"""
    return redirect(url_for('main.new_index'))

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
@main.route('/post/<string:post_id>')
def post_detail(post_id):
    """게시글 상세보기"""
    post = Post.query.filter_by(per_id=post_id).first_or_404()
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    
    # 조회수 증가
    post.views = (post.views or 0) + 1
    db.session.commit()
    
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
    """마이페이지"""
    if not current_user.is_authenticated:
        return redirect(url_for('main.new_login'))
    
    # 사용자 통계 정보
    user_stats = {
        'posts_count': Post.query.filter_by(author_id=current_user.per_id).count(),
        'comments_count': Comment.query.filter_by(author_id=current_user.per_id).count(),
        'likes_count': 0  # 좋아요 기능 구현시 추가
    }
    
    # 사용자 게시글
    user_posts = Post.query.filter_by(author_id=current_user.per_id)\
                          .order_by(Post.created_at.desc())\
                          .limit(10).all()
    
    # 사용자 댓글
    user_comments = Comment.query.filter_by(author_id=current_user.per_id)\
                                 .order_by(Comment.created_at.desc())\
                                 .limit(10).all()
    
    return render_template('profile.html', 
                         user_stats=user_stats,
                         user_posts=user_posts, 
                         user_comments=user_comments)

@main.route('/security')
def security():
    """보안 페이지"""
    return render_template('security.html')

@main.route('/statistics')
def statistics():
    """통계 페이지"""
    return render_template('statistics.html')

@main.route('/logout')
def logout():
    """로그아웃"""
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('main.new_index'))

# API 엔드포인트들
@main.route('/api/posts', methods=['POST'])
def api_create_post():
    """게시글 작성 API"""
    if not current_user.is_authenticated:
        return {'success': False, 'message': '로그인이 필요합니다.'}, 401
    
    try:
        title = request.form.get('title')
        content = request.form.get('content')
        board_type = request.form.get('board_type')
        
        if not all([title, content, board_type]):
            return {'success': False, 'message': '필수 항목을 모두 입력해주세요.'}, 400
        
        # 게시글 생성
        new_post = Post(
            title=title,
            content=content,
            author_id=current_user.per_id,
            board_type=board_type,
            created_at=get_kst_time()
        )
        
        db.session.add(new_post)
        db.session.commit()
        
        return {'success': True, 'message': '게시글이 성공적으로 등록되었습니다.', 'post_id': new_post.id}
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}, 500

@main.route('/api/posts/draft', methods=['POST'])
def api_save_draft():
    """임시저장 API"""
    if not current_user.is_authenticated:
        return {'success': False, 'message': '로그인이 필요합니다.'}, 401
    
    try:
        # 임시저장 로직 구현 (실제로는 별도 테이블이나 is_draft 필드 사용)
        return {'success': True, 'message': '임시저장되었습니다.'}
    except Exception as e:
        return {'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}, 500

@main.route('/api/profile/update', methods=['POST'])
def api_update_profile():
    """프로필 수정 API"""
    if not current_user.is_authenticated:
        return {'success': False, 'message': '로그인이 필요합니다.'}, 401
    
    try:
        username = request.form.get('username')
        email = request.form.get('email')
        bio = request.form.get('bio')
        
        current_user.username = username
        current_user.email = email
        # current_user.bio = bio  # bio 필드가 있다면
        
        db.session.commit()
        return {'success': True, 'message': '프로필이 수정되었습니다.'}
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}, 500

@main.route('/api/profile/change-password', methods=['POST'])
def api_change_password():
    """비밀번호 변경 API"""
    if not current_user.is_authenticated:
        return {'success': False, 'message': '로그인이 필요합니다.'}, 401
    
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        # 현재 비밀번호 확인
        if not check_password_hash(current_user.password, current_password):
            return {'success': False, 'message': '현재 비밀번호가 일치하지 않습니다.'}, 400
        
        # 새 비밀번호 설정
        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        
        return {'success': True, 'message': '비밀번호가 변경되었습니다.'}
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}, 500

@main.route('/community')
def community():
    """커뮤니티 페이지 (새 디자인)"""
    return redirect(url_for('main.new_community'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 페이지 및 처리"""
    if request.method == 'GET':
        # 이미 로그인된 사용자는 메인 페이지로 리다이렉트
        if current_user.is_authenticated:
            return redirect(url_for('main.new_index'))
        return redirect(url_for('main.new_login'))
    
    # POST 요청 - 로그인 처리
    try:
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        
        if not user_id or not password:
            flash('아이디와 비밀번호를 입력해주세요.')
            return redirect(url_for('main.new_login'))
        
        user = User.query.filter_by(username=user_id).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('로그인되었습니다.')
            return redirect(url_for('main.new_index'))
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.')
            return redirect(url_for('main.new_login'))
            
    except Exception as e:
        flash(f'오류가 발생했습니다: {str(e)}')
        return redirect(url_for('main.new_login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    """회원가입 페이지 및 처리"""
    if request.method == 'GET':
        # 이미 로그인된 사용자는 메인 페이지로 리다이렉트
        if current_user.is_authenticated:
            return redirect(url_for('main.new_index'))
        return redirect(url_for('main.new_register'))
    
    # POST 요청 - 회원가입 처리
    try:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        if not all([username, email, password, password_confirm]):
            flash('모든 필드를 입력해주세요.')
            return redirect(url_for('main.new_register'))
            
        if password != password_confirm:
            flash('비밀번호가 일치하지 않습니다.')
            return redirect(url_for('main.new_register'))
        
        # 중복 확인
        if User.query.filter_by(username=username).first():
            flash('이미 사용 중인 아이디입니다.')
            return redirect(url_for('main.new_register'))
        
        if User.query.filter_by(email=email).first():
            flash('이미 사용 중인 이메일입니다.')
            return redirect(url_for('main.new_register'))
        
        # 새 사용자 생성
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('회원가입이 완료되었습니다. 로그인해주세요.')
        return redirect(url_for('main.new_login'))
            
    except Exception as e:
        flash(f'오류가 발생했습니다: {str(e)}')
        return redirect(url_for('main.new_register'))

# 실제 로그인/회원가입 처리
@main.route('/api/login', methods=['POST'])
def api_login():
    """로그인 처리 API"""
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return {'success': False, 'message': '아이디와 비밀번호를 입력해주세요.'}, 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return {'success': True, 'message': '로그인되었습니다.'}
        else:
            return {'success': False, 'message': '아이디 또는 비밀번호가 올바르지 않습니다.'}, 401
            
    except Exception as e:
        return {'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}, 500

@main.route('/api/register', methods=['POST'])
def api_register():
    """회원가입 처리 API"""
    try:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not all([username, email, password]):
            return {'success': False, 'message': '모든 필드를 입력해주세요.'}, 400
        
        # 중복 확인
        if User.query.filter_by(username=username).first():
            return {'success': False, 'message': '이미 사용 중인 아이디입니다.'}, 400
        
        if User.query.filter_by(email=email).first():
            return {'success': False, 'message': '이미 사용 중인 이메일입니다.'}, 400
        
        # 새 사용자 생성
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            created_at=get_kst_time()
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return {'success': True, 'message': '회원가입이 완료되었습니다.'}
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}, 500

@main.route('/api/check-username', methods=['POST'])
def api_check_username():
    """아이디 중복 확인 API"""
    username = request.form.get('username')
    
    if not username:
        return {'available': False, 'message': '아이디를 입력해주세요.'}
    
    if len(username) < 3:
        return {'available': False, 'message': '아이디는 3자 이상이어야 합니다.'}
    
    if User.query.filter_by(username=username).first():
        return {'available': False, 'message': '이미 사용 중인 아이디입니다.'}
    
    return {'available': True, 'message': '사용 가능한 아이디입니다.'}

# 새 디자인 페이지들
@main.route('/new')
def new_index():
    """새 디자인 메인 페이지"""
    try:
        # 최신 게시글 가져오기
        latest_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
        # 인기 게시글 (조회수 기준)
        popular_posts = Post.query.order_by(Post.views.desc()).limit(5).all()
        
        return render_template('new_index.html', 
                             latest_posts=latest_posts,
                             popular_posts=popular_posts)
    except Exception as e:
        import traceback
        error_msg = f"Error in new_index: {e}\n{traceback.format_exc()}"
        print(error_msg)
        return f"<h1>에러 발생</h1><pre>{error_msg}</pre>"

@main.route('/new/community')
def new_community():
    """새 디자인 커뮤니티 페이지"""
    page = request.args.get('page', 1, type=int)
    board_type = request.args.get('board_type', '전체')
    search = request.args.get('search', '')
    
    # 검색 및 필터링 로직
    query = Post.query
    
    if board_type != '전체':
        query = query.filter_by(board_type=board_type)
    
    if search:
        query = query.filter(Post.title.contains(search) | Post.content.contains(search))
    
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 게시판 유형들
    board_types = ['전체', '일반', '질문', '정보', '취업', '자유']
    
    return render_template('new_community.html', 
                         posts=posts,
                         board_types=board_types,
                         current_board_type=board_type,
                         search=search)

@main.route('/new/login')
def new_login():
    """새 디자인 로그인 페이지"""
    return render_template('new_login.html')

@main.route('/new/register')
def new_register():
    """새 디자인 회원가입 페이지"""
    return render_template('new_register.html')

@main.route('/new/post')
@login_required
def new_post_page():
    """새 디자인 게시글 작성 페이지"""
    return render_template('new_post.html')

# 글 작성 페이지
@main.route('/create_post', methods=['GET', 'POST'])
def create_post():
    """새 글 작성"""
    if request.method == 'POST':
        try:
            board_type = request.form['board_type']
            title = request.form['title']
            content = request.form['content']
            price = request.form.get('price')  # 중고거래용 가격 (선택적)
            
            # 유효성 검사
            if not board_type or not title or not content:
                flash('모든 필수 항목을 입력해주세요.')
                return render_template('new_post.html')
            
            # 새 게시글 생성
            new_post = Post(
                per_id=str(uuid.uuid4()),  # 고유 ID 생성
                title=title,
                content=content,
                board_type=board_type,
                price=int(price) if price and price.strip() else None,
                author='temp_user',  # 추후 로그인된 사용자로 변경
                views=0,
                likes=0,
                dislikes=0,
                created_at=datetime.utcnow()
            )
            
            db.session.add(new_post)
            db.session.commit()
            
            flash('글이 성공적으로 작성되었습니다!')
            return redirect(url_for('main.new_community'))
            
        except Exception as e:
            flash(f'글 작성 중 오류가 발생했습니다: {str(e)}')
            return render_template('new_post.html')
    
    return render_template('new_post.html')

# 추가 API 엔드포인트들
@main.route('/api/posts/<int:post_id>/like', methods=['POST'])
def api_like_post(post_id):
    """게시글 좋아요 API"""
    if not current_user.is_authenticated:
        return {'success': False, 'message': '로그인이 필요합니다.'}, 401
    
    try:
        post = Post.query.get_or_404(post_id)
        # 좋아요 로직 구현 (실제로는 Like 테이블 필요)
        # 여기서는 단순히 좋아요 수만 증가
        post.likes = (post.likes or 0) + 1
        db.session.commit()
        
        return {'success': True, 'likes_count': post.likes}
    except Exception as e:
        return {'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}, 500

@main.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def api_add_comment(post_id):
    """댓글 작성 API"""
    if not current_user.is_authenticated:
        return {'success': False, 'message': '로그인이 필요합니다.'}, 401
    
    try:
        content = request.form.get('content')
        if not content:
            return {'success': False, 'message': '댓글 내용을 입력해주세요.'}, 400
        
        new_comment = Comment(
            content=content,
            author_id=current_user.id,
            post_id=post_id,
            created_at=get_kst_time()
        )
        
        db.session.add(new_comment)
        db.session.commit()
        
        return {'success': True, 'message': '댓글이 작성되었습니다.', 'comment_id': new_comment.id}
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}, 500

@main.route('/api/comments/<int:comment_id>/delete', methods=['DELETE'])
def api_delete_comment(comment_id):
    """댓글 삭제 API"""
    if not current_user.is_authenticated:
        return {'success': False, 'message': '로그인이 필요합니다.'}, 401
    
    try:
        comment = Comment.query.get_or_404(comment_id)
        
        if comment.author_id != current_user.id:
            return {'success': False, 'message': '삭제 권한이 없습니다.'}, 403
        
        db.session.delete(comment)
        db.session.commit()
        
        return {'success': True, 'message': '댓글이 삭제되었습니다.'}
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}, 500

@main.route('/api/posts/<int:post_id>/delete', methods=['DELETE'])
def api_delete_post(post_id):
    """게시글 삭제 API"""
    if not current_user.is_authenticated:
        return {'success': False, 'message': '로그인이 필요합니다.'}, 401
    
    try:
        post = Post.query.get_or_404(post_id)
        
        if post.author_id != current_user.id:
            return {'success': False, 'message': '삭제 권한이 없습니다.'}, 403
        
        # 관련 댓글들도 삭제
        Comment.query.filter_by(post_id=post_id).delete()
        db.session.delete(post)
        db.session.commit()
        
        return {'success': True, 'message': '게시글이 삭제되었습니다.'}
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}, 500

@main.route('/api/search', methods=['GET'])
def api_search():
    """검색 API"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    board_type = request.args.get('board_type', '')
    
    if not query:
        return {'success': False, 'message': '검색어를 입력해주세요.'}, 400
    
    try:
        # 검색 쿼리 빌드
        search_query = Post.query.filter(
            Post.title.contains(query) | Post.content.contains(query)
        )
        
        if board_type:
            search_query = search_query.filter_by(board_type=board_type)
        
        posts = search_query.order_by(Post.created_at.desc()).paginate(
            page=page, per_page=10, error_out=False
        )
        
        results = []
        for post in posts.items:
            results.append({
                'id': post.id,
                'title': post.title,
                'content': post.content[:100] + '...' if len(post.content) > 100 else post.content,
                'author': post.author.username if post.author else 'Unknown',
                'created_at': post.created_at.strftime('%Y-%m-%d %H:%M'),
                'views': post.views or 0,
                'likes': post.likes or 0
            })
        
        return {
            'success': True,
            'results': results,
            'total': posts.total,
            'pages': posts.pages,
            'current_page': posts.page
        }
        
    except Exception as e:
        return {'success': False, 'message': f'오류가 발생했습니다: {str(e)}'}, 500

# 에러 핸들러들
@main.errorhandler(404)
def page_not_found(e):
    return render_template('new_base.html'), 404

@main.errorhandler(500)
def internal_server_error(e):
    return render_template('new_base.html'), 500

# 기본 데이터 생성
@main.route('/init-data')
def init_data():
    """기본 데이터 생성 (개발용)"""
    try:
        # 샘플 게시글 생성
        if Post.query.count() == 0:
            sample_posts = [
                Post(title="방통대 컴퓨터과학과 신입생을 위한 가이드", content="신입생들을 위한 유용한 정보들을 공유합니다.", 
                     board_type="정보", author_id=1, views=150, likes=12),
                Post(title="프로그래밍 스터디 모집", content="함께 공부할 스터디원을 모집합니다.", 
                     board_type="일반", author_id=1, views=89, likes=7),
                Post(title="취업 면접 후기", content="IT 기업 면접 후기를 공유합니다.", 
                     board_type="취업", author_id=1, views=234, likes=18),
            ]
            for post in sample_posts:
                db.session.add(post)
        
        db.session.commit()
        flash('기본 데이터가 생성되었습니다!')
        return redirect(url_for('main.new_index'))
    except Exception as e:
        flash(f'데이터 생성 중 오류: {str(e)}')
        return redirect(url_for('main.new_index'))

# 테스트용 간단한 라우트
@main.route('/test')
def test():
    """테스트 페이지"""
    return '<h1>테스트 성공!</h1><p>앱이 정상 작동합니다.</p>'

@main.route('/new-simple')
def new_simple():
    """간단한 테스트 페이지"""
    return "<h1>간단한 테스트 페이지입니다</h1><p>이 페이지가 보이면 라우팅은 정상입니다.</p>"
