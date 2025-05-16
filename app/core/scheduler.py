from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from app.services.content.scheduler import ContentScheduler

scheduler = AsyncIOScheduler()

def setup_scheduler():
    """Setup scheduler for weekly scraping every Monday at 00:00 KST"""
    kst = timezone('Asia/Seoul')
    
    scheduler.add_job(
        func=ContentScheduler()._login_to_slp,
        trigger=CronTrigger(
            hour=0,
            minute=10,
            timezone=kst
        ),
        id='slp_login',
        name='SLP login for mileage',
        replace_existing=True
    )
    
    # 매주 화요일 새벽 3시 10분 - 예외처리 리스트 생성
    scheduler.add_job(
        func=ContentScheduler().create_exception_list,
        trigger=CronTrigger(
            day_of_week='tue',
            hour=3,
            minute=30,
            timezone=kst
        ),
        id='create_exception_list',
        name='Create LoL previous discounts list',
        replace_existing=True
    )
    
    # 매주 화요일 새벽 4시 10분 - 주간 롤 스킨 갱신 (서머타임 해제 시, 5시로 변경 필요)
    scheduler.add_job(
        func=ContentScheduler().run_weekly_update,
        trigger=CronTrigger(
            day_of_week='tue',
            hour=4,
            minute=10,
            timezone=kst
        ),
        id='weekly_content_update',
        name='Weekly LoL Store Content Update',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start() 