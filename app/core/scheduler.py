from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from app.services.lol_store import LoLStoreService

scheduler = AsyncIOScheduler()

def setup_scheduler():
    """Setup scheduler for weekly scraping every Tuesday at 16:10 KST"""
    kst = timezone('Asia/Seoul')
    
    # Create scheduler job
    scheduler.add_job(
        func=LoLStoreService().update_discounts,
        trigger=CronTrigger(
            day_of_week='sun',  # Tuesday (tue)
            hour=16,
            minute=50,
            timezone=kst
        ),
        id='weekly_scraping',
        name='Weekly LoL Store Scraping',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start() 