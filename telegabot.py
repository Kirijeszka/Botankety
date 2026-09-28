import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

with open(r"C:\Users\ktara\OneDrive\Desktop\Botik\token.txt", "r", encoding="utf-8") as f:
  import os

TOKEN = os.environ.get("TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

logging.basicConfig(level=logging.INFO)
router = Router()

logging.basicConfig(level=logging.INFO)
router = Router()

PENDING_FILE = "pending_users.txt"     # Ждут проверки
ACCEPTED_FILE = "accepted_users.txt"   # Принятые
DENIED_FILE = "denied_users.txt"       # Отклонённые

def check_user_status(user_id: int):
    """Возвращает статус пользователя: 'pending', 'accepted', 'denied' или None"""
    if os.path.exists(ACCEPTED_FILE):
        with open(ACCEPTED_FILE, "r") as f:
            if user_id in [int(line.strip()) for line in f if line.strip().isdigit()]:
                return "accepted"
                
    if os.path.exists(DENIED_FILE):
        with open(DENIED_FILE, "r") as f:
            if user_id in [int(line.strip()) for line in f if line.strip().isdigit()]:
                return "denied"
                
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, "r") as f:
            if user_id in [int(line.strip()) for line in f if line.strip().isdigit()]:
                return "pending"
                
    return None

def add_user_to_file(user_id: int, filename: str):
    """Добавляет ID пользователя в указанный файл"""
    for fn in [PENDING_FILE, ACCEPTED_FILE, DENIED_FILE]:
        if os.path.exists(fn):
            with open(fn, "r") as f:
                lines = f.readlines()
            with open(fn, "w") as f:
                for line in lines:
                    if line.strip() != str(user_id):
                        f.write(line)
                        
    with open(filename, "a") as f:
        f.write(f"{user_id}\n")

class Form(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    q6 = State()
    q7 = State()
    preview = State()

class AdminState(StatesGroup):
    waiting_for_invite = State()

QUESTIONS = [
    ("Вопрос 1: Сколько вам лет?", Form.q1),
    ("Вопрос 2: Ваша отыгровка на рп?(?/10)", Form.q2),
    ("Вопрос 3: Адекватность на рп?(?/10)", Form.q3),
    ("Вопрос 4: Опыт в рп? (в какие проекты играл(а)?)", Form.q4),
    ("Вопрос 5: Сколько по времени играешь в ERLC? (примерное общее наигранное время)", Form.q5),
    ("Вопрос 6: Насколько хорошо знаете карту игры? (?/10)", Form.q6),
    ("Вопрос 7: Насколько часто готовы с нами играть?", Form.q7),
]

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет! Это бот для сбора анкет. Напиши /ready, когда будешь готов отвечать на вопросы (‼️надо отвечать одним сообщением‼️).")

@router.message(Command("ready"))
async def cmd_ready(message: Message, state: FSMContext):
    user_id = message.from_user.id
    status = check_user_status(user_id)
    
    if status == "pending":
        await message.answer(
            "Алло, гараж! 🤨 Твоя анкета уже отправлена и ждёт своей очереди. "
            "Не надо спамить, наберись терпения!"
        )
        return

    if status == "accepted":
        await message.answer("Алло, тебя уже приняли! 😎 Просто перейди по ссылке вверху! 🔗")
        return

    if status == "denied":
        await message.answer("Опоздал! 🚪 Твою анкету отклонили. Повторная подача на этот раз не прокатит.")
        return

    await state.clear()
    await state.set_state(Form.q1)
    await message.answer(QUESTIONS[0][0])

@router.message(Form.q1)
async def step_1(message: Message, state: FSMContext):
    await state.update_data(q1=message.text)
    await state.set_state(Form.q2)
    await message.answer(QUESTIONS[1][0])

@router.message(Form.q2)
async def step_2(message: Message, state: FSMContext):
    await state.update_data(q2=message.text)
    await state.set_state(Form.q3)
    await message.answer(QUESTIONS[2][0])

@router.message(Form.q3)
async def step_3(message: Message, state: FSMContext):
    await state.update_data(q3=message.text)
    await state.set_state(Form.q4)
    await message.answer(QUESTIONS[3][0])

@router.message(Form.q4)
async def step_4(message: Message, state: FSMContext):
    await state.update_data(q4=message.text)
    await state.set_state(Form.q5)
    await message.answer(QUESTIONS[4][0])

@router.message(Form.q5)
async def step_5(message: Message, state: FSMContext):
    await state.update_data(q5=message.text)
    await state.set_state(Form.q6)
    await message.answer(QUESTIONS[5][0])

@router.message(Form.q6)
async def step_6(message: Message, state: FSMContext):
    await state.update_data(q6=message.text)
    await state.set_state(Form.q7)
    await message.answer(QUESTIONS[6][0])

@router.message(Form.q7)
async def step_7(message: Message, state: FSMContext):
    await state.update_data(q7=message.text)
    data = await state.get_data()
    
    preview_text = (
        f"📋 **Вот ваша заполненная анкета:**\n\n"
        f"1. {data.get('q1')}\n"
        f"2. {data.get('q2')}\n"
        f"3. {data.get('q3')}\n"
        f"4. {data.get('q4')}\n"
        f"5. {data.get('q5')}\n"
        f"6. {data.get('q6')}\n"
        f"7. {data.get('q7')}\n\n"
        f"Всё верно? Если да, нажимайте «Отправить». Если хотите переписать — нажмите «Заполнить заново»."
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📤 Отправить", callback_data="confirm_send"),
            InlineKeyboardButton(text="✏️ Заполнить заново", callback_data="restart_form")
        ]
    ])

    await state.set_state(Form.preview)
    await message.answer(preview_text, reply_markup=keyboard)

