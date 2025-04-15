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

@main.route('/samplegrid', methods=['GET', 'POST'])
def samplegrid():
    if request.method == 'GET':
    # 그리드 컬럼 선언
    # 데이터 형식을 맞추고 width 조정 가능 
    # *(그리드 자체 width 값이 auto 로 설정 되어 있어 특정 width 수정이 필요한 컬럼만 수정)
        columns = [
            {"label": "순번", "key": "idx", "width": "30px"},
            {"label": "날짜", "key": "date",},
            {"label": "제목", "key": "title","width": "400px"},
            # {"label": "내용", "key": "content"},
            {"label": "작성자", "key": "writer"}
        ]
    # 그리드 샘플 json 데이터 추후 DB 데이터 가져오는 것으로 변경예정
        data = get_commits_from_file("gridsampledata.json")

        return render_template('samplegrid.html', table_id="samplegrid", columns=columns, data=data)
    elif request.method == 'POST':
        # 게시판 세부 내용을 볼 수 있는 화면 랜더
        return jsonify({"success": True})
