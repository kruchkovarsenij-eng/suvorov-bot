import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "8827819420:AAGS-aXjMvsewGkxAJbBwt2SggWU8Opk5qc"
ADMIN_CHAT_ID = 8743677274

logging.basicConfig(level=logging.INFO)

QUESTIONS = [
    {"s": "Личные данные", "q": "Как вас зовут? (ФИО)", "t": "open"},
    {"s": "Личные данные", "q": "Сколько лет вы руководите этой компанией?", "t": "open"},
    {"s": "Стратегия и видение", "q": "Где вы видите компанию через 3–5 лет?\n\n💡 Конкретно: выручка, доля рынка, структура — не «расти и развиваться»", "t": "open"},
    {"s": "Стратегия и видение", "q": "Какие 3 стратегических приоритета вы бы поставили на первое место прямо сейчас?", "t": "open"},
    {"s": "Стратегия и видение", "q": "Что является главным драйвером роста компании?\nЧто — якорем, который тормозит?", "t": "open"},
    {"s": "Стратегия и видение", "q": "Какие возможности вы видите на рынке, которые используете недостаточно?", "t": "open"},
    {"s": "Стратегия и видение", "q": "Что изменится в компании через 2 года, если ничего не менять прямо сейчас?", "t": "open"},
    {"s": "Состояние компании", "q": "Как вы оцениваете текущее состояние компании?\n\n1 — кризис, 10 — отличная форма", "t": "scale"},
    {"s": "Состояние компании", "q": "Что у нас получается лучше всего как у команды?", "t": "open"},
    {"s": "Состояние компании", "q": "В каких областях мы чаще всего сталкиваемся с трудностями?", "t": "open"},
    {"s": "Состояние компании", "q": "Что является самым большим препятствием для развития компании?", "t": "open"},
    {"s": "Состояние компании", "q": "Какие ключевые угрозы вы видите для бизнеса на горизонте 1–3 лет?", "t": "open"},
    {"s": "Состояние компании", "q": "Какие возможности мы упускаем или используем недостаточно?", "t": "open"},
    {"s": "Команда", "q": "Насколько высок уровень доверия в управленческой команде?\n\n1 — нет доверия, 10 — полное доверие", "t": "scale"},
    {"s": "Команда", "q": "Насколько открыто мы обсуждаем проблемы и конфликты?\n\n1 — избегаем, 10 — обсуждаем открыто", "t": "scale"},
    {"s": "Команда", "q": "Оцените взаимодействие между подразделениями\n\n1 — нет взаимодействия, 10 — отличное", "t": "scale"},
    {"s": "Команда", "q": "Что укрепляет команду, а что её ослабляет?", "t": "open"},
    {"s": "Команда", "q": "Какие сильные стороны нашей команды стоит развивать?", "t": "open"},
    {"s": "Команда", "q": "Какие слабые стороны мешают работать эффективнее?", "t": "open"},
    {"s": "Операционка", "q": "Как в компании контролируется выполнение задач?\n\n💡 Что реально происходит, когда задача не выполнена в срок?", "t": "open"},
    {"s": "Операционка", "q": "Как часто задачи выполняются без напоминаний?\n\n1 — никогда, 10 — всегда", "t": "scale"},
    {"s": "Операционка", "q": "Всегда ли понятно, кто за что отвечает?\n\n💡 Есть ли случаи, когда виноватых нет?", "t": "open"},
    {"s": "Операционка", "q": "Бывает ли: ответственный назначен — результата нет — последствий тоже нет?\n\n💡 Опишите конкретный пример", "t": "open"},
    {"s": "Операционка", "q": "Назовите цели компании на текущий год / квартал\n\n💡 Без подготовки — то, что знаете прямо сейчас", "t": "open"},
    {"s": "Операционка", "q": "Насколько планы соответствуют реальности выполнения?\n\n1 — планы не выполняются, 10 — всегда в срок", "t": "scale"},
    {"s": "Операционка", "q": "Насколько совещания в компании результативны?\n\n1 — пустая трата времени, 10 — максимально результативны", "t": "scale"},
    {"s": "Операционка", "q": "После совещаний фиксируются ли решения и ответственные? Как это работает на практике?", "t": "open"},
    {"s": "Система управления", "q": "Насколько компания управляема без вашего личного участия?\n\n1 — без меня всё остановится, 10 — работает самостоятельно", "t": "scale"},
    {"s": "Система управления", "q": "Где вы лично являетесь узким местом системы управления?\n\n💡 В чём вы сами тормозите компанию — честно", "t": "open"},
    {"s": "Система управления", "q": "Какие решения вы вынуждены принимать сами, хотя могли бы делегировать? Почему не делегируете?", "t": "open"},
    {"s": "Система управления", "q": "Что в компании держится только на вас — и почему это опасно?", "t": "open"},
    {"s": "Система управления", "q": "Какое управленческое решение вы откладываете уже давно, хотя знаете, что его нужно принять?", "t": "open"},
    {"s": "Система управления", "q": "Есть ли в команде люди, которые тормозят систему? Что с этим делается?", "t": "open"},
    {"s": "Управленческая команда", "q": "Как вы оцениваете качество своей управленческой команды в целом?\n\n1 — команда слабая, 10 — команда сильная", "t": "scale"},
    {"s": "Управленческая команда", "q": "Кто из команды точно на своём месте? Кто — нет? Почему до сих пор не изменили ситуацию?", "t": "open"},
    {"s": "Управленческая команда", "q": "Кого из команды вы бы взяли с собой, если бы начинали всё заново? Почему?", "t": "open"},
    {"s": "Управленческая команда", "q": "Что происходит в компании, когда вас нет? Приведите конкретный пример.", "t": "open"},
    {"s": "Деньги и потери", "q": "Где компания теряет деньги прямо сейчас, но причина ещё не устранена?", "t": "open"},
    {"s": "Деньги и потери", "q": "Что является самым узким горлышком в компании прямо сейчас?", "t": "open"},
    {"s": "Самооценка лидера", "q": "Какой управленческий стиль вы используете чаще всего?", "t": "choice",
     "opts": ["Директивный (я решаю, команда выполняет)", "Делегирующий (ставлю задачу, доверяю результат)", "Коучинговый (развиваю людей через вопросы)", "Хаотичный (по ситуации, системы нет)"]},
    {"s": "Самооценка лидера", "q": "Что вы готовы изменить в собственном стиле управления?\n\n💡 Конкретно — не «стать лучше», а что именно и в какой срок", "t": "open"},
    {"s": "Самооценка лидера", "q": "Назовите одну вещь, которую вы бы изменили в компании завтра, если бы не было сопротивления.", "t": "open"},
    {"s": "Самооценка лидера", "q": "Что вы хотите получить от диагностики и консалтинга?\n\n💡 Конкретная метрика успеха, которую готовы зафиксировать как результат", "t": "open"},
]