@router.callback_query(Form.preview, F.data == "confirm_send")
async def process_confirm(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    add_user_to_file(user_id, PENDING_FILE)

    data = await state.get_data()
    user = callback.from_user
    
    username_str = f"@{user.username}" if user.username else f"id: {user.id} (без юзернейма)"

    summary = (f"📝 Новая анкета от пользователя:\n"
        f"👤 Игрок: {user.full_name} ({username_str})\n\n"
        f"1. {data.get('q1')}\n"
        f"2. {data.get('q2')}\n"
        f"3. {data.get('q3')}\n"
        f"4. {data.get('q4')}\n"
        f"5. {data.get('q5')}\n"
        f"6. {data.get('q6')}\n"
        f"7. {data.get('q7')}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Отказать", callback_data=f"deny_{user.id}"),
            InlineKeyboardButton(text="💬 Связаться", callback_data=f"contact_{user.id}")
        ],
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{user.id}")
        ]
    ])

    await callback.bot.send_message(ADMIN_ID, summary, reply_markup=keyboard)
    await callback.message.edit_text("✅ Спасибо! Ваша анкета успешно отправлена администрации. Ожидайте ответа.")
    await state.clear()
    await callback.answer()

@router.callback_query(Form.preview, F.data == "restart_form")
async def process_restart(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(Form.q1)
    await callback.message.edit_text("Хорошо, давайте начнем сначала.\n\n" + QUESTIONS[0][0])
    await callback.answer()

@router.callback_query(F.data.startswith("deny_"))
async def callback_deny(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    add_user_to_file(user_id, DENIED_FILE)

    await callback.bot.send_message(user_id, "К сожалению, ваша анкета отклонена.")
    await callback.message.edit_text(callback.message.text + "\n\n❌ СТАТУС: Отказано")
    await callback.answer()

@router.callback_query(F.data.startswith("contact_"))
async def callback_contact(callback: CallbackQuery):
    parts = callback.data.split("_")
    user_id = parts[1]
    await callback.message.answer(f"💬 Контакт для связи с игроком:\nID: `{user_id}`\nСсылка: tg://user?id={user_id}")
    await callback.answer("Контакт отправлен в чат!")

@router.callback_query(F.data.startswith("accept_"))
async def callback_accept(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[1])
    await state.update_data(target_user_id=user_id)
    await state.set_state(AdminState.waiting_for_invite)
    
    await callback.message.answer("🔗 Отправь следующим сообщением ссылку на Discord, и я перешлю её игроку вместе с поздравлением.")
    await callback.answer()

@router.message(AdminState.waiting_for_invite)
async def send_invite_link(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("target_user_id")
    invite_link = message.text

    add_user_to_file(user_id, ACCEPTED_FILE)

    await message.bot.send_message(
        user_id, 
        f"🎉 Поздравляем! Ваша анкета принята.\nВот ссылка на наш Discord-сервер: {invite_link}"
    )

    await message.answer("✅ Ссылка успешно отправлена игроку!")
    await state.clear()

async def main():
    global bot
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
