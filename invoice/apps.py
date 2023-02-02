from django.apps import AppConfig


class InvoiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'invoice'

    def ready(self):
        # Send invoice back online
        from core.scheduler import start_send_invoice_offline_job
        start_send_invoice_offline_job()