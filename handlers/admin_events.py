from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from config import config
from keyboards.admin import get_event_admin_keyboard
from utils.events import get_event_by_id
from database.db import get_users_by_event
from states.admin import NewEvent, EditEvent
from utils.events import save_events, load_events, get_next_event_id
from datetime import datetime
from utils.events import format_date
from utils.excel import generate_excel_for_event
from utils.excel import generate_excel_for_all_events

router = Router()

@router.message(Command("admin_events"))
async def list_admin_events(message: types.Message):
    await message.answer(f"DEBUG: config.admin_ids = {config.admin_ids}")
    await message.answer(f"DEBUG: message.from_user.id = {message.from_user.id}")

    if message.from_user.id not in config.admin_ids:
        await message.answer("⛔ У вас нет доступа.")
        return

    events = load_events()
    if not events:
        await message.answer("Мероприятия пока не добавлены.")
        return

    await message.answer("<b>📋 Все мероприятия:</b>", parse_mode="HTML")

    for event in events:
        text = (
            f"<b>{event['title']}</b>\n"
            f"{event['description']}\n\n"
            f"📍 Место проведения: {event.get('location', 'не указано')}\n\n"
            f"🕒 {format_date(event['start_date'])} {event['start_time']} – {format_date(event['end_date'])} {event['end_time']}"
        )
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_event_admin_keyboard(event["id"])
        )

@router.callback_query(F.data == "admin_list_events")
async def cb_list_events(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if user_id not in config.admin_ids:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    events = load_events()
    if not events:
        await callback.message.answer("Мероприятия пока не добавлены.")
        return

    await callback.message.answer("<b>📋 Все мероприятия:</b>", parse_mode="HTML")

    for event in events:
        text = (
            f"<b>{event['title']}</b>\n"
            f"{event['description']}\n\n"
            f"📍 Место проведения: {event.get('location', 'не указано')}\n\n"
            f"🗓️ {format_date(event['start_date'])} {event['start_time']} – {format_date(event['end_date'])} {event['end_time']}"
        )
        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_event_admin_keyboard(event["id"])
        )

@router.callback_query(F.data.startswith("admin_view_"))
async def admin_view_event(callback: types.CallbackQuery):
    event_id = int(callback.data.split("_")[2])
    event = get_event_by_id(event_id)
    if not event:
        await callback.message.answer("❌ Мероприятие не найдено.")
        return

    # Заголовок мероприятия
    text = (
        f"<b>📌 {event['title']}</b>\n\n"
        f"{event['description']}\n\n"
        f"📍 Место проведения: {event.get('location', 'не указано')}\n\n"
        f"🗓️ {format_date(event['start_date'])} {event['start_time']} – {format_date(event['end_date'])} {event['end_time']}"
    )

    # Список участников
    users = await get_users_by_event(event["title"])
    if not users:
        text += "🙁 Никто пока не зарегистрирован."
    else:
        text += f"<b>👥 Зарегистрировано: {len(users)}</b>\n\n"
        for i, u in enumerate(users, 1):
            text += (
                f"{i}. {u['name']} {u['surname']} | {u['email']} | {u['phone']}\n"
                f"   {u['telegram']}\n"
            )

    await callback.message.answer(text, parse_mode="HTML")

@router.message(Command("add_event"))
async def add_event_start(message: types.Message, state: FSMContext):
    if message.from_user.id not in config.admin_ids:
        await message.answer("⛔ У вас нет доступа.")
        return

    await message.answer("Введите название нового мероприятия:")
    await state.set_state(NewEvent.waiting_for_title)

@router.message(NewEvent.waiting_for_title)
async def get_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание мероприятия:")
    await state.set_state(NewEvent.waiting_for_description)

@router.message(NewEvent.waiting_for_description)
async def get_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите место проведения:")
    await state.set_state(NewEvent.waiting_for_location)

