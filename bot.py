import sys
import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Моментальный вывод логов для Railway
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("--- [DOCKER START] СТАРТ ЧИСТОГО ЯДРА БОТА ---", flush=True)

TOKEN = "8827819420:AAGS-aXjMvsewGkxAJbBwt2SggWU8Opk5qc"
ADMIN_CHAT_ID = 8743677274
EXCEL_FILE = "/app/data/diagnostics_results.xlsx"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

QUESTIONS = [
    {"s": "Личные данные", "q": "Как вас зовут? (ФИО)", "t": "open"},
    {"s": "Личные данные", "q": "Сколько лет вы руководите этой компанией?", "t": "open"},
    {"s": "Стратегия и видение", "q": "Где вы видите компанию через 3–5 лет?\n\n 💡 Конкретно: выручка, доля рынка, структура — не «расти и развиваться»", "t": "open"},
    {"s": "Стратегия и видение", "q": "Какие 3 стратегических приоритета вы бы поставили на первое место прямо сейчас?", "t": "open"},
    {"s": "Стратегия и видение", "q": "Что является главным драйвером роста компании?\n Что — якорем, который тормозит?", "t": "open"},
    {"s": "Стратегия и видение", "q": "Какие возможности вы видите на рынке, которые используете недостаточно?", "t": "open"},
    {"s": "Стратегия и видение", "q": "Что изменится в компании через 2 года, если ничего не менять прямо сейчас?", "t": "open"},
    {"s": "Состояние компании", "q": "Как вы оцениваете текущее состояние компании?\n\n 1 — кризис, 10 — отличная форма", "t": "scale"},
    {"s": "Состояние компании", "q": "Что у нас получается лучше всего как у команды?", "t": "open"},
    {"s": "Состояние компании", "q": "В каких областях мы чаще всего сталкиваемся с трудностями?", "t": "open"},
    {"s": "Состояние компании", "q": "Что является самым большим препятствием для развития компании?", "t": "open"},
    {"s": "Состояние компании", "q": "Какие ключевые угрозы вы видите для бизнеса на горизонте 1–3 лет?", "t": "open"},
    {"s": "Состояние компании", "q": "Какие возможности мы упускаем или используем недостаточно?", "t": "open"},
    {"s": "Команда", "q": "Насколько высок уровень доверия в управленческой команде?\n\n 1 — нет доверия, 10 — полное доверие", "t": "scale"},
    {"s": "Команда", "q": "Насколько открыто мы обсуждаем проблемы и конфликты?\n\n 1 — избегаем, 10 — обсуждаем открыто", "t": "scale"},
    {"s": "Команда", "q": "Оцените взаимодействие между подразделениями\n\n 1 — нет взаимодействия, 10 — отличное", "t": "scale"},
    {"s": "Команда", "q": "Что укрепляет команду, а что её ослабляет?", "t": "open"},
    {"s": "Команда", "q": "Какие сильные стороны нашей команды стоит развивать?", "t": "open"},
    {"s": "Команда", "q": "Какие слабые стороны мешают работать эффективнее?", "t": "open"},
    {"s": "Операционка", "q": "Как в компании контролируется выполнение задач?\n\n 💡 Что реально происходит, когда задача не выполнена в срок?", "t": "open"},
    {"s": "Операционка", "q": "Как часто задачи выполняются без напоминаний?\n\n 1 — никогда, 10 — всегда", "t": "scale"},
    {"s": "Операционка", "q": "Всегда ли понятно, кто за что отвечает?\n\n 💡 Есть ли случаи, когда виноватых нет?", "t": "open"},
    {"s": "Операционка", "q": "Бывает ли: ответственный назначен — результата нет — последствий тоже нет?\n\n 💡 Опишите конкретный пример", "t": "open"},
    {"s": "Операционка", "q": "Назовите цели компании на текущий год / квартал\n\n 💡 Без подготовки — то, что знаете прямо сейчас", "t": "open"},
    {"s": "Операционка", "q": "Насколько планы соответствуют реальности выполнения?\n\n 1 — планы не выполняются, 10 — всегда в срок", "t": "scale"},
    {"s": "Операционка", "q": "Насколько совещания в компании результативны?\n\n 1 — пустая трата времени, 10 — максимально результативны", "t": "scale"},
    {"s": "Операционка", "q": "После совещаний фиксируются ли решения и ответственные? Как это работает на практике?", "t": "open"},
    {"s": "Система управления", "q": "Насколько компания управляема без вашего личного участия?\n\n 1 — без меня всё остановится, 10 — работает самостоятельно", "t": "scale"},
    {"s": "Система управления", "q": "Где вы лично являетесь узким местом системы управления?\n\n 💡 В чём вы сами тормозите компанию — честно", "t": "open"},
    {"s": "Система управления", "q": "Какие решения вы вынуждены принимать сами, хотя могли бы делегировать? Почему не делегируете?", "t": "open"},
    {"s": "Система управления", "q": "Что в компании держится только на вас — и почему это опасно?", "t": "open"},
    {"s": "Система управления", "q": "Какое управленческое решение вы откладываете уже давно, хотя знаете, что его нужно принять?", "t": "open"},
    {"s": "Система управления", "q": "Есть ли в команде люди, которые тормозят систему? Что с этим делается?", "t": "open"},
    {"s": "Управленческая команда", "q": "Как вы оцениваете качество своей управленческой команды в целом?\n\n 1 — команда слабая, 10 — команда сильная", "t": "scale"},
    {"s": "Управленческая команда", "q": "Кто из команды точно на своём месте? Кто — нет? Почему до сих пор не изменили ситуацию?", "t": "open"},
    {"s": "Управленческая команда", "q": "Кого из команды вы бы взяли с собой, если бы начинали всё заново? Почему?", "t": "open"},
    {"s": "Управленческая команда", "q": "Что происходит в компании, когда вас нет? Приведите конкретный пример.", "t": "open"},
    {"s": "Деньги и потери", "q": "Где компания теряет деньги прямо сейчас, но причина ещё не устранена?", "t": "open"},
    {"s": "Деньги и потери", "q": "Что является самым узким горлышком в компании прямо сейчас?", "t": "open"},
    {"s": "Самооценка лидера", "q": "Какой управленческий стиль вы используете чаще всего?", "t": "choice", "opts": ["Директивный (я решаю, команда выполняет)", "Делегирующий (ставлю задачу, доверяю результат)", "Коучинговый (развиваю людей через вопросы)", "Хаотичный (по ситуации, системы нет)"]},
    {"s": "Самооценка лидера", "q": "Что вы готовы изменить в собственном стиле управления?\n\n 💡 Конкретно — не «стать лучше», а что именно и в какой срок", "t": "open"},
    {"s": "Самооценка лидера", "q": "Назовите одну вещь, которую вы бы изменили в компании завтра, если бы не было сопротивления.", "t": "open"},
    {"s": "Самооценка лидера", "q": "Что вы хотите получить от диагностики и консалтинга?\n\n 💡 Конкретная метрика успеха, которую готовы зафиксировать как результат", "t": "open"},
]

