from django.core.management.base import BaseCommand
from asgiref.sync import async_to_sync
from telegram_bot.bot import main

class Command(BaseCommand):
    help = 'Запуск Telegram бота'

    def handle(self, *args, **options):
        """Точка входа для Django management command"""
        async_to_sync(main)()