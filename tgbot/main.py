import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime, timedelta
from models import Subscriptions
from states import AddSubState

# Bot tokenni bu yerga joylash:
BOT_TOKEN = "8593216205:AAE1sjrUTSc-ZjrfGzwC8akPCsAAQIs2XYc"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- START komandasi ---
@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    await msg.answer(
        "👋 Salom! Men 'Obuna Nazoratchisi' botman.\n"
        "Sizga pullik xizmatlaringizni (Netflix, Telegram Premium va boshqalar) kuzatishda yordam beraman.\n\n"
        "➕ Yangi obuna qo‘shish uchun /add yuboring.\n"
        "📜 Obunalarni ko‘rish uchun /mysubs yuboring.\n"
        "📊 Xarajatlarni ko‘rish uchun /summary yuboring."
    )

# --- Yangi obuna qo‘shish ---
@dp.message(Command("add"))
async def addsub_start(msg: types.Message, state: FSMContext):
    await msg.answer("📛 Obuna nomini kiriting (masalan: Netflix):")
    await state.set_state(AddSubState.nick)

@dp.message(AddSubState.nick)
async def addsub_name(msg: types.Message, state: FSMContext):
    await state.update_data(nick=msg.text)
    await msg.answer("💰 Oylik summani kiriting (masalan: 50000):")
    await state.set_state(AddSubState.amount)

@dp.message(AddSubState.amount)
async def addsub_amount(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("❌ Iltimos, faqat raqam kiriting.")
        return
    await state.update_data(amount=int(msg.text))
    await msg.answer("📅 Keyingi to‘lov sanasini kiriting (YYYY-MM-DD formatda):")
    await state.set_state(AddSubState.term)

@dp.message(AddSubState.term)
async def addsub_term(msg: types.Message, state: FSMContext):
    try:
        term = datetime.strptime(msg.text, "%Y-%m-%d")
    except ValueError:
        await msg.answer("❌ Sana formati noto‘g‘ri! Masalan: 2025-11-12")
        return

    data = await state.get_data()
    Subscriptions.create(
        user_id=msg.from_user.id,
        nick=data["nick"],
        amount=data["amount"],
        term=term
    )

    await msg.answer(f"✅ Obuna qo‘shildi!\n\n📛 {data['nick']}\n💰 {data['amount']} so‘m\n📅 {term.date()}")
    await state.clear()

# --- Obunalarni ko‘rsatish ---
@dp.message(Command("mysubs"))
async def showsubs(msg: types.Message):
    subs = list(Subscriptions.select().where(Subscriptions.user_id == msg.from_user.id))
    
    if subs:
        text = "\n".join([
            f"📛 {sub.nick}\n💰 {sub.amount} so‘m\n📅 {sub.term.strftime('%Y-%m-%d')}\n"
            for sub in subs
        ])
        await msg.answer(f"📜 Sizning obunalaringiz:\n\n{text}")
    else:
        await msg.answer("❌ Sizda hali hech qanday obuna yo‘q.")

# --- Umumiy xarajatlar ---
@dp.message(Command("summary"))
async def summary(msg: types.Message):
    subs = Subscriptions.select().where(Subscriptions.user_id == msg.from_user.id)
    total = sum(sub.amount for sub in subs)
    await msg.answer(f"📊 Jami oylik xarajatlaringiz: {total} so‘m")

# --- Eslatmalar (async scheduler) ---
async def remind_payments():
    while True:
        now = datetime.now()
        subs = Subscriptions.select()
        for sub in subs:
            if 0 < (sub.term - now).days <= 3:  # 3 kun qoldi
                try:
                    await bot.send_message(
                        sub.user_id,
                        f"⏰ Eslatma!\nSizning '{sub.nick}' obunangiz uchun to‘lov kuni {sub.term.date()} ga yaqinlashmoqda!"
                    )
                except Exception:
                    pass
        await asyncio.sleep(86400)  # har 24 soatda tekshirish

# --- Botni ishga tushurish ---
async def main():
    asyncio.create_task(remind_payments())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
