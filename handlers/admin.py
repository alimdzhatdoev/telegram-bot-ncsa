from aiogram import Router, types, F
from config import config
from database.db import get_all_registrations
from aiogram.filters import Command
from utils.excel import generate_excel_for_all_events
from keyboards.admin import get_admin_main_keyboard

router = Router()

@router.message(Command("admin"))
async def show_all_registrations(message: types.Message):
    if message.from_user.id not in config.admin_ids:
        await message.answer("У вас нет прав доступа к этой команде.")
        return

    registrations = await get_all_registrations()

    if not registrations:
        await message.answer("Список регистраций пуст.")
        return

    text = "📋 <b>Список регистраций:</b>\n\n"
    for reg in registrations:
        text += (
            f"👤 {reg['name']} {reg['surname']}\n"
            f"📧 {reg['email']}\n"
            f"🎯 {reg['event']}\n"
            f"🆔 Telegram: {reg['telegram_id']}\n\n"
        )

    await message.answer(text, parse_mode="HTML")

@router.message(Command("export_all"))
async def export_all_excel(message: types.Message):
    generate_excel_for_all_events("all_events.xlsx")

    with open("all_events.xlsx", "rb") as file:
        await message.answer_document(file, caption="📦 Все мероприятия и участники")

@router.message(F.text == "👨‍💼 Админ-панель")
async def admin_panel_button(message: types.Message):
    if message.from_user.id not in config.admin_ids:
        await message.answer("⛔ У вас нет доступа.")
        return

    await message.answer("Добро пожаловать в админ-панель:", reply_markup=get_admin_main_keyboard())