@router.message(NewEvent.waiting_for_location)
async def get_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer("Введите дату начала (ДД.ММ.ГГГГ):")
    await state.set_state(NewEvent.waiting_for_start_date)

@router.message(NewEvent.waiting_for_start_date)
async def get_start_date(message: types.Message, state: FSMContext):
    try:
        parsed_date = datetime.strptime(message.text, "%d.%m.%Y").strftime("%Y-%m-%d")
        await state.update_data(start_date=parsed_date)
        await message.answer("Введите время начала (ЧЧ:ММ):")
        await state.set_state(NewEvent.waiting_for_start_time)
    except ValueError:
        await message.answer("⚠️ Неверный формат. Введите дату в формате ДД.ММ.ГГГГ")

@router.message(NewEvent.waiting_for_start_time)
async def get_start_time(message: types.Message, state: FSMContext):
    try:
        parsed_time = datetime.strptime(message.text, "%H:%M").strftime("%H:%M")
        await state.update_data(start_time=parsed_time)
        await message.answer("Введите дату окончания (ДД.ММ.ГГГГ):")
        await state.set_state(NewEvent.waiting_for_end_date)
    except ValueError:
        await message.answer("⚠️ Неверный формат. Введите время в формате ЧЧ:ММ")

@router.message(NewEvent.waiting_for_end_date)
async def get_end_date(message: types.Message, state: FSMContext):
    try:
        parsed_date = datetime.strptime(message.text, "%d.%m.%Y").strftime("%Y-%m-%d")
        await state.update_data(end_date=parsed_date)
        await message.answer("Введите время окончания (ЧЧ:ММ):")
        await state.set_state(NewEvent.waiting_for_end_time)
    except ValueError:
        await message.answer("⚠️ Неверный формат. Введите дату в формате ДД.ММ.ГГГГ")

@router.message(NewEvent.waiting_for_end_time)
async def get_end_time(message: types.Message, state: FSMContext):
    try:
        parsed_time = datetime.strptime(message.text, "%H:%M").strftime("%H:%M")
        await state.update_data(end_time=parsed_time)

        data = await state.get_data()

        events = load_events()
        new_event = {
            "id": get_next_event_id(),
            "title": data["title"],
            "description": data["description"],
            "location": data["location"],
            "start_date": data["start_date"],
            "start_time": data["start_time"],
            "end_date": data["end_date"],
            "end_time": data["end_time"]
        }

        events.append(new_event)
        save_events(events)

        await message.answer(f"✅ Мероприятие \"{data['title']}\" успешно добавлено!")
        await state.clear()

    except ValueError:
        await message.answer("⚠️ Неверный формат. Введите время в формате ЧЧ:ММ")

