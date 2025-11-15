from aiogram.fsm.state import StatesGroup, State

class AddSubState(StatesGroup):
    nick = State()
    amount = State()
    term = State()
