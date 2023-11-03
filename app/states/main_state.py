from aiogram.fsm.state import StatesGroup, State

class MainState(StatesGroup):
    get_domain = State()
    get_command = State()


class AcceptCommandState(StatesGroup):
    


class TempState(StatesGroup):
    temp = State()
