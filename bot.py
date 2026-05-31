import json
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

TOKEN = "8827819420:AAGS-aXjMvsewGkxAJbBwt2SggWU8Opk5qc"
ADMIN_CHAT_ID = 8743677274
API = f"https://api.telegram.org/bot{TOKEN}"

QUESTIONS = [
    {"s": "Личные данные", "q": "Как вас зовут? (ФИО)", "t": "open"},
    {"s": "Личные данные", "q": "Сколько лет вы руководите этой компанией?", "t": "open"},
    {"s": "Стратегия и видение", "q": "Где вы видите компанию через 3–5 лет?\n\nКонкретно: выручка, доля рынка, структура — не «расти и развиваться»", "t": "open"},
    {"s": "Стратегия и видение", "q": "Какие 3 стратегических приоритета вы бы поставили на первое место прямо сейчас?", "t": "open"},
    {"s": "Стратегия и видение", "q": "Что является главным драйвером роста компании? Что — якорем, который тормозит?", "t": "open"},
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
    {"s": "Операционка", "q": "Как в компании контролируется выполнение задач?\n\nЧто реально происходит, когда задача не выполнена в срок?", "t": "open"},
    {"s": "Операционка", "q": "Как часто задачи выполняются без напоминаний?\n\n1 — никогда, 10 — всегда", "t": "scale"},
    {"s": "Операционка", "q": "Всегда ли понятно, кто за что отвечает?\n\nЕсть ли случаи, когда виноватых нет?", "t": "open"},
    {"s": "Операционка", "q": "Бывает ли: ответственный назначен — результата нет — последствий тоже нет?\n\nОпишите конкретный пример", "t": "open"},
    {"s": "Операционка", "q": "Назовите цели компании на текущий год / квартал\n\nБез подготовки — то, что знаете прямо сейчас", "t": "open"},
    {"s": "Операционка", "q": "Насколько планы соответствуют реальности выполнения?\n\n1 — планы не выполняются, 10 — всегда в срок", "t": "scale"},
    {"s": "Операционка", "q": "Насколько совещания в компании результативны?\n\n1 — пустая трата времени, 10 — максимально результативны", "t": "scale"},
    {"s": "Операционка", "q": "После совещаний фиксируются ли решения и ответственные? Как это работает на практике?", "t": "open"},
    {"s": "Система управления", "q": "Насколько компания управляема без вашего личного участия?\n\n1 — без меня всё остановится, 10 — работает самостоятельно", "t": "scale"},
    {"s": "Система управления", "q": "Где вы лично являетесь узким местом системы управления?\n\nВ чём вы сами тормозите компанию — честно", "t": "open"},
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
    {"s": "Самооценка лидера", "q": "Какой управленческий стиль вы используете чаще всего?\n\n1. Директивный (я решаю, команда выполняет)\n2. Делегирующий (ставлю задачу, доверяю результат)\n3. Коучинговый (развиваю людей через вопросы)\n4. Хаотичный (по ситуации, системы нет)\n\nОтветьте цифрой 1, 2, 3 или 4", "t": "open"},
    {"s": "Самооценка лидера", "q": "Что вы готовы изменить в собственном стиле управления?\n\nКонкретно — не «стать лучше», а что именно и в какой срок", "t": "open"},
    {"s": "Самооценка лидера", "q": "Назовите одну вещь, которую вы бы изменили в компании завтра, если бы не было сопротивления.", "t": "open"},
    {"s": "Самооценка лидера", "q": "Что вы хотите получить от диагностики и консалтинга?\n\nКонкретная метрика успеха, которую готовы зафиксировать как результат", "t": "open"},
]

sessions = {}


def api_call(method, data=None):
    url = f"{API}/{method}"
    if data:
        payload = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"API error {method}: {e}")
        return None


def send_message(chat_id, text, keyboard=None):
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    return api_call("sendMessage", data)


def edit_message(chat_id, message_id, text):
    api_call("editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": text})


def answer_callback(callback_id):
    api_call("answerCallbackQuery", {"callback_query_id": callback_id})


def scale_keyboard():
    return {
        "inline_keyboard": [
            [{"text": str(i), "callback_data": f"s_{i}"} for i in range(1, 6)],
            [{"text": str(i), "callback_data": f"s_{i}"} for i in range(6, 11)],
        ]
    }


