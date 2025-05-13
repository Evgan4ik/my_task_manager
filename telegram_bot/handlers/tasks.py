"""
Обработчики команд для работы с задачами
"""

import logging
from datetime import datetime
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from ..keyboards.builders import TaskKeyboards
from ..states.tasks import TaskActions
from ..models.tasks import AsyncTaskManager
from ..lexicon import LEXICON
from ..utils.converters import parse_date

router = Router()

# Настройка логирования
logger = logging.getLogger(__name__)

# Основные команды
@router.message(Command("tasks"))
async def list_tasks(message: types.Message, state: FSMContext):
    """
    Обработчик команды /tasks
    Показывает список всех задач пользователя
    """
    try:
        logger.info(f"Пользователь {message.from_user.id} запросил задачи")
        tasks = await AsyncTaskManager.get_all()

        if state is not None:
            await state.set_state(TaskActions.choosing_task)
        else:
            logger.warning("State not provided for list_tasks")

        await message.answer(
            LEXICON['choose_task'],
            reply_markup=TaskKeyboards.tasks_list(tasks)
        )

    except Exception as e:
        logger.error(f"Ошибка списка задач: {e}")
        await message.answer("❌ Произошла ошибка при загрузке задач")

@router.message(Command("newtask"))
async def create_new_task(message: types.Message, state: FSMContext):
    """
    Обработчик команды /newtask
    Начинает процесс создания новой задачи
    """
    try:
        logger.info(f"Пользователь {message.from_user.id} создает задачу")
        await message.answer(LEXICON['input_new_task_title'])
        await state.set_state(TaskActions.new_task_title)
    except Exception as e:
        logger.error(f"Ошибка создания задачи: {e}")
        await message.answer("❌ Произошла ошибка при создании задачи")


# Callback обработчики
@router.callback_query(TaskActions.choosing_task, lambda c: c.data.startswith("view_"))
async def view_task(callback: types.CallbackQuery, state: FSMContext):
    """
    Просмотр деталей конкретной задачи
    """
    try:
        logger.info(f"Пользователь выбрал задачу {callback.data.split("_")[1]}")
        task_id = int(callback.data.split("_")[1])
        task = await AsyncTaskManager.get(id=task_id)

        text = LEXICON['task_details'].format(
            id=task.id,
            title=task.title,
            description=task.description or LEXICON['not_set'],
            created_at=task.created_at.strftime('%d.%m.%Y %H:%M'),
            deadline=task.deadline.strftime('%d.%m.%Y') if task.deadline else LEXICON['not_set'],
            status=LEXICON['status_completed'] if task.is_completed else LEXICON['status_in_progress']
        )
        markup = TaskKeyboards.task_actions(task.id)
        await callback.message.edit_text(text, reply_markup=markup)
        await state.set_state(TaskActions.choosing_field)

    except Exception as e:
        logger.error(f"Ошибка просмотра задачи {e}")
        await callback.message.answer("❌ Ошибка при загрузке задачи")

