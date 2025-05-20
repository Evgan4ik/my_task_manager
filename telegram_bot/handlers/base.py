from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import logging
from ..lexicon import LEXICON

# Настройка логирования
logger = logging.getLogger(__name__)


router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    """
    Обработчик команды /start
    """
    try:
        logger.info(f"Пользователь {message.from_user.id} нажал /start")
        await message.answer(LEXICON['start'])
    except Exception as e:
        logger.error(f"Ошибка в /start: {e}")
        await message.answer("⚠️ Ошибка")

async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик отмены действий
    """
    await state.clear()
    await callback.message.edit_text(LEXICON['cancel'])

@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Отмена' в любом состоянии"""
    try:
        logger.info(f"Пользователь {callback.from_user.id} отменил действие")
        await state.clear()  # Очищаем состояние
        await callback.message.edit_text(LEXICON['cancel'])  # Редактируем сообщение
        await callback.answer()  # Подтверждаем обработку callback
    except Exception as e:
        logger.error(f"Ошибка отмены: {e}")
        await callback.answer("⚠️ Ошибка")
