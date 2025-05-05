from django.core.management.base import BaseCommand
from telegram_bot.bot import Command as BotCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        BotCommand().handle()