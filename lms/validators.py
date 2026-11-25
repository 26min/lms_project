from urllib.parse import urlparse

from django.core.exceptions import ValidationError


def validate_youtube_url(value):
    """Проверяет, что ссылка ведёт только на youtube.com"""
    if not value:
        return value

    parsed = urlparse(value)
    domain = parsed.netloc.lower()

    allowed_domains = ["youtube.com", "www.youtube.com", "youtu.be"]

    if not any(domain == d or domain.endswith("." + d) for d in allowed_domains):
        raise ValidationError(
            "Ссылка должна вести только на youtube.com. "
            "Ссылки на другие ресурсы запрещены."
        )

    return value
