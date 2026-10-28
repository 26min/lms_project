from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Payment, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Настройка админки для кастомной модели пользователя"""

    list_display = ("email", "phone", "city", "is_staff")
    search_fields = ("email", "phone")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Личная информация", {"fields": ("phone", "city", "avatar")}),
        (
            "Права",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "payment_date",
        "course",
        "lesson",
        "amount",
        "payment_method",
    )
    list_filter = ("payment_method", "course", "lesson")
    search_fields = ("user__email",)
