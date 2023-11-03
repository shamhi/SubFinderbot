from aiogram.fsm.state import StatesGroup, State

class MainState(StatesGroup):
    get_domain = State()
    get_command = State()


class AcceptCommandState(StatesGroup):
    wait_accept = State()


class TempState(StatesGroup):
    temp = State()
