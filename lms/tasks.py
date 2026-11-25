from celery import shared_task
from django.core.mail import send_mass_mail

@shared_task
def send_course_update_emails(course_title, subscriber_emails):
    """Отправляет письма подписчикам курса (батчем)."""
    if not subscriber_emails:
        return "Нет подписчиков"

    messages = []
    for email in subscriber_emails:
        messages.append((
            f'Курс "{course_title}" обновлён!',
            'Материалы курса обновлены. Зайдите посмотреть.',
            'noreply@yoursite.com',
            [email],
        ))

    send_mass_mail(messages, fail_silently=False)
    return f"Отправлено {len(messages)} писем"