import requests
from bs4 import BeautifulSoup
from models import Notice
from extensions import db
from datetime import datetime

def crawl_notices(url):
    """
    주어진 URL에서 공지사항 데이터를 크롤링하고 데이터베이스에 저장합니다.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
        soup = BeautifulSoup(response.text, 'html.parser')

        # 공지사항 데이터 추출 (HTML 구조에 따라 수정 필요)
        notices = soup.find_all('div', class_='notice-item')
        for notice in notices:
            title = notice.find('h2').text.strip()
            content = notice.find('p').text.strip()
            source_url = notice.find('a')['href']

            # 중복 데이터 방지
            if not Notice.query.filter_by(title=title).first():
                new_notice = Notice(
                    title=title,
                    content=content,
                    source_url=source_url,
                    created_at=datetime.utcnow()
                )
                db.session.add(new_notice)
        db.session.commit()
        print("크롤링 완료!")
    except requests.exceptions.RequestException as e:
        print(f"크롤링 중 오류 발생: {e}")