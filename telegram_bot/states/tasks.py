from aiogram.fsm.state import State, StatesGroup

class TaskActions(StatesGroup):
    """
    Конечные автоматы (FSM) для управления состоянием диалога.
    Каждое состояние соответствует этапу взаимодействия с задачей.
    """
    choosing_task = State()          # Выбор задачи из списка
    choosing_field = State()         # Выбор поля для редактирования
    editing_title = State()          # Редактирование названия
    editing_description = State()    # Редактирование описания
    editing_deadline = State()       # Редактирование дедлайна
    new_task_title = State()         # Ввод названия новой задачи
    new_task_description = State()   # Ввод описания новой задачи
    new_task_deadline = State()      # Ввод дедлайна новой задачи