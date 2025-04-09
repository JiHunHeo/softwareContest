import os
from git import Repo
from datetime import datetime

def summarize_repository(repo_path):
    # 레포지토리 열기
    repo = Repo(repo_path)
    
    if repo.bare:
        print("레포지토리가 비어 있습니다.")
        return

    # 레포지토리 생성 날짜 (최초 커밋 날짜)
    first_commit = next(repo.iter_commits('master', max_count=1))
    creation_date = datetime.fromtimestamp(first_commit.committed_date).strftime('%Y-%m-%d %H:%M:%S')

    # 브랜치 목록
    branches = [branch.name for branch in repo.branches]

    # 커밋 요약
    commits = []
    for commit in repo.iter_commits('--all'):
        commits.append({
            "hash": commit.hexsha[:7],
            "author": commit.author.name,
            "date": datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M:%S'),
            "message": commit.message.strip(),
            "branch": [branch.name for branch in repo.branches if commit in repo.iter_commits(branch.name)]
        })

    # 출력
    print(f"레포지토리 생성 날짜: {creation_date}")
    print(f"브랜치 목록: {', '.join(branches)}")
    print("\n커밋 요약:")
    for commit in commits:
        print(f"- [{commit['date']}] {commit['author']} ({', '.join(commit['branch'])})")
        print(f"  메시지: {commit['message']}")
        print(f"  해시: {commit['hash']}")
        print()

if __name__ == "__main__":
    # 레포지토리 경로 설정
    repo_path = os.path.abspath(".")  # 현재 디렉토리
    summarize_repository(repo_path)