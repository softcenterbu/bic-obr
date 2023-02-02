from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from invoice.views import send_invoice_offline

def start_send_invoice_offline_job():
    scheduler = BackgroundScheduler()

    scheduler.add_job(send_invoice_offline, 'interval', seconds=2)
    
    scheduler.start()
    

