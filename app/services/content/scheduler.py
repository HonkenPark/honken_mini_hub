from datetime import datetime, timedelta
import pytz
from app.services.lol_store.store import LoLStoreService
from app.services.content.generator import ContentGeneratorService
from app.services.content.publisher import YouTubePublisherService
from app.services.slp.login import SLPLoginService

class ContentScheduler:
    def __init__(self):
        self.store_service = LoLStoreService()
        self.content_generator = ContentGeneratorService()
        self.youtube_publisher = YouTubePublisherService()
        self.slp_login = SLPLoginService()
        
    def _login_to_slp(self):
        """
        Login to SLP (Student Life Portal)
        """
        self.slp_login.login()
        
        
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
        
        # 영상 링크 추가
        description += "\n\n지난 할인 보기: https://www.youtube.com/playlist?list=PLOjGkLv4hSDB54IOZlae8NXw69sjrEoZi"
        
        # 해시 태그 추가
        description += "\n\n#롤스킨할인 #롤스킨세일 #롤할인 #롤할인스킨 #롤스킨 #스킨할인 #게임 #리그오브레전드"
        return description
    
    async def create_exception_list(self):
        """
        Create exception list from exception discounts data
        """
        discounts = await self.store_service.update_exception_discounts()
        if not discounts:
            print("No discounts found. Exception list creation skipped.")
        else:
            print("Exception list is created.")
        return
        

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