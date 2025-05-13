from datetime import datetime

# Утилиты для конвертации даты
def parse_date(date_str: str) -> datetime:
    """Конвертация строки в datetime"""
    try:
        return datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        raise ValueError("Неверный формат даты")