from celery import Celery

celery_app = Celery(
    "gen_trade", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1"
)

# Optional configurations
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
