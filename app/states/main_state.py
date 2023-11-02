from aiogram.fsm.state import StatesGroup, State

class MainState(StatesGroup):
    get_domain = State()
    get_command = State()


class TempState(StatesGroup):
    temp = State()
