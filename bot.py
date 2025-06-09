# bot.py
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import config
from handlers import start, registration
from database.db import init_db  # ← добавили
from handlers import admin
from handlers import admin_events
import asyncio
from datetime import datetime, timedelta
from utils.events import load_events, format_date
from database.db import get_users_by_event
from aiogram import Bot

sent_notifications = set()

async def notify_upcoming_events(bot: Bot):
    while True:
        events = load_events()
        now = datetime.now()

        for event in events:
            try:
                start_dt = datetime.strptime(f"{event['start_date']} {event['start_time']}", "%Y-%m-%d %H:%M")
                delta = start_dt - now
                minutes_left = int(delta.total_seconds() // 60)

                if minutes_left in [30, 10]:
                    notify_key = f"{event['id']}_{minutes_left}"
                    if notify_key in sent_notifications:
                        continue

                    users = await get_users_by_event(event["title"])
                    for user in users:
                        try:
                            await bot.send_message(
                                chat_id=user["telegram_id"],
                                text=(
                                    f"🔔 Напоминание о мероприятии:\n\n"
                                    f"{event['title']}\n"
                                    f"🕒 Начало в {event['start_time']} {format_date(event['start_date'])}\n"
                                    f"⏳ Осталось {minutes_left} минут"
                                ),
                            )
                        except Exception as e:
                            print(f"Ошибка при отправке пользователю {user['telegram_id']}: {e}")

                    sent_notifications.add(notify_key)

            except Exception as e:
                print(f"Ошибка при проверке мероприятия: {e}")

        await asyncio.sleep(60)  # проверяем каждую минуту

async def main():
    await init_db()
    bot = Bot(token=config.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(registration.router)
    dp.include_router(admin.router)
    dp.include_router(admin_events.router)

    # ⏱️ Запускаем фоновую задачу
    asyncio.create_task(notify_upcoming_events(bot))

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("⛔ Бот остановлен.")

