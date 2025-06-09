from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from utils.events import get_event_titles, load_events
from config import config

def get_main_menu(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="💬 Начать")],
        [KeyboardButton(text="📋 Посмотреть мероприятия")],
        [KeyboardButton(text="📌 Мои мероприятия")],
    ]

    if user_id in config.admin_ids:
        keyboard.append([KeyboardButton(text="👨‍💼 Админ-панель")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_event_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=title, callback_data=f"event_{title}")]
        for title in get_event_titles()
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_event_list_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=event["title"], callback_data=f"view_{event['id']}")]
        for event in load_events()
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_register_event_keyboard(event_id: int, already_registered: bool) -> InlineKeyboardMarkup:
    if already_registered:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Вы уже зарегистрированы", callback_data="none")],
            [InlineKeyboardButton(text="❌ Отменить регистрацию", callback_data=f"cancel_{event_id}")],
            [InlineKeyboardButton(text="🔙 Вернуться назад", callback_data="back_to_events")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Зарегистрироваться", callback_data=f"register_{event_id}")],
            [InlineKeyboardButton(text="🔙 Вернуться назад", callback_data="back_to_events")]
        ])

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes")],
        [InlineKeyboardButton(text="❌ Нет", callback_data="confirm_no")]
    ])

def get_cancel_registration_keyboard(event_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить регистрацию", callback_data=f"cancel_{event_id}")],
        [InlineKeyboardButton(text="🔙 Вернуться назад", callback_data="back_to_events")]
    ])

def get_event_admin_keyboard(event_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("✏️ Изменить", callback_data=f"edit_{event_id}")],
        [InlineKeyboardButton("🗑 Удалить", callback_data=f"delete_{event_id}")],
        [InlineKeyboardButton("📥 Экспорт в Excel", callback_data=f"export_{event_id}")]
    ])
