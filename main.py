import asyncio 
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties

BOT_TOKEN = "8423015034:AAEpGlJ4ksthplBc71ig6YEpuRlgI84tHkI"
ADMIN_USERNAME = "AyyildizOrj"
DB_NAME = "depo.db"

# ---------------- DB ----------------
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS depo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            text TEXT
        )
        """)
        await db.commit()

# ---------------- BOT ----------------
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

# ---------------- /start ----------------
@dp.message(Command("start"))
async def start(msg: types.Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Devam", callback_data="devam")]
        ]
    )
    await msg.answer(
        "📜 <b>Selam Aleykum</b>\n"
        "Cezan Verildi.\n"
        "Botu silmen bir şeyi değiştirmez.",
        reply_markup=kb
    )

# ---------------- DEVAM ----------------
@dp.callback_query(lambda c: c.data == "devam")
async def devam(call: types.CallbackQuery):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT username FROM depo")
        rows = await cursor.fetchall()

    buttons = []
    for r in rows:
        buttons.append(
            [InlineKeyboardButton(text=f"@{r[0]}", callback_data=f"show:{r[0]}")]
        )

    buttons.append(
        [InlineKeyboardButton(text="⬅️ Geri", callback_data="geri")]
    )

    await call.message.edit_text(
        "📂 <b>Kayıtlı Hesaplar</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await call.answer()

# ---------------- SHOW ----------------
@dp.callback_query(lambda c: c.data.startswith("show:"))
async def show(call: types.CallbackQuery):
    username = call.data.split(":")[1]

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT text FROM depo WHERE username=?",
            (username,)
        )
        row = await cursor.fetchone()

    text = row[0] if row else "❌ Veri yok"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Geri", callback_data="devam")]
        ]
    )

    await call.message.delete()

    await call.message.answer(
        f"👤 @{username}\n\n"
        f"<tg-spoiler>{text}</tg-spoiler>",
        reply_markup=kb
    )
    await call.answer()

# ---------------- GERİ ----------------
@dp.callback_query(lambda c: c.data == "geri")
async def geri(call: types.CallbackQuery):
    await start(call.message)
    await call.answer()

# ---------------- ADMIN EKLE ----------------
@dp.message(Command("ekle"))
async def ekle(msg: types.Message):
    if msg.from_user.username != ADMIN_USERNAME:
        return

    try:
        _, username, text = msg.text.split(" ", 2)
        username = username.replace("@", "")
    except:
        return await msg.answer("❌ Kullanım:\n/ekle @kullanici metin")

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR REPLACE INTO depo (username, text) VALUES (?, ?)",
            (username, text)
        )
        await db.commit()

    await msg.answer(f"✅ @{username} eklendi.")

# ---------------- ADMIN SIL ----------------
@dp.message(Command("sil"))
async def sil(msg: types.Message):
    if msg.from_user.username != ADMIN_USERNAME:
        return

    try:
        _, username = msg.text.split(" ", 1)
        username = username.replace("@", "")
    except:
        return await msg.answer("❌ Kullanım:\n/sil @kullanici")

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "DELETE FROM depo WHERE username=?",
            (username,)
        )
        await db.commit()

        if cursor.rowcount == 0:
            return await msg.answer("❌ Böyle bir kullanıcı yok.")

    await msg.answer(f"🗑️ @{username} silindi.")

# ---------------- MIRROR ----------------
async def start_mirror(token: str):
    mirror_bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    mirror_dp = Dispatcher()
    mirror_dp.include_router(dp.router)
    asyncio.create_task(mirror_dp.start_polling(mirror_bot))

# ---------------- MAIN ----------------
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
