import json
from flask import Blueprint, render_template, request

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

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
