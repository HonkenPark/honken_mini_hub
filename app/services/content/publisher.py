from typing import Optional, List
from datetime import datetime
import pytz
from app.services.youtube.uploader import YouTubeUploader

class YouTubePublisherService:
    def __init__(self):
        self.youtube_uploader = YouTubeUploader()

    def publish_video(self, video_path: str, title: str = None) -> Optional[str]:
        """
        Publish video to YouTube
        
        Args:
            video_path: Path to the video file
            title: Optional custom title. If not provided, a default title with current date will be used
            
        Returns:
            Optional[str]: YouTube video ID if successful, None otherwise
        """
        if title is None:
            current_date = datetime.now(pytz.timezone('Asia/Seoul')).strftime("%m월 %d일")
            title = f"주간 롤 스킨 할인 정보 ({current_date}) #게임 #리그오브레전드 #롤스킨세일 #롤스킨할인 #롤할인 #롤할인스킨"

        return self.youtube_uploader.upload_video(
            file_path=video_path,
            title=title,
            description="",
            privacy_status="public",
            keywords=["게임", "리그오브레전드", "롤스킨세일", "롤스킨할인", "롤할인", "롤할인스킨"]
        ) 