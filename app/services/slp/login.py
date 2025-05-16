import requests
import os
from dotenv import load_dotenv

class SLPLoginService:
    def __init__(self):
        # .env.slp 파일 로드
        load_dotenv('.env.slp')
        
        # 환경 변수에서 ID와 비밀번호 불러오기
        self.user_id = os.getenv("USER_ID")
        self.password = os.getenv("PWD")

    def login(self):
        # 로그인 요청
        url = "https://www.eduslp.ac.kr/member/login_ok.php"
        data = {
            "ret_url": "",
            "remember_id": "Y",
            "USER_ID": self.user_id,
            "PWD": self.password,
            "REMEMBER_ME": "on"
        }

        session = requests.Session()
        response = session.post(url, data=data)

        # 응답 확인
        print("Status Code:", response.status_code)
        print("Response URL:", response.url)
        print("Response Text:", response.text[:500])  # 응답 일부 출력
        
        return session

if __name__ == "__main__":
    service = SLPLoginService()
    service.login()
