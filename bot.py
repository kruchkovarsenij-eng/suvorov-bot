import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- Конфигурация ---
TOKEN = "YOUR_TOKEN_HERE" # Вставь свой токен!
QUESTIONS = [{"s": "С", "q": "Вопрос 1", "t": "open"}] # Для примера

# --- Логика ---
user_sessions = {}
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()
router = Router()

class Survey(StatesGroup):
    answering = State()

def get_scale_keyboard():
    buttons = [InlineKeyboardButton(text=str(i), callback_data=f"scale_{i}") for i in range(1, 11)]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

# ИСПРАВЛЕННЫЙ ХЕНДЛЕР СТАРТА
@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.set_state(Survey.answering)
    user_sessions[message.from_user.id] = {"current_q": 0}
    await next_question(message.chat.id, message.from_user.id, state)

# ИСПРАВЛЕННЫЙ CALLBACK (используем bot.send_message)
@router.callback_query(F.data.startswith("scale_"))
async def scale_answer(callback: CallbackQuery, state: FSMContext):
    await next_question(callback.message.chat.id, callback.from_user.id, state)
    await callback.answer()

async def next_question(chat_id, user_id, state: FSMContext):
    # Логика отправки...
    await bot.send_message(chat_id, "Вопрос...", reply_markup=get_scale_keyboard())

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
