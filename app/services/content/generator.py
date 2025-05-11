from typing import List, Dict, Any
from pathlib import Path
from app.services.image_generator.discount_image import DiscountImageGenerator
from app.services.video.video_generator import VideoGenerator

class ContentGeneratorService:
    def __init__(self):
        self.image_generator = DiscountImageGenerator()
        self.video_generator = VideoGenerator()

    def generate_content(self, discounts_data: dict) -> tuple[List[str], str]:
        """
        Generate images and video from discounts data
        
        Args:
            discounts_data: Dictionary containing discounts information
            
        Returns:
            tuple: (list of image paths, video path)
        """
        # 이미지 생성
        image_paths = self.image_generator.generate_all_images(discounts_data)
        
        # 비디오 생성
        video_path = self.video_generator.create_weekly_sale_video(
            image_dir="data/images",
            audio_file="data/audio/bgm.mp3",
            image_duration=3,
            transition_duration=0.5
        )
        
        return image_paths, video_path 