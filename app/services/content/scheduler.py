from datetime import datetime, timedelta
import pytz
from app.services.lol_store.store import LoLStoreService
from app.services.content.generator import ContentGeneratorService
from app.services.content.publisher import YouTubePublisherService

class ContentScheduler:
    def __init__(self):
        self.store_service = LoLStoreService()
        self.content_generator = ContentGeneratorService()
        self.youtube_publisher = YouTubePublisherService()

    def _generate_description(self, discounts: list) -> str:
        """
        Generate YouTube video description from discounts data
        
        Args:
            discounts: List of discount information
            
        Returns:
            str: Formatted description text
        """
        current_date = datetime.now(pytz.timezone('Asia/Seoul'))
        end_date = current_date + timedelta(days=7)
        description = f"주간 롤 스킨 할인 정보 ({current_date.strftime('%m월 %d일')} ~ {end_date.strftime('%m월 %d일')})\n\n"
        
        # 할인 정보 추가
        for discount in discounts:
            description += f"{discount['name']} → {discount['price']} ({discount['discount']})\n"
        
        return description

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
        description = self._generate_description(discounts)
        video_id = self.youtube_publisher.publish_video(video_path, description=description)
        if video_id:
            print(f"Successfully uploaded video to YouTube. Video ID: {video_id}")
        else:
            print("Failed to upload video to YouTube") 