import os
import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.core.management.base import BaseCommand
from asgiref.sync import sync_to_async
from tasks.models import Task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=os.getenv('TELEGRAM_TOKEN'))
dp = Dispatcher(storage=MemoryStorage())


class TaskActions(StatesGroup):
    choosing_task = State()
    choosing_field = State()
    editing_title = State()
    editing_description = State()
    editing_deadline = State()
    new_task_title = State()
    new_task_description = State()
    new_task_deadline = State()


# Асинхронные обертки
async_get_tasks = sync_to_async(lambda: list(Task.objects.all().order_by('-created_at')))
async_get_task = sync_to_async(Task.objects.get)
async_save_task = sync_to_async(lambda task: task.save())
async_delete_task = sync_to_async(lambda task: task.delete())


async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/start", description="Главное меню"),
        types.BotCommand(command="/tasks", description="Мои задачи"),
        types.BotCommand(command="/newtask", description="Новая задача"),
    ]
    await bot.set_my_commands(commands)


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "📋 Task Manager Bot\n\n"
        "Доступные команды:\n"
        "/tasks - Просмотр и редактирование задач\n"
        "/newtask - Создать новую задачу"
    )


@dp.message(Command("tasks"))
async def list_tasks(message: types.Message, state: FSMContext):
    tasks = await async_get_tasks()

    if not tasks:
        await message.answer("📭 У вас пока нет задач")
        return

    builder = InlineKeyboardBuilder()
    for task in tasks:
        status = "✅" if task.is_completed else "🕒"
        builder.button(
            text=f"{status} {task.title}",
            callback_data=f"view_{task.id}"
        )

    builder.button(text="❌ Отмена", callback_data="cancel")
    builder.adjust(1)

    await message.answer(
        "📋 Выберите задачу:",
        reply_markup=builder.as_markup()
    )
    await state.set_state(TaskActions.choosing_task)


