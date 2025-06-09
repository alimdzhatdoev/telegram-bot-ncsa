import aiosqlite

DB_NAME = "event_bot.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                name TEXT,
                surname TEXT,
                email TEXT,
                phone TEXT,
                telegram TEXT,
                event TEXT,
                event_id INTEGER
            )
        """)
        await db.commit()

async def save_registration(telegram_id, name, surname, email, phone, telegram, event, event_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO registrations (
                telegram_id,
                name,
                surname,
                email,
                phone,
                telegram,
                event,
                event_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            telegram_id,
            name,
            surname,
            email,
            phone,
            telegram,
            event,
            event_id
        ))
        await db.commit()

async def get_all_registrations():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM registrations")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_user_registrations(telegram_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT event, event_id, email, phone FROM registrations WHERE telegram_id = ?",
            (telegram_id,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def cancel_registration(telegram_id: int, event_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "DELETE FROM registrations WHERE telegram_id = ? AND event_id = ?",
            (telegram_id, event_id)
        )
        await db.commit()

async def get_users_by_event(event_title: str):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT telegram_id, name, surname, email, phone, telegram FROM registrations WHERE event = ?",
            (event_title,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_all_registrations():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM registrations")
        return [dict(row) for row in await cursor.fetchall()]

async def get_registrations_by_event(event_title: str):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM registrations WHERE event = ?", (event_title,))
        return [dict(row) for row in await cursor.fetchall()]
