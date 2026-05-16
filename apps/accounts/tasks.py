from celery import shared_task


@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, user_id: str) -> None:
    from django.contrib.auth import get_user_model
    from django.core.mail import send_mail
    from django.conf import settings

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    try:
        send_mail(
            subject="Welcome to Pinboard!",
            message=f"Hi {user.display_name}, welcome to Pinboard.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
