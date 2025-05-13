from django.db import models
from django.db.models import Q
from django.utils import timezone

class Task(models.Model):
    """Модель для хранения задач"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        """Проверка просрочки задачи"""
        if self.deadline:
            return timezone.now() > self.deadline
        return False

    @classmethod
    def search(cls, query):
        """Поиск по заголовку и описанию"""
        return cls.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )