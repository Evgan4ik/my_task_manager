from django.db import models
from django.utils import timezone

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)  # Новое поле
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.deadline:
            return timezone.now() > self.deadline
        return False

    @classmethod
    def search(cls, query):
        return cls.objects.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query)
        )