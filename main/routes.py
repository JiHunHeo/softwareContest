from flask import Blueprint, render_template, request
from git import Repo
from datetime import datetime

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/timeline')
def timeline():
    repo_path = '.'  # 현재 레포지토리 경로
    commits = get_git_commits(repo_path)

    # 페이지네이션
    page = int(request.args.get('page', 1))  # 현재 페이지 (기본값: 1)
    per_page = 10  # 페이지당 커밋 수
    start = (page - 1) * per_page
    end = start + per_page
    paginated_commits = commits[start:end]

    total_pages = (len(commits) + per_page - 1) // per_page  # 전체 페이지 수 계산

    return render_template(
        'timeline.html',
        commits=paginated_commits,
        page=page,
        total_pages=total_pages
    )

# Git 커밋 데이터를 가져오는 함수
def get_git_commits(repo_path):
    repo = Repo(repo_path)
    commits = []
    for commit in repo.iter_commits('master'):  # 모든 커밋 가져오기
        commits.append({
            "hash": commit.hexsha[:7],  # 커밋 해시 (짧게)
            "author": commit.author.name,  # 작성자
            "date": datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M:%S'),  # 커밋 날짜
            "message": commit.message.strip()  # 커밋 메시지
        })
    return commits