from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson, Subscription

User = get_user_model()


class LessonTestCase(APITestCase):
    """Тесты CRUD уроков"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com", password="test12345"
        )
        self.moderator = User.objects.create_user(
            email="mod@test.com", password="test12345"
        )

        moder_group, _ = Group.objects.get_or_create(name="Модераторы")
        self.moderator.groups.add(moder_group)

        self.course = Course.objects.create(
            title="Курс", description="Описание", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            title="Урок",
            description="Описание",
            video_url="https://youtube.com/watch?v=123",
            course=self.course,
            owner=self.user,
        )

    def test_lesson_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/lessons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_list_unauthorized(self):
        response = self.client.get("/api/lessons/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lesson_create(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Новый урок",
            "description": "Описание",
            "video_url": "https://youtube.com/watch?v=456",
            "course": self.course.id,
        }
        response = self.client.post("/api/lessons/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lesson_create_invalid_url(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Новый урок",
            "description": "Описание",
            "video_url": "https://vk.com/video123",
            "course": self.course.id,
        }
        response = self.client.post("/api/lessons/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lesson_update_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f"/api/lessons/{self.lesson.id}/", {"title": "Изменено"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_update_not_owner(self):
        other = User.objects.create_user(email="other@test.com", password="test12345")
        self.client.force_authenticate(user=other)
        response = self.client.patch(
            f"/api/lessons/{self.lesson.id}/", {"title": "Взлом"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lesson_delete_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/lessons/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_lesson_delete_moderator(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(f"/api/lessons/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_update_moderator(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.patch(
            f"/api/lessons/{self.lesson.id}/", {"title": "Модерация"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SubscriptionTestCase(APITestCase):
    """Тесты подписки"""

    def setUp(self):
        self.user = User.objects.create_user(email="sub@test.com", password="test12345")
        self.course = Course.objects.create(
            title="Курс", description="Описание", owner=self.user
        )

    def test_subscribe(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/subscribe/", {"course_id": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_unsubscribe(self):
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/subscribe/", {"course_id": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscribe_unauthorized(self):
        response = self.client.post("/api/subscribe/", {"course_id": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
