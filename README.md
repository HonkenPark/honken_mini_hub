# Honken Mini Hub

To supply private services this project is created by FastAPI

## 프로젝트 구조

```
.
├── app/                    # 메인 애플리케이션 코드
│   ├── api/               # API 엔드포인트 정의
│   │   └── v1/           # API 버전 1
│   │       ├── endpoints/# 각 API 엔드포인트 구현
│   │       └── router.py # API 라우터 설정
│   ├── core/             # 핵심 설정 및 구성 파일
│   │   ├── config/       # 설정 파일 (YouTube API 등)
│   │   └── scheduler.py  # 스케줄러 설정
│   ├── models/           # 데이터 모델 정의
│   ├── services/         # 비즈니스 로직 처리
│   │   ├── lol_store/    # LoL 스토어 관련 서비스
│   │   │   ├── __init__.py
│   │   │   └── store.py  # 스토어 스크래핑 로직
│   │   └── youtube/      # YouTube 관련 서비스
│   │       ├── __init__.py
│   │       └── uploader.py # 비디오 업로드 로직
│   ├── static/           # 정적 파일 (CSS, JS)
│   │   ├── css/         # CSS 스타일시트
│   │   └── js/          # JavaScript 파일
│   ├── templates/        # HTML 템플릿
│   ├── utils/            # 유틸리티 함수
│   └── main.py           # FastAPI 애플리케이션 진입점
├── data/                 # 데이터 저장 디렉토리
│   └── exception_results.json # 예외 처리 결과
├── tests/               # 테스트 코드
├── requirements.txt     # 프로젝트 의존성
├── restart.sh          # 도커 재시작 스크립트
└── README.md           # 프로젝트 문서
```

## 주요 기능

- League of Legends 스토어의 주간 스킨 할인 정보 취합
- 취합된 정보의 이미지 및 영상화 후 유튜브에 게시
- 스케줄러를 통한 주기적인 데이터 업데이트
- 웹 인터페이스를 통한 API 정보 및 서비스 상태 확인

## 웹 인터페이스

- `GET /`: 메인 페이지 (HTML)
  - API 정보 표시
  - 실시간 서버 상태 확인
  - 반응형 디자인

## API 엔드포인트

- `GET /api/v1/lol-store/discounts`: 할인 정보 조회
- `GET /api/v1/lol-store/last-update`: 마지막 스크래핑 시간 조회

## 기술 스택

- FastAPI: 웹 프레임워크
- Playwright: 웹 스크래핑
- APScheduler: 스케줄링
- Python-dotenv: 환경 변수 관리
- Uvicorn: ASGI 서버
- Google API Client: YouTube API 연동
- OAuth2Client: YouTube 인증
- HTML5/CSS3: 웹 인터페이스
- JavaScript: 동적 웹 기능
- Docker: 컨테이너화

## 설치 및 실행

### 도커를 사용한 실행

1. 도커 이미지 빌드 및 실행:
```bash
./restart.sh
```

이 스크립트는 다음 작업을 자동으로 수행합니다:
- 기존 컨테이너 중지 및 삭제
- 기존 이미지 삭제
- 새 이미지 빌드
- 새 컨테이너 실행
- 컨테이너 로그 표시

### 개발 모드 실행

1. 의존성 설치:
```bash
pip install -r requirements.txt
```

2. 서버 실행:
```bash
uvicorn app.main:app --reload
```

## 개발 모드 옵션

- `--reload`: 코드 변경 시 자동 재시작
- `--host 0.0.0.0`: 외부 접근 허용
- `--port 8000`: 포트 지정 (기본값: 8000)
- `--workers 4`: 워커 프로세스 수 지정

예시:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
``` 