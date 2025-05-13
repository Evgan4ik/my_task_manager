from aiogram.utils.keyboard import InlineKeyboardBuilder


class TaskKeyboards:
    """Фабрика инлайн-клавиатур для взаимодействия с задачами"""

    @staticmethod
    def tasks_list(tasks: list) -> InlineKeyboardBuilder:
        """
        Генерирует клавиатуру со списком задач
        :param tasks: Список объектов Task
        :return: Объект InlineKeyboardMarkup
        """
        builder = InlineKeyboardBuilder()
        for task in tasks:
            if task:
                status = "✅" if task.is_completed else "🕒"
                builder.button(
                    text=f"{status} {task.title}",
                 callback_data=f"view_{task.id}"
                )
        builder.button(text="❌ Отмена", callback_data="cancel")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def task_actions(task_id: int) -> InlineKeyboardBuilder:
        """
        Генерирует клавиатуру действий с конкретной задачей
        :param task_id: ID задачи в базе данных
        :return: Объект InlineKeyboardMarkup
        """
        builder = InlineKeyboardBuilder()
        builder.button(text="✏️ Редактировать", callback_data=f"edit_task_{task_id}")
        builder.button(text="🗑 Удалить", callback_data=f"delete_{task_id}")
        builder.button(text="🔙 Назад", callback_data="back")
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def edit_fields(task_id: int):
        """
        Клавиатура для выбора поля редактирования задачи
        :param task_id: ID редактируемой задачи
        :return: InlineKeyboardMarkup
        """
        builder = InlineKeyboardBuilder()

        # Кнопки выбора поля
        builder.button(text="📝 Название", callback_data=f"edit_title_{task_id}")
        builder.button(text="📄 Описание", callback_data=f"edit_desc_{task_id}")
        builder.button(text="📅 Дедлайн", callback_data=f"edit_deadline_{task_id}")
        builder.button(text="✅ Статус", callback_data=f"edit_status_{task_id}")
        builder.button(text="🔙 Назад", callback_data="back")

        # Распределение кнопок по рядам (первые 4 кнопки по 2 в ряду)
        builder.adjust(2, 2, 1)

        return builder.as_markup()