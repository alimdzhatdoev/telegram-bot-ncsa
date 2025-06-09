from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from keyboards.common import get_main_menu, get_event_list_keyboard, get_register_event_keyboard, \
    get_cancel_registration_keyboard
from utils.events import load_events, format_date
from config import config
from states.registration import Registration
from database.db import get_user_registrations
from database.db import cancel_registration
from keyboards.admin import get_admin_main_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Добро пожаловать! Выберите действие:",
        reply_markup=get_main_menu(message.from_user.id)
    )

@router.message(F.text == "📋 Посмотреть мероприятия")
async def show_event_menu(message: types.Message):
    await message.answer("Выберите мероприятие:", reply_markup=get_event_list_keyboard())

@router.callback_query(F.data.startswith("view_"))
async def view_event_detail(callback: types.CallbackQuery, state: FSMContext):
    event_id = int(callback.data.split("_")[1])
    events = load_events()
    event = next((e for e in events if e["id"] == event_id), None)
    if not event:
        await callback.message.answer("Мероприятие не найдено.")
        return

    # Проверка регистрации пользователя на это мероприятие
    registrations = await get_user_registrations(callback.from_user.id)
    already_registered = any(r["event_id"] == event["id"] for r in registrations)

    text = (
        f"<b>{event['title']}</b>\n\n"
        f"{event['description']}\n\n"
        f"📍 Место проведения: {event['location']}\n"
        f"📅 {format_date(event['start_date'])} {event['start_time']} – "
        f"{format_date(event['end_date'])} {event['end_time']}"
    )
    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_register_event_keyboard(event_id, already_registered)
    )

@router.message(F.text == "📝 Зарегистрироваться")
async def start_registration_button(message: types.Message, state: FSMContext):
    await message.answer("Введите ваше имя:")
    await state.set_state(Registration.waiting_for_name)

@router.message(F.text == "👨‍💼 Админ-панель")
async def admin_panel_button(message: types.Message):
    if message.from_user.id not in config.admin_ids:
        await message.answer("У вас нет доступа к админ-панели.")
        return

    await message.answer(
        "<b>🔐 Админ-панель:</b>\nВыберите действие:",
        parse_mode="HTML",
        reply_markup=get_admin_main_keyboard()
    )

@router.callback_query(F.data == "back_to_events")
async def back_to_event_list(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Выберите мероприятие:", reply_markup=get_event_list_keyboard())

@router.message(F.text == "📌 Мои мероприятия")
async def show_user_registrations(message: types.Message):
    registrations = await get_user_registrations(message.from_user.id)

    if not registrations:
        await message.answer("Вы пока не зарегистрированы ни на одно мероприятие.")
        return

    for reg in registrations:
        text = (
            f"<b>{reg['event']}</b>\n"
            f"📧 {reg['email']} | 📞 {reg['phone']}"
        )
        event_id = reg.get("event_id")
        if event_id:
            await message.answer(
                text,
                parse_mode="HTML",
                reply_markup=get_cancel_registration_keyboard(event_id)
            )
        else:
            await message.answer(text, parse_mode="HTML")


@router.callback_query(F.data == "none")
async def ignore_button(callback: types.CallbackQuery):
    await callback.answer("Вы уже зарегистрированы", show_alert=True)

@router.callback_query(F.data.startswith("cancel_"))
async def cancel_user_registration(callback: types.CallbackQuery):
    event_id = int(callback.data.split("_")[1])
    events = load_events()
    event = next((e for e in events if e["id"] == event_id), None)
    if not event:
        await callback.message.answer("Мероприятие не найдено.")
        return

    await cancel_registration(callback.from_user.id, event_id)
    await callback.message.answer(f"❌ Вы отменили регистрацию на мероприятие \"{event['title']}\"")

@router.message(F.text == "💬 Начать")
async def manual_start_button(message: types.Message, state: FSMContext):
    await cmd_start(message)