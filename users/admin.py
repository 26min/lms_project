from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Payment, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "phone", "city", "is_staff")
    search_fields = ("email",)
    ordering = ("email",)


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
