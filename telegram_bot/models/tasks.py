"""
Асинхронные методы для работы с моделью Task из Django ORM
"""

from asgiref.sync import sync_to_async
from tasks.models import Task


class AsyncTaskManager:
    """Обеспечивает асинхронное взаимодействие с базой данных"""

    @staticmethod
    @sync_to_async
    def get_all():
        """
        Получение всех задач с сортировкой по дате создания
        """
        return list(Task.objects.all().order_by('-created_at'))

    @staticmethod
    @sync_to_async
    def get(**kwargs):
        """
        Получение задачи по параметрам
         """
        return Task.objects.get(**kwargs)

    @staticmethod
    @sync_to_async
    def save(task):
        """
        Сохранение задачи в базе данных
        """
        task.save()

    @staticmethod
    @sync_to_async
    def delete(task):
        """
        Удаление задачи из базы данных
        """
        task.delete()

    @staticmethod
    @sync_to_async
    def create(**kwargs):
        """
        Создание новой задачи
        """
        return Task.objects.create(**kwargs)
