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
        Returns: list[Task] - список объектов Task
        """
        return list(Task.objects.all().order_by('-created_at'))

    @staticmethod
    @sync_to_async
    def get(**kwargs):
        """
        Получение задачи по параметрам
        Args:
            **kwargs: Параметры фильтрации (например: id=1)
        Returns: Task - объект задачи
        """
        return Task.objects.get(**kwargs)

    @staticmethod
    @sync_to_async
    def save(task):
        """
        Сохранение задачи в базе данных
        Args:
            task (Task): Объект задачи для сохранения
        """
        task.save()

    @staticmethod
    @sync_to_async
    def delete(task):
        """
        Удаление задачи из базы данных
        Args:
            task (Task): Объект задачи для удаления
        """
        task.delete()

    @staticmethod
    @sync_to_async
    def create(**kwargs):
        """
        Создание новой задачи
        Args:
            **kwargs: Параметры задачи (title, description и т.д.)
        Returns: Task - созданный объект задачи
        """
        return Task.objects.create(**kwargs)