def format_report(session):
    answers = session["answers"]
    name = answers[0] if answers else "Аноним"
    lines = [
        "ДИАГНОСТИКА — «Пластик Руси»",
        f"Имя: {name}",
        f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        f"Username: @{session.get('username', '—')} | ID: {session['uid']}",
        "",
    ]
    cur_sec = ""
    for i, q in enumerate(QUESTIONS):
        if q["s"] != cur_sec:
            cur_sec = q["s"]
            lines.append(f"\n=== {cur_sec.upper()} ===")
        short = q["q"].split("\n")[0]
        ans = answers[i] if i < len(answers) and answers[i] else "—"
        if q["t"] == "scale":
            try:
                sc = int(ans)
                bar = "█" * sc + "░" * (10 - sc)
            except Exception:
                bar = ""
            lines.append(f"\n{i+1}. {short}")
            lines.append(f"   [{bar}] {ans}/10")
        else:
            lines.append(f"\n{i+1}. {short}")
            lines.append(f"   → {ans}")
    return "\n".join(lines)


def ask(chat_id, session):
    idx = session["current"]
    q = QUESTIONS[idx]
    total = len(QUESTIONS)
    prog = int((idx / total) * 10)
    bar = "▓" * prog + "░" * (10 - prog)

    sec_changed = idx == 0 or QUESTIONS[idx]["s"] != QUESTIONS[idx - 1]["s"]
    header = f"[ {q['s']} ]\n\n" if sec_changed else ""
    text = f"{header}Вопрос {idx+1} из {total}\n{bar}\n\n{q['q']}"

    if q["t"] == "scale":
        send_message(chat_id, text, scale_keyboard())
    else:
        send_message(chat_id, text)


def finish(chat_id, session):
    send_message(chat_id,
        "Диагностика завершена!\n\n"
        "Спасибо за честные ответы.\n"
        "Результаты отправлены консультанту.\n\n"
        "По вопросам: @suvorovez | 8-958-159-08-07 | Артемий"
    )
    report = format_report(session)
    chunks = [report[i:i+4000] for i in range(0, len(report), 4000)]
    for j, chunk in enumerate(chunks):
        prefix = "ОТЧЁТ ДИАГНОСТИКИ\n\n" if j == 0 else ""
        send_message(ADMIN_CHAT_ID, prefix + chunk)
    sessions.pop(session["uid"], None)


def handle_update(update):
    # Обычное сообщение
    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        user = msg.get("from", {})
        uid = user.get("id")
        text = msg.get("text", "").strip()

        if text == "/start":
            sessions[uid] = {"current": 0, "answers": [], "uid": uid, "username": user.get("username", "")}
            send_message(chat_id,
                "Добро пожаловать!\n\n"
                "Диагностика для собственника\n"
                "«Менеджмент по-Суворовски» — «Пластик Руси»\n\n"
                "43 вопроса о стратегии, команде и вас как лидере.\n"
                "Займёт 15–25 минут.\n\n"
                "Отвечайте честно. Поехали!"
            )
            ask(chat_id, sessions[uid])
            return

        if text == "/status" and uid == ADMIN_CHAT_ID:
            if not sessions:
                send_message(chat_id, "Активных сессий нет.")
            else:
                lines = [f"Активные сессии: {len(sessions)}"]
                for s in sessions.values():
                    lines.append(f"@{s.get('username','—')} — вопрос {s['current']+1}/43")
                send_message(chat_id, "\n".join(lines))
            return

        if uid not in sessions:
            send_message(chat_id, "Введите /start чтобы начать диагностику.")
            return

        session = sessions[uid]
        if not text:
            return

        session["answers"].append(text)
        session["current"] += 1

        if session["current"] >= len(QUESTIONS):
            finish(chat_id, session)
        else:
            ask(chat_id, session)

    # Нажатие кнопки
    elif "callback_query" in update:
        cb = update["callback_query"]
        uid = cb["from"]["id"]
        chat_id = cb["message"]["chat"]["id"]
        msg_id = cb["message"]["message_id"]
        data = cb.get("data", "")
        answer_callback(cb["id"])

        if uid not in sessions:
            return

        session = sessions[uid]
        idx = session["current"]
        q = QUESTIONS[idx]

        if data.startswith("s_") and q["t"] == "scale":
            val = data[2:]
            short = q["q"].split("\n")[0]
            edit_message(chat_id, msg_id, f"✓ {short}\n→ {val}/10")
            session["answers"].append(val)
            session["current"] += 1

            if session["current"] >= len(QUESTIONS):
                finish(chat_id, session)
            else:
                ask(chat_id, session)


def main():
    print("Бот запущен ✅")
    offset = None
    while True:
        try:
            params = {"timeout": 30}
            if offset:
                params["offset"] = offset
            url = f"{API}/getUpdates?" + urllib.parse.urlencode(params)
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read())
            if data.get("ok"):
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    try:
                        handle_update(update)
                    except Exception as e:
                        print(f"Error handling update: {e}")
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
