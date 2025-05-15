from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from datetime import datetime, timedelta
import pytz
import os
from pathlib import Path

class DiscountImageGenerator:
    def __init__(self):
        self.output_dir = Path("data/images")
        self.output_dir.mkdir(exist_ok=True)
        self.rp_icon_path = Path("app/services/image_generator/templates/icon_rp.png")
        
        # 폰트 설정
        self.title_font = ImageFont.truetype("app/services/image_generator/fonts/GamjaFlower-Regular.ttf", 68)
        self.date_font = ImageFont.truetype("app/services/image_generator/fonts/GamjaFlower-Regular.ttf", 92)
        self.name_font = ImageFont.truetype("app/services/image_generator/fonts/GamjaFlower-Regular.ttf", 64)
        self.price_font = ImageFont.truetype("app/services/image_generator/fonts/GamjaFlower-Regular.ttf", 62   )

    def _create_template(self):
        """Create a template image with gradient background"""
        width, height = 1280, 2266
        template = Image.new('RGB', (width, height), color='#000000')
        draw = ImageDraw.Draw(template)
        return template

    def _get_date_range(self):
        """Get current date and date after 7 days in KST"""
        kst = pytz.timezone('Asia/Seoul')
        now = datetime.now(kst)
        end_date = now + timedelta(days=7)
        return now.strftime("%Y.%m.%d"), end_date.strftime("%Y.%m.%d")

    def _download_image(self, url):
        """Download image from URL"""
        response = requests.get(url)
        return Image.open(BytesIO(response.content))

    def _resize_image(self, image, max_size=(1280, 1280)):
        """Resize image maintaining aspect ratio"""
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image

    def generate_discount_image(self, skin_data, index):
        """Generate discount image for a single skin"""
        # 템플릿 이미지 생성
        template = self._create_template()
        draw = ImageDraw.Draw(template)

        # 날짜 범위 가져오기
        start_date, end_date = self._get_date_range()
        date_text = f"{start_date} ~ {end_date}"
        title_text = "주간 롤 스킨 할인 정보"

        # 날짜와 제목 텍스트 그리기
        date_bbox = draw.textbbox((0, 0), date_text, font=self.date_font)
        title_bbox = draw.textbbox((0, 0), title_text, font=self.title_font)
        
        date_width = date_bbox[2] - date_bbox[0]
        title_width = title_bbox[2] - title_bbox[0]
        
        draw.text(((template.width - date_width) // 2, 420), date_text, font=self.date_font, fill="white")
        draw.text(((template.width - title_width) // 2, 560), title_text, font=self.title_font, fill="#FFD700")  # 노란색

        # 스킨 이미지 다운로드 및 배치
        skin_image = self._download_image(skin_data["url"])
        skin_image = self._resize_image(skin_image)
        skin_pos = ((template.width - skin_image.width) // 2, (template.height - skin_image.height) // 2)
        template.paste(skin_image, skin_pos)

        # 챔피언 이름 그리기
        name_bbox = draw.textbbox((0, 0), skin_data["name"], font=self.name_font)
        name_width = name_bbox[2] - name_bbox[0]
        draw.text(((template.width - name_width) // 2, 1600), skin_data["name"], font=self.name_font, fill="white")

        # RP 아이콘과 가격 정보 그리기
        rp_icon = Image.open(self.rp_icon_path)
        price_text = f"{skin_data['price']} ({skin_data['discount']})"
        price_bbox = draw.textbbox((0, 0), price_text, font=self.price_font)
        price_width = price_bbox[2] - price_bbox[0]
        
        total_width = rp_icon.width + price_width + 20  # 20은 아이콘과 텍스트 사이 간격
        start_x = (template.width - total_width) // 2
        
        template.paste(rp_icon, (start_x, 1710), rp_icon)
        draw.text((start_x + rp_icon.width + 20, 1705), price_text, font=self.price_font, fill="white")

        # 이미지 저장
        output_path = self.output_dir / f"{index:02d}.png"
        template.save(output_path)
        return output_path

    def generate_all_images(self, skins_data):
        """Generate images for all skins"""
        # 기존 이미지 파일 삭제
        for file in self.output_dir.glob("*.png"):
            try:
                file.unlink()
            except Exception as e:
                print(f"Error deleting file {file}: {e}")

        generated_paths = []
        for i, skin in enumerate(skins_data["discounts"], 1):
            path = self.generate_discount_image(skin, i)
            generated_paths.append(path)
        return generated_paths 