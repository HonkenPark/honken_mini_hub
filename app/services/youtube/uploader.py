import http.client as httplib
import httplib2
import random
import time
from typing import Optional, List
import json

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

from app.core.config.youtube_config import (
    YOUTUBE_UPLOAD_SCOPE,
    YOUTUBE_API_SERVICE_NAME,
    YOUTUBE_API_VERSION,
    CLIENT_SECRETS_FILE,
    OAUTH2_FILE,
    MAX_RETRIES,
    MISSING_CLIENT_SECRETS_MESSAGE,
    VALID_PRIVACY_STATUSES
)

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from app.core.config.settings import settings

# HTTP 관련 설정
httplib2.RETRIES = 1

# 재시도할 예외 목록
RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error,
    IOError,
    httplib.NotConnected,
    httplib.IncompleteRead,
    httplib.ImproperConnectionState,
    httplib.CannotSendRequest,
    httplib.CannotSendHeader,
    httplib.ResponseNotReady,
    httplib.BadStatusLine
)

# 재시도할 HTTP 상태 코드
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

class YouTubeUploader:
    def __init__(self):
        self.credentials = None
        self.youtube = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with YouTube API"""
        if os.path.exists(OAUTH2_FILE):
            with open(OAUTH2_FILE, 'r') as f:
                credentials_data = json.load(f)
                self.credentials = Credentials.from_authorized_user_info(credentials_data)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE,
                [YOUTUBE_UPLOAD_SCOPE]
            )
            self.credentials = flow.run_local_server(port=0)
            
            # Save credentials
            with open(OAUTH2_FILE, 'w') as f:
                json.dump(self.credentials.to_json(), f)

        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=self.credentials)

    def upload_video(
        self,
        file_path: str,
        title: str,
        description: str = "",
        category: str = "22",
        keywords: Optional[List[str]] = None,
        privacy_status: str = "public"
    ) -> Optional[str]:
        """
        비디오를 YouTube에 업로드합니다.

        Args:
            file_path: 업로드할 비디오 파일 경로
            title: 비디오 제목
            description: 비디오 설명
            category: 비디오 카테고리 ID
            keywords: 비디오 키워드 리스트
            privacy_status: 비디오 공개 상태 (public, private, unlisted)

        Returns:
            업로드된 비디오의 ID 또는 실패 시 None
        """
        if privacy_status not in VALID_PRIVACY_STATUSES:
            raise ValueError(f"privacy_status must be one of {VALID_PRIVACY_STATUSES}")

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": keywords or [],
                "categoryId": category
            },
            "status": {
                "privacyStatus": privacy_status
            }
        }

        insert_request = self.youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
        )

        return self._resumable_upload(insert_request)

    def _resumable_upload(self, insert_request) -> Optional[str]:
        """재시도 가능한 업로드를 수행합니다."""
        response = None
        error = None
        retry = 0

        while response is None:
            try:
                print("Uploading file...")
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        print(f"Video id '{response['id']}' was successfully uploaded.")
                        return response['id']
                    else:
                        print(f"The upload failed with an unexpected response: {response}")
                        return None
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
                else:
                    raise
            except RETRIABLE_EXCEPTIONS as e:
                error = f"A retriable error occurred: {e}"

            if error is not None:
                print(error)
                retry += 1
                if retry > MAX_RETRIES:
                    print("No longer attempting to retry.")
                    return None

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print(f"Sleeping {sleep_seconds} seconds and then retrying...")
                time.sleep(sleep_seconds)

        return None 