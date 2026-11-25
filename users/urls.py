from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import PaymentViewSet, UserRegisterView, UserViewSet

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", UserRegisterView.as_view(), name="register"),
]
