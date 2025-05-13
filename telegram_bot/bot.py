from aiogram import Bot, Dispatcher
from telegram_bot.config.settings import TELEGRAM_TOKEN
from aiogram.fsm.storage.memory import MemoryStorage
import logging
from logging.handlers import RotatingFileHandler


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),         # Логи в консоль
        # Реализация ротации лог-файлов(будут создаваться 3 резервные копии файлов и перезаписываться когда размер достигнет 1мб)
        RotatingFileHandler(
            filename="bot.log",          # Логи в файл
            maxBytes=1024 * 1024,        # Размер файла - 1 MB
            backupCount=3,               # Количество файлов - 3
            encoding="utf-8"             # Кодировка
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info(">>> Бот запущен")

# Инициализация бота
dp = Dispatcher(storage=MemoryStorage())
bot = Bot(token=TELEGRAM_TOKEN)

# Регистрация роутеров
from .handlers import base, tasks


def setup_routers():
    dp.include_router(base.router)
    dp.include_router(tasks.router)


async def main():
    setup_routers()
    await dp.start_polling(bot)
