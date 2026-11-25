from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

@shared_task
def block_inactive_users():
    month_ago = timezone.now() - timedelta(days=30)

    updated_count = User.objects.filter(
        last_login__lt=month_ago,
        is_active=True
    ).update(is_active=False)

    return f"Заблокировано: {updated_count}"