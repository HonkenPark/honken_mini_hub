# LoL Store Scraper API

League of Legends 스토어의 할인 정보를 스크래핑하고 제공하는 FastAPI 기반의 웹 애플리케이션입니다.

## 프로젝트 구조

```
.
├── app/                    # 메인 애플리케이션 코드
│   ├── api/               # API 엔드포인트 정의
│   │   └── v1/           # API 버전 1
│   │       ├── endpoints/# 각 API 엔드포인트 구현
│   │       └── router.py # API 라우터 설정
│   ├── core/             # 핵심 설정 및 구성 파일
│   ├── models/           # 데이터 모델 정의
│   ├── services/         # 비즈니스 로직 처리
│   ├── utils/            # 유틸리티 함수
│   └── main.py           # FastAPI 애플리케이션 진입점
├── data/                 # 데이터 저장 디렉토리
├── tests/               # 테스트 코드
├── requirements.txt     # 프로젝트 의존성
└── scraping_results.json # 스크래핑 결과 저장
```

## 주요 기능

- League of Legends 스토어의 할인 정보 자동 스크래핑
- RESTful API를 통한 할인 정보 제공
- 스케줄러를 통한 주기적인 데이터 업데이트

## API 엔드포인트

- `GET /`: API 기본 정보
- `GET /discounts`: 현재 할인 정보 조회
- `GET /api/v1/lol-store/discounts`: 할인 정보 조회
- `GET /api/v1/lol-store/last-update`: 마지막 스크래핑 시간 조회

## 기술 스택

- FastAPI: 웹 프레임워크
- Playwright: 웹 스크래핑
- APScheduler: 스케줄링
- Python-dotenv: 환경 변수 관리
- Uvicorn: ASGI 서버

## 설치 및 실행

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