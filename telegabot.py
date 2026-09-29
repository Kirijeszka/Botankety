import asyncio 
import os
import threading 
from http.server import HTTPServer, BaseHTTPRequestHandler 
from aiogram import Bot, Dispatcher, F, Router 
from aiogram.types import Message, CallbackQuery 
from aiogram.fsm.context import FSMContext 
from aiogram.fsm.state import State, StatesGroup

TOKEN = os.getenv("BOT_TOKEN", "ТВОЙ_ТОКЕН") 
ACCEPTED_FILE = "accepted_users.txt"

class AdminState(StatesGroup): 
  waiting_for_invite = State()
  
def add_user_to_file(user_id, filename): 
  with open(filename, "a", encoding="utf-8") as f: 
    f.write(f"{user_id}\n")
    
class SimpleHandler(BaseHTTPRequestHandler): 
  def do_GET(self): 
    self.send_response(200) 
    self.end_headers() 
    self.wfile.write(b"Bot is alive!")
    
def run_dummy_server():
  port = int(os.environ.get("PORT", 10000))
  server = HTTPServer(("0.0.0.0", port), SimpleHandler) 
  server.serve_forever()
  
router = Router()

@router.callback_query(F.data.startswith("contact_")) 
async def callback_contact(callback: CallbackQuery): 
  parts = callback.data.split("_") 
  user_id = parts[1] 
  await callback.message.answer(f"💬 Контакт для связи с игроком:\nID: {user_id}\nСсылка: tg://user?id={user_id}") 
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
if __name__ == "main": 
  server_thread = threading.Thread(target=run_dummy_server, daemon=True) 
  server_thread.start() 
  asyncio.run(main())