user_sessions = {}


def get_scale_keyboard():
    row1 = [InlineKeyboardButton(str(i), callback_data=f"scale_{i}") for i in range(1, 6)]
    row2 = [InlineKeyboardButton(str(i), callback_data=f"scale_{i}") for i in range(6, 11)]
    return InlineKeyboardMarkup([row1, row2])


def get_choice_keyboard(opts):
    rows = [[InlineKeyboardButton(opt, callback_data=f"choice_{i}")] for i, opt in enumerate(opts)]
    return InlineKeyboardMarkup(rows)


def format_report(session):
    answers = session["answers"]
    name = answers[0] if answers else "Аноним"
    lines = [
        "📋 ДИАГНОСТИКА — «Пластик Руси»",
        f"👤 {name}",
        f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        f"📱 @{session.get('username', '—')} | ID: {session['user_id']}",
        "",
    ]
    current_section = ""
    for i, q in enumerate(QUESTIONS):
        if q["s"] != current_section:
            current_section = q["s"]
            lines.append(f"\n{'━'*28}")
            lines.append(f"📌 {current_section.upper()}")
            lines.append(f"{'━'*28}")
        short_q = q["q"].split("\n")[0]
        ans = answers[i] if i < len(answers) and answers[i] else "—"
        if q["t"] == "scale":
            try:
                score = int(ans)
                bar = "█" * score + "░" * (10 - score)
                lines.append(f"\n{i+1}. {short_q}")
                lines.append(f"   [{bar}] {ans}/10")
            except Exception:
                lines.append(f"\n{i+1}. {short_q}\n   → {ans}")
        else:
            lines.append(f"\n{i+1}. {short_q}")
            lines.append(f"   → {ans}")
    return "\n".join(lines)