@router.callback_query(lambda c: c.data.startswith("edit_task_"))
async def edit_task_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик выбора редактирования задачи
    """
    try:
        logger.info(f"Пользователь редактирует выбранную задачу")
        task_id = int(callback.data.split("_")[2])
        await state.update_data(current_task_id=task_id)

        await callback.message.edit_text(
            LEXICON['edit_choose_field'],
            reply_markup=TaskKeyboards.edit_fields(task_id))

        await state.set_state(TaskActions.choosing_field)

    except Exception as e:
        logger.error(f"Ошибка просмотра задачи {e}")
        await callback.message.answer("❌ Ошибка при загрузке задачи")

# Редактирование задачи
@router.message(TaskActions.editing_title)
async def process_title_edit(message: types.Message, state: FSMContext):
    """
    Обновление названия задачи
    """
    try:
        logger.info(f"Пользователь редактирует название выбранной задачи")
        data = await state.get_data()
        task = await AsyncTaskManager.get(id=data['current_task_id'])
        task.title = message.text
        await AsyncTaskManager.save(task)

        await message.answer(LEXICON['edit_title_success'])
        await state.clear()
        await list_tasks(message, state)

    except Exception as e:
        logger.error(f"Ошибка редактирования названия задачи {e}")


@router.message(TaskActions.editing_description)
async def process_description_edit(message: types.Message, state: FSMContext):
    """
    Обновление описания задачи
    """
    try:
        logger.info(f"Пользователь редактирует описание выбранной задачи")
        data = await state.get_data()
        task = await AsyncTaskManager.get(id=data['current_task_id'])
        task.description = message.text
        await AsyncTaskManager.save(task)

        await message.answer(LEXICON['edit_description_success'])
        await state.clear()
        await list_tasks(message, state)

    except Exception as e:
        logger.error(f"Ошибка редактирования названия задачи {e}")

@router.message(TaskActions.editing_deadline)
async def process_deadline_edit(message: types.Message, state: FSMContext):
    """
    Обновление дедлайна задачи
    """
    try:
        logger.info(f"Пользователь редактирует дедлайн выбранной задачи")
        deadline = parse_date(message.text)
        data = await state.get_data()
        task = await AsyncTaskManager.get(id=data['current_task_id'])
        task.deadline = deadline
        await AsyncTaskManager.save(task)

        await message.answer(LEXICON['edit_deadline_success'])
    except ValueError:
        await message.answer(LEXICON['date_format_error'])
    finally:
        await state.clear()
        await list_tasks(message, state)


# Создание новой задачи
@router.message(TaskActions.new_task_title)
async def process_new_title(message: types.Message, state: FSMContext):
    """
    Обработка ввода названия новой задачи
    """
    try:
        logger.info(f"Пользователь создает новую задачу, вводит название")
        await state.update_data(title=message.text)
        await message.answer(LEXICON['input_new_task_description'])
        await state.set_state(TaskActions.new_task_description)

    except Exception as e:
        logger.error(f"Ошибка создания задачи {e}")

@router.message(TaskActions.new_task_description)
async def process_new_description(message: types.Message, state: FSMContext):
    """
    Обработка ввода описания новой задачи
    """
    try:
        logger.info(f"Пользователь вводит описание новой задачи")
        description = message.text if message.text != "-" else ""
        await state.update_data(description=description)
        await message.answer(LEXICON['input_new_task_deadline'])
        await state.set_state(TaskActions.new_task_deadline)
    except Exception as e:
        logger.error(f"Ошибка создания задачи {e}")

@router.message(TaskActions.new_task_deadline)
async def process_new_deadline(message: types.Message, state: FSMContext):
    """
    Обработка ввода дедлайна новой задачи
    """
    data = await state.get_data()
    deadline = None

    try:
        if message.text != "-":
            logger.info(f"Пользователь вводит дедлайн новой задачи")
            deadline = parse_date(message.text)
    except ValueError:
        await message.answer(LEXICON['date_format_error'])
        return

    await AsyncTaskManager.create(
        title=data['title'],
        description=data['description'],
        deadline=deadline,
        is_completed=False
    )

    await message.answer(LEXICON['new_task_success'])
    await state.clear()


# Обработчики для кнопок редактирования
@router.callback_query(F.data.startswith("edit_title_"))
async def process_edit_title_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Название'"""
    try:
        logger.info(f"Пользователь редактирует название выбранной задачи")
        task_id = int(callback.data.split("_")[2])
        await state.update_data(current_task_id=task_id)
        await callback.message.answer(LEXICON['input_title'])
        await state.set_state(TaskActions.editing_title)
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка ошибка редактирования названия задачи {e}")

@router.callback_query(F.data.startswith("edit_desc_"))
async def process_edit_desc_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Описание'"""
    try:
        logger.info(f"Пользователь редактирует описание выбранной задачи")
        task_id = int(callback.data.split("_")[2])
        await state.update_data(current_task_id=task_id)
        await callback.message.answer(LEXICON['input_description'])
        await state.set_state(TaskActions.editing_description)
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка ошибка редактирования описания задачи {e}")

@router.callback_query(F.data.startswith("edit_deadline_"))
async def process_edit_deadline_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Дедлайн'"""
    try:
        logger.info(f"Пользователь редактирует дедлайн выбранной задачи")
        task_id = int(callback.data.split("_")[2])
        await state.update_data(current_task_id=task_id)
        await callback.message.answer(LEXICON['input_deadline'])
        await state.set_state(TaskActions.editing_deadline)
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка ошибка редактирования дедлайна задачи {e}")

@router.callback_query(F.data.startswith("edit_status_"))
async def process_edit_status_callback(callback: types.CallbackQuery):
    """Обработчик кнопки 'Статус'"""
    try:
        logger.info(f"Пользователь редактирует статус выбранной задачи")
        task_id = int(callback.data.split("_")[2])
        task = await AsyncTaskManager.get(id=task_id)
        task.is_completed = not task.is_completed
        await AsyncTaskManager.save(task)

        status = LEXICON['status_completed'] if task.is_completed else LEXICON['status_in_progress']
        await callback.message.answer(LEXICON['edit_status_success'].format(status=status))
        await list_tasks(callback.message, state=None)
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка ошибка редактирования статуса задачи {e}")

@router.callback_query(F.data == "back")
async def back_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Назад'"""
    try:
        logger.info(f"Пользователь нажал кнопку Назад")
        await state.clear()
        await list_tasks(callback.message, state)
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при нажатии кнопки назад {e}")

@router.callback_query(F.data.startswith("delete_"))
async def delete_task_handler(callback: types.CallbackQuery):
    """Обработчик удаления задачи"""
    try:
        # Извлекаем ID задачи из callback_data
        task_id = int(callback.data.split("_")[1])
        logger.info(f"Удаление задачи ID: {task_id}")

        # Получаем и удаляем задачу
        task = await AsyncTaskManager.get(id=task_id)
        await AsyncTaskManager.delete(task)

        # Отправляем подтверждение и обновляем список
        await callback.message.delete()  # Удаляем сообщение с кнопками
        await callback.message.answer(LEXICON['delete_success'])
        await list_tasks(callback.message, state=None)

        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка удаления: {e}")
        await callback.answer("⚠️ Не удалось удалить задачу")
    finally:
        await callback.answer()