import json
import time
import urllib.request
import urllib.parse
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

# Сессии: ключ — строка uid
sessions = {}
# Защита от дублей: последний обработанный update_id на пользователя
last_update = {}

SESSIONS_FILE = "/tmp/sessions.json"


def save():
    try:
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(sessions, f, ensure_ascii=False)
    except Exception as e:
        print(f"[SAVE ERROR] {e}")


def load():
    global sessions
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            sessions = json.load(f)
        print(f"[LOAD] Загружено сессий: {len(sessions)}")
    except Exception:
        sessions = {}


def api_call(method, data=None):
    url = f"{API}/{method}"
    payload = json.dumps(data or {}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"[API ERROR] {method}: {e}")
        return None


def send(chat_id, text, keyboard=None):
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    api_call("sendMessage", data)


def edit(chat_id, msg_id, text):
    api_call("editMessageText", {"chat_id": chat_id, "message_id": msg_id, "text": text})


def scale_kb():
    return {"inline_keyboard": [
        [{"text": str(i), "callback_data": f"s_{i}"} for i in range(1, 6)],
        [{"text": str(i), "callback_data": f"s_{i}"} for i in range(6, 11)],
    ]}


def ask(chat_id, uid):
    s = sessions[uid]
    idx = s["current"]
    q = QUESTIONS[idx]
    total = len(QUESTIONS)
    prog = int((idx / total) * 10)
    bar = "▓" * prog + "░" * (10 - prog)
    sec = f"[ {q['s']} ]\n\n" if (idx == 0 or QUESTIONS[idx]["s"] != QUESTIONS[idx-1]["s"]) else ""
    text = f"{sec}Вопрос {idx+1} из {total}\n{bar}\n\n{q['q']}"
    print(f"[ASK] uid={uid} q={idx+1} current_answers={len(s['answers'])}")
    if q["t"] == "scale":
        send(chat_id, text, scale_kb())
    else:
        send(chat_id, text)


def format_report(uid):
    s = sessions[uid]
    answers = s["answers"]
    name = answers[0] if answers else "Аноним"
    lines = [
        "ДИАГНОСТИКА — «Пластик Руси»",
        f"Имя: {name}",
        f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        f"Username: @{s.get('username','—')} | ID: {uid}",
        "",
    ]
    cur_sec = ""
    for i, q in enumerate(QUESTIONS):
        if q["s"] != cur_sec:
            cur_sec = q["s"]
            lines.append(f"\n=== {cur_sec.upper()} ===")
        short = q["q"].split("\n")[0]
        ans = answers[i] if i < len(answers) else "—"
        if q["t"] == "scale":
            try:
                sc = int(ans)
                bar = "█" * sc + "░" * (10 - sc)
                lines.append(f"\n{i+1}. {short}\n   [{bar}] {ans}/10")
            except Exception:
                lines.append(f"\n{i+1}. {short}\n   → {ans}")
        else:
            lines.append(f"\n{i+1}. {short}\n   → {ans}")
    return "\n".join(lines)


def finish(chat_id, uid):
    send(chat_id,
        "Диагностика завершена!\n\n"
        "Спасибо за честные ответы.\n"
        "Результаты отправлены консультанту.\n\n"
        "По вопросам: @suvorovez | 8-958-159-08-07 | Артемий"
    )
    report = format_report(uid)
    for j, chunk in enumerate([report[i:i+4000] for i in range(0, len(report), 4000)]):
        send(ADMIN_CHAT_ID, ("ОТЧЁТ ДИАГНОСТИКИ\n\n" if j == 0 else "") + chunk)
    sessions.pop(uid, None)
    save()


def handle_message(msg):
    chat_id = msg["chat"]["id"]
    user = msg.get("from", {})
    uid = str(user.get("id", ""))
    text = msg.get("text", "").strip()
    msg_id = msg.get("message_id", 0)

    # Защита от дублей: игнорируем если уже видели этот message_id
    if last_update.get(uid) == msg_id:
        print(f"[SKIP DUPLICATE] uid={uid} msg_id={msg_id}")
        return
    last_update[uid] = msg_id

    print(f"[MSG] uid={uid} text={repr(text[:50])} msg_id={msg_id}")

    if text == "/start":
        sessions[uid] = {"current": 0, "answers": [], "username": user.get("username", "")}
        save()
        send(chat_id,
            "Добро пожаловать!\n\n"
            "Диагностика для собственника\n"
            "«Менеджмент по-Суворовски» — «Пластик Руси»\n\n"
            "43 вопроса о стратегии, команде и вас как лидере.\n"
            "Займёт 15–25 минут. Поехали!"
        )
        ask(chat_id, uid)
        return

    if text == "/status" and uid == str(ADMIN_CHAT_ID):
        if not sessions:
            send(chat_id, "Активных сессий нет.")
        else:
            lines = [f"Активных сессий: {len(sessions)}"]
            for k, s in sessions.items():
                lines.append(f"@{s.get('username','—')} — вопрос {s['current']+1}/43")
            send(chat_id, "\n".join(lines))
        return

    if uid not in sessions:
        send(chat_id, "Введите /start чтобы начать диагностику.")
        return

    s = sessions[uid]
    idx = s["current"]
    q = QUESTIONS[idx]

    if q["t"] == "scale":
        send(chat_id, "Пожалуйста, выберите оценку кнопкой выше.")
        return

    if not text:
        return

    print(f"[ANSWER] uid={uid} q={idx+1} answer={repr(text[:40])}")
    s["answers"].append(text)
    s["current"] += 1
    save()

    if s["current"] >= len(QUESTIONS):
        finish(chat_id, uid)
    else:
        ask(chat_id, uid)


def handle_callback(cb):
    uid = str(cb["from"]["id"])
    chat_id = cb["message"]["chat"]["id"]
    msg_id = cb["message"]["message_id"]
    data = cb.get("data", "")
    cb_id = cb["id"]

    api_call("answerCallbackQuery", {"callback_query_id": cb_id})

    # Защита от дублей
    cb_key = f"cb_{uid}_{msg_id}"
    if last_update.get(cb_key) == data:
        print(f"[SKIP DUPLICATE CB] uid={uid} data={data}")
        return
    last_update[cb_key] = data

    print(f"[CB] uid={uid} data={data}")

    if uid not in sessions:
        return

    s = sessions[uid]
    idx = s["current"]
    q = QUESTIONS[idx]

    if data.startswith("s_") and q["t"] == "scale":
        val = data[2:]
        short = q["q"].split("\n")[0]
        edit(chat_id, msg_id, f"✓ {short}\n→ {val}/10")
        print(f"[SCALE ANSWER] uid={uid} q={idx+1} val={val}")
        s["answers"].append(val)
        s["current"] += 1
        save()

        if s["current"] >= len(QUESTIONS):
            finish(chat_id, uid)
        else:
            ask(chat_id, uid)


def main():
    load()
    print("Бот запущен ✅")
    offset = None
    while True:
        try:
            params = {"timeout": 30, "allowed_updates": ["message", "callback_query"]}
            if offset:
                params["offset"] = offset
            url = f"{API}/getUpdates?" + urllib.parse.urlencode(params)
            with urllib.request.urlopen(url, timeout=35) as resp:
                data = json.loads(resp.read())
            if data.get("ok"):
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    try:
                        if "message" in update:
                            handle_message(update["message"])
                        elif "callback_query" in update:
                            handle_callback(update["callback_query"])
                    except Exception as e:
                        print(f"[HANDLER ERROR] {e}")
        except Exception as e:
            print(f"[POLL ERROR] {e}")
            time.sleep(3)


if __name__ == "__main__":
    main()
