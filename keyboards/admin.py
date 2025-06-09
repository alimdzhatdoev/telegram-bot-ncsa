from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_event_admin_keyboard(event_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👁️ Посмотреть", callback_data=f"admin_view_{event_id}"),
            InlineKeyboardButton(text="✏️ Изменить", callback_data=f"admin_edit_{event_id}"),
            InlineKeyboardButton(text="❌ Удалить", callback_data=f"admin_delete_{event_id}")
        ]
    ])

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить мероприятие", callback_data="admin_add_event")],
        [InlineKeyboardButton(text="📋 Список мероприятий", callback_data="admin_list_events")],
        [InlineKeyboardButton(text="📤 Выгрузить все регистрации", callback_data="admin_export_all")]
    ])
