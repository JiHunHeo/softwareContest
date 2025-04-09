import os
from git import Repo
from datetime import datetime

def summarize_repository(repo_path):
    # �젅�룷吏��넗由� �뿴湲�
    repo = Repo(repo_path)
    
    if repo.bare:
        print("�젅�룷吏��넗由ш�� 鍮꾩뼱 �엳�뒿�땲�떎.")
        return

    # �젅�룷吏��넗由� �깮�꽦 �궇吏� (理쒖큹 而ㅻ컠 �궇吏�)
    first_commit = next(repo.iter_commits('master', max_count=1))
    creation_date = datetime.fromtimestamp(first_commit.committed_date).strftime('%Y-%m-%d %H:%M:%S')

    # 釉뚮옖移� 紐⑸줉
    branches = [branch.name for branch in repo.branches]

    # 而ㅻ컠 �슂�빟
    commits = []
    for commit in repo.iter_commits('--all'):
        commits.append({
            "hash": commit.hexsha[:7],
            "author": commit.author.name,
            "date": datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M:%S'),
            "message": commit.message.strip(),
            "branch": [branch.name for branch in repo.branches if commit in repo.iter_commits(branch.name)]
        })

    # 異쒕젰
    print(f"�젅�룷吏��넗由� �깮�꽦 �궇吏�: {creation_date}")
    print(f"釉뚮옖移� 紐⑸줉: {', '.join(branches)}")
    print("\n而ㅻ컠 �슂�빟:")
    for commit in commits:
        print(f"- [{commit['date']}] {commit['author']} ({', '.join(commit['branch'])})")
        print(f"  硫붿떆吏�: {commit['message']}")
        print(f"  �빐�떆: {commit['hash']}")
        print()

if __name__ == "__main__":
    # �젅�룷吏��넗由� 寃쎈줈 �꽕�젙
    repo_path = os.path.abspath(".")  # �쁽�옱 �뵒�젆�넗由�
    summarize_repository(repo_path)