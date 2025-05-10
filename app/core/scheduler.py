from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from app.services.lol_store import LoLStoreService

scheduler = AsyncIOScheduler()
lol_store_service = LoLStoreService()

async def scheduled_scraping():
    """Scheduled task to scrape the LoL store"""
    await lol_store_service.update_discounts()

def setup_scheduler():
    """Set up the scheduler with all scheduled tasks"""
    # Set up the scheduler to run every Tuesday at 4 AM KST
    scheduler.add_job(
        scheduled_scraping,
        trigger=CronTrigger(
            day_of_week='tue',
            hour=4,
            minute=0,
            timezone=pytz.timezone('Asia/Seoul')
        )
    )
    scheduler.start() 