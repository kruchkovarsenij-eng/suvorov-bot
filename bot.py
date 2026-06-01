import sys
import os
import subprocess
import asyncio
import logging
from datetime import datetime

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
print("--- [DOCKER START] ИНИЦИАЛИЗАЦИЯ СИСТЕМНОГО ОКРУЖЕНИЯ ---", flush=True)

try:
    import aiogram
    import openpyxl
except ModuleNotFoundError:
    print("Кэш сборщика пуст. Принудительно устанавливаю библиотеки...", flush=True)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiogram>=3.0.0", "openpyxl"])
    print("Установка успешно завершена! ✅", flush=True)

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

print("--- [DOCKER START] ЗАПУСК СВЕРХНАДЕЖНОГО AIOGRAM ЯДРА ---", flush=True)

TOKEN = "8959504034:AAFTvRop6ApDFX6dCnngx50LmEye_WtZ6C4"
ADMIN_CHAT_ID = 8743677274
EXCEL_FILE = "diagnostics_results.xlsx"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

session = AiohttpSession()
bot = Bot(token=TOKEN, session=session, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()
router = Router()

QUESTIONS = [
    # ... весь твой список вопросов остаётся без изменений ...
]

class Survey(StatesGroup):
    answering = State()

user_sessions = {}

def init_excel():
    if os.path.exists(EXCEL_FILE):
        return
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ответы"
    hf = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    hf_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    ca = Alignment(horizontal="center", vertical="center", wrap_text=True)
    headers = ["Дата прохождения", "ID Пользователя", "Никнейм (username)"]
    for i, q in enumerate(QUESTIONS):
        headers.append(f"Вопрос {i+1}: {q['q'].replace('\n', ' ')} [{q['s']}]")
    ws.append(headers)
    for cell in ws[1]:
        cell.font, cell.fill, cell.alignment = hf, hf_fill, ca
    ws.row_dimensions[1].height = 35
    wb.save(EXCEL_FILE)

def save_to_excel_final(user_id, username, answers_list):
    init_excel()
    try:
        import openpyxl
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
        row_data = [datetime.now().strftime("%d.%m.%Y %H:%M"), str(user_id), f"@{username}" if username else "—"]
        for i in range(len(QUESTIONS)):
            row_data.append(str(answers_list[i]) if i < len(answers_list) else "—")
        ws.append(row_data)
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            ws.column_dimensions[openpyxl.utils.get_column_letter(col[0].column)].width = min(max(max_len + 3, 12), 60)
        wb.save(EXCEL_FILE)
    except Exception as e:
        logging.error(f"Excel error: {e}")

def get_scale_keyboard():
    buttons1 = [InlineKeyboardButton(text=str(i), callback_data=f"scale_{i}") for i in range(1, 6)]
    buttons2 = [InlineKeyboardButton(text=str(i), callback_data=f"scale_{i}") for i in range(6, 11)]
    return InlineKeyboardMarkup(inline_keyboard=[buttons1, buttons2])

def get_choice_keyboard(opts):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=opt, callback_data=f"choice_{i}")] for i, opt in enumerate(opts)
    ])

def format_report(user_id, username, answers_list):
    lines = [
        "📋 ДИАГНОСТИКА — «Пластик Руси»",
        f"👤 ID: {user_id}",
        f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        ""
    ]
    current_section = ""
    for i, q in enumerate(QUESTIONS):
        if q["s"] != current_section:
            current_section = q["s"]
            lines.extend([f"\n{'━'*28}", f"📌 {current_section.upper()}", f"{'━'*28}"])
        ans = answers_list[i] if i < len(answers_list) else "—"
        clean_q = q['q'].replace('\n\n', ' ').replace('\n', ' ')
        lines.append(f"❓ {clean_q}")
        lines.append(f"➜ {ans}")
    return "\n".join(lines)

# ---------------- Прогресс-бар ----------------
def get_progress_bar(current_question, total_questions):
    bar_length = 20
    filled = int(bar_length * current_question / total_questions)
    bar = '▓' * filled + '░' * (bar_length - filled)
    return f"Прогресс: {bar} [{current_question}/{total_questions}]"

# ---------------- Хендлеры ----------------
@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.set_state(Survey.answering)
    user_sessions[message.from_user.id] = {
        "current_q": 0,
        "answers": []
    }
    q = QUESTIONS[0]
    progress = get_progress_bar(1, len(QUESTIONS))
    text = f"{progress}\n\n{q['q']}"
    if q["t"] == "scale":
        await message.answer(text, reply_markup=get_scale_keyboard())
    elif q["t"] == "choice":
        await message.answer(text, reply_markup=get_choice_keyboard(q["opts"]))
    else:
        await message.answer(text)

@router.callback_query(F.data.startswith("scale_"))
async def scale_answer(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    session = user_sessions.get(user_id)
    if not session:
        await callback.answer("Начните с /start")
        return
    value = callback.data.split("_")[1]
    session["answers"].append(value)
    session["current_q"] += 1
    await next_question(callback.message, user_id, state)
    await callback.answer()

@router.callback_query(F.data.startswith("choice_"))
async def choice_answer(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    session = user_sessions.get(user_id)
    if not session:
        await callback.answer("Начните с /start")
        return
    idx = int(callback.data.split("_")[1])
    q_idx = session["current_q"]
    answer_text = QUESTIONS[q_idx]["opts"][idx]
    session["answers"].append(answer_text)
    session["current_q"] += 1
    await next_question(callback.message, user_id, state)
    await callback.answer()

@router.message(Survey.answering)
async def open_answer(message: Message, state: FSMContext):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)
    if not session:
        await message.answer("Начните с /start")
        return
    session["answers"].append(message.text)
    session["current_q"] += 1
    await next_question(message, user_id, state)

async def next_question(msg, user_id, state: FSMContext):
    session = user_sessions[user_id]
    idx = session["current_q"]   # Индекс следующего вопроса
    if idx >= len(QUESTIONS):
        # Опрос завершён
        save_to_excel_final(user_id, msg.from_user.username, session["answers"])
        report = format_report(user_id, msg.from_user.username, session["answers"])
        await msg.answer("✅ Спасибо за ответы! Вот ваша диагностика:\n\n" + report)
        await state.clear()
        return

    q = QUESTIONS[idx]
    progress = get_progress_bar(idx + 1, len(QUESTIONS))   # Пользовательский номер = idx+1
    text = f"{progress}\n\n{q['q']}"
    if q["t"] == "scale":
        await msg.answer(text, reply_markup=get_scale_keyboard())
    elif q["t"] == "choice":
        await msg.answer(text, reply_markup=get_choice_keyboard(q["opts"]))
    else:
        await msg.answer(text)

# ---------------- Запуск ----------------
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
