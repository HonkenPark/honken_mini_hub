import os
from pathlib import Path
from typing import Optional, List
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips, AudioFileClip, vfx
import logging

logger = logging.getLogger(__name__)

class VideoGenerator:
    """비디오 생성 서비스 클래스"""
    
    def __init__(self, output_dir: str = "data/videos"):
        """
        Args:
            output_dir (str): 생성된 비디오가 저장될 디렉토리 경로
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_video_from_images(
        self,
        image_dir: str,
        output_filename: str,
        image_duration: int = 3,
        audio_file: Optional[str] = None,
        transition_duration: float = 0.5
    ) -> str:
        """
        이미지 시퀀스로부터 비디오를 생성합니다.
        
        Args:
            image_dir (str): 이미지 파일들이 있는 디렉토리 경로
            output_filename (str): 출력될 비디오 파일 이름
            image_duration (int): 각 이미지가 표시될 시간(초)
            audio_file (str, optional): 배경음악 파일 경로
            transition_duration (float): 전환 효과 지속 시간(초)
            
        Returns:
            str: 생성된 비디오 파일의 경로
            
        Raises:
            ValueError: 이미지 파일이 없거나 처리 중 오류가 발생한 경우
        """
        try:
            # 이미지 파일 목록 가져오기
            image_files = [f for f in Path(image_dir).glob("*") 
                         if f.suffix.lower() in ('.png', '.jpg', '.jpeg')]
            
            if not image_files:
                raise ValueError(f"'{image_dir}' 디렉토리에 이미지 파일이 없습니다.")
            
            # 이미지 파일들을 정렬
            image_files.sort()
            
            # 이미지 클립 생성 및 연결
            clips = []
            for image_path in image_files:
                clip = ImageClip(str(image_path)).set_duration(image_duration)
                clips.append(clip)
            
            # 모든 클립 연결
            final_clip = concatenate_videoclips(clips, method="compose")
            
            # 페이드 인/아웃 효과 추가
            final_clip = final_clip.fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
            
            # 배경 음악 추가
            if audio_file and os.path.exists(audio_file):
                try:
                    logger.info(f"오디오 파일 로드 중: {audio_file}")
                    audio = AudioFileClip(str(audio_file))
                    logger.info(f"오디오 길이: {audio.duration}초, 비디오 길이: {final_clip.duration}초")
                    
                    # 오디오 길이를 비디오 길이에 맞춤
                    if audio.duration > final_clip.duration:
                        audio = audio.subclip(0, final_clip.duration)
                    else:
                        # 오디오가 비디오보다 짧으면 반복
                        audio = audio.loop(duration=final_clip.duration)
                    
                    # 오디오 볼륨 조절 (70%로 설정)
                    audio = audio.volumex(0.7)
                    logger.info("오디오를 비디오에 적용 중...")
                    final_clip = final_clip.set_audio(audio)
                    logger.info("오디오 적용 완료")
                except Exception as e:
                    logger.error(f"오디오 처리 중 오류 발생: {str(e)}")
                    raise
            
            # 출력 파일 경로 생성
            output_path = str(self.output_dir / output_filename)
            
            # 비디오 저장
            logger.info(f"비디오 저장 중: {output_path}")
            final_clip.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                logger=None  # moviepy의 기본 로깅 비활성화
            )
            logger.info("비디오 저장 완료")
            
            # 메모리 정리
            final_clip.close()
            if audio_file and os.path.exists(audio_file):
                audio.close()
            
            return str(output_path)
            
        except Exception as e:
            raise ValueError(f"비디오 생성 중 오류 발생: {str(e)}")
    
    def create_weekly_sale_video(
        self,
        image_dir: str,
        audio_file: Optional[str] = None,
        image_duration: int = 3,
        transition_duration: float = 0.5
    ) -> str:
        """
        주간 할인 정보를 담은 비디오를 생성합니다.
        
        Args:
            image_dir (str): 할인 정보 이미지가 있는 디렉토리 경로
            audio_file (str, optional): 배경음악 파일 경로
            image_duration (int): 각 이미지가 표시될 시간(초)
            transition_duration (float): 전환 효과 지속 시간(초)
            
        Returns:
            str: 생성된 비디오 파일의 경로
        """
        return self.create_video_from_images(
            image_dir=image_dir,
            output_filename="주간 롤 스킨 할인 정보.mp4",
            image_duration=image_duration,
            audio_file=audio_file,
            transition_duration=transition_duration
        ) 