async def send_question(chat_id, context, session):
    idx = session["current"]
    q = QUESTIONS[idx]
    total = len(QUESTIONS)
    progress = int((idx / total) * 10)
    bar = "▓" * progress + "░" * (10 - progress)

    section_changed = idx == 0 or QUESTIONS[idx]["s"] != QUESTIONS[idx - 1]["s"]
    header = f"📌 *{q['s']}*\n\n" if section_changed else ""
    text = f"{header}*Вопрос {idx+1} из {total}*\n{bar}\n\n{q['q']}"

    if q["t"] == "scale":
        await context.bot.send_message(chat_id, text, reply_markup=get_scale_keyboard(), parse_mode="Markdown")
    elif q["t"] == "choice":
        await context.bot.send_message(chat_id, text, reply_markup=get_choice_keyboard(q["opts"]), parse_mode="Markdown")
    else:
        await context.bot.send_message(chat_id, text, parse_mode="Markdown")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_sessions[user.id] = {
        "current": 0,
        "answers": [],
        "user_id": user.id,
        "username": user.username or "",
    }
    await update.message.reply_text(
        "👋 Добро пожаловать!\n\n"
        "Это диагностика для собственника\n"
        "*«Менеджмент по-Суворовски»* — «Пластик Руси»\n\n"
        "📝 *43 вопроса* о стратегии, команде и вас как лидере.\n"
        "⏱ Займёт 15–25 минут.\n\n"
        "Отвечайте честно — это только для вас и консультанта.\n\n"
        "Поехали! 🚀",
        parse_mode="Markdown"
    )
    await asyncio.sleep(0.5)
    await send_question(update.effective_chat.id, context, user_sessions[user.id])


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_sessions:
        await update.message.reply_text("Введите /start чтобы начать диагностику.")
        return

    session = user_sessions[user_id]
    idx = session["current"]
    q = QUESTIONS[idx]

    if q["t"] in ("scale", "choice"):
        await update.message.reply_text("👆 Пожалуйста, выберите вариант кнопкой выше.")
        return

    answer = update.message.text.strip()
    if not answer:
        return

    session["answers"].append(answer)
    session["current"] += 1

    if session["current"] >= len(QUESTIONS):
        await finish(update.effective_chat.id, context, session)
    else:
        await send_question(update.effective_chat.id, context, session)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_sessions:
        await query.edit_message_text("Введите /start чтобы начать диагностику.")
        return

    session = user_sessions[user_id]
    idx = session["current"]
    q = QUESTIONS[idx]
    data = query.data

    if data.startswith("scale_") and q["t"] == "scale":
        val = data.replace("scale_", "")
        session["answers"].append(val)
        session["current"] += 1
        short_q = q["q"].split("\n")[0]
        await query.edit_message_text(f"✅ *{short_q}*\n→ {val}/10", parse_mode="Markdown")
    elif data.startswith("choice_") and q["t"] == "choice":
        val_idx = int(data.replace("choice_", ""))
        val = q["opts"][val_idx]
        session["answers"].append(val)
        session["current"] += 1
        short_q = q["q"].split("\n")[0]
        await query.edit_message_text(f"✅ *{short_q}*\n→ {val}", parse_mode="Markdown")
    else:
        return

    if session["current"] >= len(QUESTIONS):
        await finish(query.message.chat_id, context, session)
    else:
        await send_question(query.message.chat_id, context, session)


async def finish(chat_id, context, session):
    await context.bot.send_message(
        chat_id,
        "🎉 *Диагностика завершена!*\n\n"
        "Спасибо за честные ответы.\n"
        "Ваши результаты отправлены консультанту.\n\n"
        "📞 По вопросам: @suvorovez · 8-958-159-08-07 · Артемий",
        parse_mode="Markdown"
    )
    report = format_report(session)
    chunks = [report[i:i+4000] for i in range(0, len(report), 4000)]
    for j, chunk in enumerate(chunks):
        prefix = "🏁 *ОТЧЁТ ДИАГНОСТИКИ*\n\n" if j == 0 else ""
        await context.bot.send_message(ADMIN_CHAT_ID, prefix + chunk, parse_mode="Markdown")
    if session["user_id"] in user_sessions:
        del user_sessions[session["user_id"]]


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    if not user_sessions:
        await update.message.reply_text("Активных сессий нет.")
        return
    lines = [f"*Активные сессии:* {len(user_sessions)}\n"]
    for uid, s in user_sessions.items():
        lines.append(f"@{s.get('username','—')} — вопрос {s['current']+1}/43")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен ✅")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
