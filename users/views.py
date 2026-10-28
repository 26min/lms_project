from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, viewsets

from users.models import Payment
from users.serializers import PaymentSerializer, UserRegisterSerializer, UserSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """CRUD для пользователей (только для админа)"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class UserRegisterView(generics.CreateAPIView):
    """Регистрация — доступна всем"""

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]
