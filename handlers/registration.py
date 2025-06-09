from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from states.registration import Registration
from database.db import save_registration
from keyboards.common import get_confirm_keyboard
from utils.events import load_events

router = Router()

@router.callback_query(F.data.startswith("register_"))
async def start_registration(callback: types.CallbackQuery, state: FSMContext):
    event_id = int(callback.data.split("_")[1])
    events = load_events()
    event = next((e for e in events if e["id"] == event_id), None)
    if not event:
        await callback.message.answer("Мероприятие не найдено.")
        return

    await state.update_data(event=event["title"], event_id=event["id"])
    await callback.message.answer("Введите ваше имя:")
    await state.set_state(Registration.waiting_for_name)

@router.message(Registration.waiting_for_name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите вашу фамилию:")
    await state.set_state(Registration.waiting_for_surname)

@router.message(Registration.waiting_for_surname)
async def get_surname(message: types.Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await message.answer("Введите ваш email:")
    await state.set_state(Registration.waiting_for_email)

@router.message(Registration.waiting_for_email)
async def get_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Введите ваш номер телефона:")
    await state.set_state(Registration.waiting_for_phone)

@router.message(Registration.waiting_for_phone)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)

    data = await state.get_data()
    telegram_link = f"https://t.me/{message.from_user.username}" if message.from_user.username else "Без username"

    await state.update_data(telegram=telegram_link)

    await message.answer(
        f"Проверьте данные:\n"
        f"Имя: {data['name']}\n"
        f"Фамилия: {data['surname']}\n"
        f"Email: {data['email']}\n"
        f"Телефон: {data['phone']}\n"
        f"Мероприятие: {data['event']}\n"
        f"Telegram: {telegram_link}",
        reply_markup=get_confirm_keyboard()
    )
    await state.set_state(Registration.confirm)

@router.callback_query(Registration.confirm, F.data == "confirm_yes")
async def confirm_yes(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await save_registration(
        telegram_id=callback.from_user.id,
        name=data["name"],
        surname=data["surname"],
        email=data["email"],
        phone=data["phone"],
        telegram=data["telegram"],
        event=data["event"],
        event_id=data["event_id"]
    )
    await callback.message.answer(
        f"✅ Вы, {data['name']} {data['surname']}, успешно зарегистрированы на мероприятие \"{data['event']}\""
    )
    await state.clear()

@router.callback_query(Registration.confirm, F.data == "confirm_no")
async def confirm_no(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Регистрация отменена.")
    await state.clear()
