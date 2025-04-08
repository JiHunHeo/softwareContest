import json
from git import Repo

def export_commits_to_json(repo_path, output_file):
    try:
        repo = Repo(repo_path)
        commits = [
            {
                "hash": commit.hexsha[:7],
                "author": commit.author.name,
                "date": commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                "message": commit.message.strip(),
            }
            for commit in repo.iter_commits('master')  # 'master' 브랜치의 모든 커밋
        ]

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(commits, f, ensure_ascii=False, indent=4)
        print(f"커밋 정보가 {output_file}에 저장되었습니다.")
    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    export_commits_to_json(".", "commits.json")