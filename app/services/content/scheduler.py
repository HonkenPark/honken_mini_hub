from datetime import datetime
import pytz
from app.services.lol_store.store import LoLStoreService
from app.services.content.generator import ContentGeneratorService
from app.services.content.publisher import YouTubePublisherService

class ContentScheduler:
    def __init__(self):
        self.store_service = LoLStoreService()
        self.content_generator = ContentGeneratorService()
        self.youtube_publisher = YouTubePublisherService()

    async def run_weekly_update(self):
        """
        Run the complete weekly update process:
        1. Scrape discount information
        2. Generate content (images and video)
        3. Publish to YouTube
        """
        # 1. 스크래핑
        discounts = await self.store_service.update_discounts()
        if not discounts:
            print("No discounts found, skipping content generation")
            return

        # 2. 콘텐츠 생성
        data = {
            "last_update": self.store_service.last_update,
            "discounts": discounts
        }
        image_paths, video_path = self.content_generator.generate_content(data)
        print(f"Generated {len(image_paths)} images and video: {video_path}")

        # 3. YouTube 업로드
        video_id = self.youtube_publisher.publish_video(video_path)
        if video_id:
            print(f"Successfully uploaded video to YouTube. Video ID: {video_id}")
        else:
            print("Failed to upload video to YouTube") 