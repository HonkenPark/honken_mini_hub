import os
from pathlib import Path

# API 설정
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# 파일 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "app", "core", "config", "client_secrets.json")
OAUTH2_FILE = os.path.join(BASE_DIR, "app", "core", "config", "oauth2.json")

# 업로드 설정
MAX_RETRIES = 10
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

# 에러 메시지
MISSING_CLIENT_SECRETS_MESSAGE = f"""
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   {CLIENT_SECRETS_FILE}

with information from the API Console
https://console.cloud.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" 