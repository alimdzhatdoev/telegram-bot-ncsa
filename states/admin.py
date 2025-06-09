from aiogram.fsm.state import StatesGroup, State

class NewEvent(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_location = State()
    waiting_for_start_date = State()
    waiting_for_start_time = State()
    waiting_for_end_date = State()
    waiting_for_end_time = State()

class EditEvent(StatesGroup):
    selecting_event = State()
    editing_title = State()
    editing_description = State()
    editing_location = State()
    editing_start_date = State()
    editing_start_time = State()
    editing_end_date = State()
    editing_end_time = State()
