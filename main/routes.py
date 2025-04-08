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
    return render_template('timeline.html', commits=commits)