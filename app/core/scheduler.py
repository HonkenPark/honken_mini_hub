from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from app.services.content.scheduler import ContentScheduler

scheduler = AsyncIOScheduler()

def setup_scheduler():
    """Setup weekly LoL store jobs on fixed Pacific Time (US DST auto-handled)."""
    # LoL sale refresh follows US Pacific. Fixed PT times auto-convert to KST
    # (PDT → Tue 03:10/04:10 KST, PST → Tue 04:10/05:10 KST).
    pt = timezone('America/Los_Angeles')
    
    # scheduler.add_job(
    #     func=ContentScheduler()._login_to_slp,
    #     trigger=CronTrigger(
    #         hour=0,
    #         minute=10,
    #         timezone=timezone('Asia/Seoul')
    #     ),
    #     id='slp_login',
    #     name='SLP login for mileage',
    #     replace_existing=True
    # )
    
    # 매주 월요일 11:10 PT - 예외처리 리스트 생성 (KST 화 03:10 PDT / 04:10 PST)
    scheduler.add_job(
        func=ContentScheduler().create_exception_list,
        trigger=CronTrigger(
            day_of_week='mon',
            hour=11,
            minute=10,
            timezone=pt
        ),
        id='create_exception_list',
        name='Create LoL previous discounts list',
        replace_existing=True
    )
    
    # 매주 월요일 12:10 PT - 주간 롤 스킨 갱신 (KST 화 04:10 PDT / 05:10 PST)
    scheduler.add_job(
        func=ContentScheduler().run_weekly_update,
        trigger=CronTrigger(
            day_of_week='mon',
            hour=12,
            minute=10,
            timezone=pt
        ),
        id='weekly_content_update',
        name='Weekly LoL Store Content Update',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
