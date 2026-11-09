from django.shortcuts import get_object_or_404

# from django.urls import reverse
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course, Lesson, Subscription
from lms.paginators import CoursePaginator, LessonPaginator
from lms.serializers import CourseSerializer, LessonSerializer
from lms.services import (
    create_stripe_checkout_session,
    create_stripe_price,
    create_stripe_product,
)
from users.models import Payment
from users.permissions import IsModerator, IsNotModerator, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    """CRUD для курсов"""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_permissions(self):
        if self.action in ["create", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsNotModerator]
        elif self.action in ["update", "partial_update"]:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Модераторы").exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    """Список и создание уроков"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [IsAuthenticated, IsNotModerator]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Модераторы").exists():
            return Lesson.objects.all().order_by("id")
        return Lesson.objects.filter(owner=user).order_by("id")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Детали, обновление и удаление урока"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == "DELETE":
            self.permission_classes = [IsAuthenticated, IsNotModerator, IsOwner]
        elif self.request.method in ["PUT", "PATCH"]:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Модераторы").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class SubscriptionAPIView(APIView):
    """Управление подпиской на курс"""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            return Response({"error": "Не передан course_id"}, status=400)

        course_item = get_object_or_404(Course, id=course_id)
        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = "Подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "Подписка добавлена"

        return Response({"message": message})


class CreatePaymentView(APIView):
    """Создание платежа через Stripe"""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course_id = request.data.get("course_id")
        if not course_id:
            return Response({"error": "Не передан course_id"}, status=400)

        course = get_object_or_404(Course, id=course_id)
        price = getattr(course, "price", 1000)

        payment = Payment.objects.create(
            user=request.user, course=course, amount=price, payment_method="transfer"
        )

        product_id = create_stripe_product(course.title, course.description)
        if not product_id:
            return Response({"error": "Ошибка создания продукта"}, status=500)

        price_id = create_stripe_price(product_id, price)
        if not price_id:
            return Response({"error": "Ошибка создания цены"}, status=500)

        success_url = request.build_absolute_uri("/api/courses/")
        cancel_url = request.build_absolute_uri("/api/courses/")

        payment_url = create_stripe_checkout_session(price_id, success_url, cancel_url)
        if not payment_url:
            return Response({"error": "Ошибка создания сессии"}, status=500)

        payment.stripe_product_id = product_id
        payment.stripe_price_id = price_id
        payment.payment_url = payment_url
        payment.save()

        return Response(
            {
                "payment_url": payment_url,
                "payment_id": payment.id,
            }
        )
