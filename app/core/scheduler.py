from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from app.services.content.scheduler import ContentScheduler

scheduler = AsyncIOScheduler()

def setup_scheduler():
    """Setup scheduler for weekly scraping every Monday at 00:00 KST"""
    kst = timezone('Asia/Seoul')
    
    # Create scheduler job
    scheduler.add_job(
        func=ContentScheduler().run_weekly_update,
        trigger=CronTrigger(
            day_of_week='tue',
            hour=4,
            minute=5,
            timezone=kst
        ),
        id='weekly_content_update',
        name='Weekly LoL Store Content Update',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start() 