user_sessions = {}

def init_excel():
    os.makedirs(os.path.dirname(EXCEL_FILE), exist_ok=True)
    if os.path.exists(EXCEL_FILE): return
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
    for cell in ws:
        cell.font, cell.fill, cell.alignment = hf, hf_fill, ca
    ws.row_dimensions.height = 35
    wb.save(EXCEL_FILE)

def append_to_excel(session):
    init_excel()
    try:
        import openpyxl
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb.active
        row_data = [datetime.now().strftime("%d.%m.%Y %H:%M"), str(session["user_id"]), f"@{session['username']}" if session["username"] else "—"]
        for i in range(len(QUESTIONS)):
            row_data.append(str(session["answers"][i]) if i < len(session["answers"]) else "—")
        ws.append(row_data)
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            ws.column_dimensions[openpyxl.utils.get_column_letter(col.column)].width = min(max(max_len + 3, 12), 60)
        wb.save(EXCEL_FILE)
    except Exception as e:
        logger.error(f"Excel error: {e}")

def get_scale_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton(str(i), callback_data=f"scale_{i}") for i in range(1, 6)], [InlineKeyboardButton(str(i), callback_data=f"scale_{i}") for i in range(6, 11)]])

def get_choice_keyboard(opts):
    return InlineKeyboardMarkup([[InlineKeyboardButton(opt, callback_data=f"choice_{i}")] for i, opt in enumerate(opts)])

def format_report(session):
    answers = session["answers"]
    lines = ["📋 ДИАГНОСТИКА — «Пластик Руси»", f"👤 ID: {session['user_id']}", f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}", ""]
    current_section = ""
    for i, q in enumerate(QUESTIONS):
        if q["s"] != current_section:
            current_section = q["s"]
            lines.extend([f"\n{'━'*28}", f"📌 {current_section.upper()}", f"{'━'*28}"])
        ans = answers[i] if i < len(answers) else "—"
        clean_q = q['q'].replace('\n\n', ' ').replace('\n', ' ')
        lines.append(f"\n{i+1}. {clean_q}\n   → {ans}")
    return "\n".join(lines)

async def send_question(chat_id, context, session):
    idx = session["current"]
    if idx >= len(QUESTIONS):
        await finish(chat_id, context, session)
        return
    q = QUESTIONS[idx]
    progress = int((idx / len(QUESTIONS)) * 10)
    text = f"📌 *{q['s']}*\n\n*Вопрос {idx+1} из {len(QUESTIONS)}*\n{'▓'*progress + '░'*(10-progress)}\n\n{q['q']}"
    rm = get_scale_keyboard() if q["t"] == "scale" else (get_choice_keyboard(q["opts"]) if q["t"] == "choice" else None)
    await context.bot.send_message(chat_id, text, reply_markup=rm, parse_mode="Markdown")
    session["lock"] = False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