@dp.callback_query(TaskActions.choosing_task, lambda c: c.data.startswith("view_"))
async def view_task(callback: types.CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split("_")[1])
    task = await async_get_task(id=task_id)

    text = (
        f"📌 Задача #{task.id}\n\n"
        f"🔖 Название: {task.title}\n"
        f"📄 Описание: {task.description or 'отсутствует'}\n"
        f"📅 Создана: {task.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"⏳ Дедлайн: {task.deadline.strftime('%d.%m.%Y') if task.deadline else 'не установлен'}\n"
        f"✅ Статус: {'выполнена' if task.is_completed else 'в работе'}"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Редактировать", callback_data=f"edit_task_{task.id}")
    builder.button(text="🗑 Удалить", callback_data=f"delete_{task.id}")
    builder.button(text="🔙 Назад", callback_data="back")
    builder.adjust(1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await state.update_data(current_task_id=task_id)


@dp.callback_query(lambda c: c.data.startswith("edit_task_"))
async def edit_task_handler(callback: types.CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split("_")[2])
    await state.update_data(current_task_id=task_id)

    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Название", callback_data=f"edit_title_{task_id}")
    builder.button(text="📄 Описание", callback_data=f"edit_desc_{task_id}")
    builder.button(text="📅 Дедлайн", callback_data=f"edit_deadline_{task_id}")
    builder.button(text="✅ Статус", callback_data=f"edit_status_{task_id}")
    builder.button(text="🔙 Назад", callback_data="back")
    builder.adjust(2)

    await callback.message.edit_text(
        "✏️ Выберите что хотите изменить:",
        reply_markup=builder.as_markup()
    )
    await state.set_state(TaskActions.choosing_field)


@dp.callback_query(TaskActions.choosing_field, lambda c: any(
    c.data.startswith(prefix) for prefix in [
        "edit_title_",
        "edit_desc_",
        "edit_deadline_",
        "edit_status_"
    ]
))
async def process_field_choice(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    action_type = parts[1]
    task_id = int(parts[2])

    if action_type == "title":
        await callback.message.answer("📝 Введите новое название:")
        await state.set_state(TaskActions.editing_title)

    elif action_type == "desc":
        await callback.message.answer("📄 Введите новое описание:")
        await state.set_state(TaskActions.editing_description)

    elif action_type == "deadline":
        await callback.message.answer("📅 Введите новый дедлайн (дд.мм.гггг):")
        await state.set_state(TaskActions.editing_deadline)

    elif action_type == "status":
        task = await async_get_task(id=task_id)
        task.is_completed = not task.is_completed
        await async_save_task(task)
        await callback.message.answer(f"✅ Статус изменен на {'выполнена' if task.is_completed else 'в работе'}")
        await list_tasks(callback.message, state)

    await state.update_data(current_task_id=task_id)
    await callback.answer()


@dp.message(TaskActions.editing_title)
async def process_title_edit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    task = await async_get_task(id=data['current_task_id'])
    task.title = message.text
    await async_save_task(task)
    await message.answer("📝 Название успешно обновлено!")
    await state.clear()
    await list_tasks(message, state)


@dp.message(TaskActions.editing_description)
async def process_description_edit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    task = await async_get_task(id=data['current_task_id'])
    task.description = message.text
    await async_save_task(task)
    await message.answer("📄 Описание успешно обновлено!")
    await state.clear()
    await list_tasks(message, state)


@dp.message(TaskActions.editing_deadline)
async def process_deadline_edit(message: types.Message, state: FSMContext):
    try:
        deadline = datetime.strptime(message.text, "%d.%m.%Y")
        data = await state.get_data()
        task = await async_get_task(id=data['current_task_id'])
        task.deadline = deadline
        await async_save_task(task)
        await message.answer("📅 Дедлайн успешно обновлен!")
    except ValueError:
        await message.answer("❌ Неверный формат даты! Используйте ДД.ММ.ГГГГ")
    finally:
        await state.clear()
        await list_tasks(message, state)


@dp.callback_query(lambda c: c.data.startswith("delete_"))
async def delete_task(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    task = await async_get_task(id=task_id)
    await async_delete_task(task)
    await callback.message.answer("🗑 Задача успешно удалена!")
    await list_tasks(callback.message, state=None)


@dp.callback_query(lambda c: c.data == "back")
async def back_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await list_tasks(callback.message, state)


@dp.callback_query(lambda c: c.data == "cancel")
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Действие отменено")


@dp.message(Command("newtask"))
async def create_new_task(message: types.Message, state: FSMContext):
    await message.answer("📝 Введите название новой задачи:")
    await state.set_state(TaskActions.new_task_title)


@dp.message(TaskActions.new_task_title)
async def process_new_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("📄 Введите описание задачи (или отправьте '-' чтобы пропустить):")
    await state.set_state(TaskActions.new_task_description)


@dp.message(TaskActions.new_task_description)
async def process_new_description(message: types.Message, state: FSMContext):
    description = message.text if message.text != "-" else None
    await state.update_data(description=description)
    await message.answer("📅 Введите дедлайн в формате ДД.ММ.ГГГГ (или отправьте '-' чтобы пропустить):")
    await state.set_state(TaskActions.new_task_deadline)


@dp.message(TaskActions.new_task_deadline)
async def process_new_deadline(message: types.Message, state: FSMContext):
    data = await state.get_data()
    deadline = None

    try:
        if message.text != "-":
            deadline = datetime.strptime(message.text, "%d.%m.%Y")
    except ValueError:
        await message.answer("❌ Неверный формат даты! Используйте ДД.ММ.ГГГГ")
        return

    new_task = Task(
        title=data['title'],
        description=data['description'],
        deadline=deadline,
        created_at=datetime.now(),
        is_completed=False
    )

    await sync_to_async(new_task.save)()
    await message.answer("✅ Новая задача успешно создана!")
    await state.clear()


class Command(BaseCommand):
    help = 'Запуск Telegram бота'

    def handle(self, *args, **options):
        asyncio.run(self._start_bot())

    async def _start_bot(self):
        await set_commands(bot)
        await dp.start_polling(bot)