@router.callback_query(F.data == "admin_add_event")
async def cb_add_event(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название нового мероприятия:")
    await state.set_state(NewEvent.waiting_for_title)

@router.callback_query(F.data == "admin_list_events")
async def cb_list_events(callback: types.CallbackQuery):
    await list_admin_events(callback.message)

@router.callback_query(F.data == "admin_export_all")
async def cb_export_all(callback: types.CallbackQuery):
    if callback.from_user.id not in config.admin_ids:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    filename = "all_events.xlsx"
    await generate_excel_for_all_events(filename)

    file = FSInputFile(filename)
    await callback.message.answer_document(file, caption="📥 Все мероприятия и участники")


@router.callback_query(F.data.startswith("admin_delete_"))
async def admin_delete_event(callback: types.CallbackQuery):
    event_id = int(callback.data.split("_")[2])
    events = load_events()

    updated = [e for e in events if e["id"] != event_id]

    if len(updated) == len(events):
        await callback.message.answer("❌ Мероприятие не найдено.")
        return

    save_events(updated)
    await callback.message.answer("🗑️ Мероприятие удалено.")

@router.callback_query(F.data.startswith("admin_edit_"))
async def admin_edit_event(callback: types.CallbackQuery, state: FSMContext):
    event_id = int(callback.data.split("_")[2])
    event = get_event_by_id(event_id)

    if not event:
        await callback.message.answer("❌ Мероприятие не найдено.")
        return

    await callback.message.answer(f"Редактируем: <b>{event['title']}</b>\n\nВведите новое название:", parse_mode="HTML")
    await state.update_data(event_id=event_id)
    await state.set_state(EditEvent.editing_title)

@router.message(EditEvent.editing_title)
async def edit_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите новое описание:")
    await state.set_state(EditEvent.editing_description)

@router.message(EditEvent.editing_description)
async def edit_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите новое место проведения:")
    await state.set_state(EditEvent.editing_location)

@router.message(EditEvent.editing_location)
async def edit_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer("Введите новую дату начала (ДД.ММ.ГГГГ):")
    await state.set_state(EditEvent.editing_start_date)

@router.message(EditEvent.editing_start_date)
async def edit_start_date(message: types.Message, state: FSMContext):
    try:
        parsed_date = datetime.strptime(message.text, "%d.%m.%Y").strftime("%Y-%m-%d")
        await state.update_data(start_date=parsed_date)
        await message.answer("Введите новое время начала (ЧЧ:ММ):")
        await state.set_state(EditEvent.editing_start_time)
    except ValueError:
        await message.answer("⚠️ Неверный формат. Введите дату в формате ДД.ММ.ГГГГ")

@router.message(EditEvent.editing_start_time)
async def edit_start_time(message: types.Message, state: FSMContext):
    try:
        parsed_time = datetime.strptime(message.text, "%H:%M").strftime("%H:%M")
        await state.update_data(start_time=parsed_time)
        await message.answer("Введите новую дату окончания (ДД.ММ.ГГГГ):")
        await state.set_state(EditEvent.editing_end_date)
    except ValueError:
        await message.answer("⚠️ Неверный формат. Введите время в формате ЧЧ:ММ")

@router.message(EditEvent.editing_end_date)
async def edit_end_date(message: types.Message, state: FSMContext):
    try:
        parsed_date = datetime.strptime(message.text, "%d.%m.%Y").strftime("%Y-%m-%d")
        await state.update_data(end_date=parsed_date)
        await message.answer("Введите новое время окончания (ЧЧ:ММ):")
        await state.set_state(EditEvent.editing_end_time)
    except ValueError:
        await message.answer("⚠️ Неверный формат. Введите дату в формате ДД.ММ.ГГГГ")

@router.message(EditEvent.editing_end_time)
async def edit_end_time(message: types.Message, state: FSMContext):
    try:
        parsed_time = datetime.strptime(message.text, "%H:%M").strftime("%H:%M")
        await state.update_data(end_time=parsed_time)

        data = await state.get_data()
        events = load_events()

        for e in events:
            if e["id"] == data["event_id"]:
                e["title"] = data["title"]
                e["description"] = data["description"]
                e["location"] = data["location"]
                e["start_date"] = data["start_date"]
                e["start_time"] = data["start_time"]
                e["end_date"] = data["end_date"]
                e["end_time"] = data["end_time"]
                break

        save_events(events)
        await message.answer("✅ Мероприятие успешно обновлено.")
        await state.clear()
    except ValueError:
        await message.answer("⚠️ Неверный формат. Введите время в формате ЧЧ:ММ")

@router.callback_query(F.data.startswith("export_"))
async def export_one_event(callback: types.CallbackQuery):
    event_id = int(callback.data.split("_")[1])
    events = load_events()
    event = next((e for e in events if e["id"] == event_id), None)
    if not event:
        await callback.message.answer("Мероприятие не найдено.")
        return

    filename = f"event_{event_id}.xlsx"
    generate_excel_for_event(event["title"], filename)

    with open(filename, "rb") as file:
        await callback.message.answer_document(file, caption=f"📥 Участники: {event['title']}")