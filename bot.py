import asyncio
import os
import random

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

print("=== BOT v14 ===")

bot = Bot(token=TOKEN)
dp = Dispatcher()

BOT_NAME = "@love_fantasies_rp_bot"
USERS = []                      # (user_id, first_name)

# ---------- СТАТИСТИКА ----------
STATS = {
    "starts": 0,            # всего нажатий /start
    "actions_menu": 0,      # открытий меню «Все команды»
    "offers_sent": 0,       # отправлено предложений
    "accepted": 0,          # принято
    "declined": 0,          # отклонено
    "luck_used": 0,         # бросков удачи
    "suggest_started": 0,   # нажали «Предложить команду»
    "suggest_sent": 0,      # реально отправили идею
    "suggest_dropped": 0,   # начали писать идею и не отправили (при перезапуске цикл не закрылся)
}
ACTION_COUNTS = {}          # action -> счётчик использований
PENDING_SUGGEST = set()     # кто сейчас в режиме ввода идеи
# --------------------------------

ACTIONS = {
    "hug": {
        "label": "Обнять",
        "keywords": ["обнять", "обня", "hug"],
        "offer": "{actor} хочет тебя обнять",
        "accepted": "{responder} принял(а) обнимашки",
        "declined": "{responder} отказался(ась) от обнимашек",
    },
    "kiss": {
        "label": "Поцеловать",
        "keywords": ["поцелу", "целовать", "kiss", "чмок"],
        "offer": "{actor} целует тебя",
        "accepted": "{responder} ответил(а) на поцелуй",
        "declined": "{responder} увернулся(лась)",
    },
    "pet": {
        "label": "Погладить",
        "keywords": ["поглад", "гладить", "pet"],
        "offer": "{actor} хочет погладить тебя",
        "accepted": "{responder} разрешил(а) себя погладить",
        "declined": "{responder} отвернулся(лась)",
    },
    "pinch": {
        "label": "Ущипнуть",
        "keywords": ["ущип", "щип", "pinch"],
        "offer": "{actor} целится ущипнуть тебя",
        "accepted": "{responder} получил(а) щипок — «ай, больно!»",
        "declined": "{responder} успел(а) увернуться",
    },
    "smack": {
        "label": "Шлепнуть по попке",
        "keywords": ["шлеп", "попк", "smack"],
        "offer": "{actor} замахивается шлепнуть тебя по попке",
        "accepted": "{responder} получил(а) шлепок по попке",
        "declined": "{responder} ловко увернулся(лась)",
    },
    "air_kiss": {
        "label": "Воздушный поцелуй",
        "keywords": ["воздушный", "чмок в воздух", "air_kiss"],
        "offer": "{actor} посылает тебе воздушный поцелуй 🌬️",
        "accepted": "{responder} поймал(а) его — как мило ✨",
        "declined": "❌ {responder} не поймал(а) поцелуй",
    },
    "whisper": {
        "label": "Прошептать на ушко",
        "keywords": ["шёпот", "шептать", "whisper", "на ушко"],
        "offer": "{actor} шепчет тебе на ушко 🤫",
        "accepted": "{responder} прислушался(ась) — и ему/ей понравилось",
        "declined": "❌ {responder} попросил(а) говорить громче",
    },
    "compliment": {
        "label": "Сказать комплимент",
        "keywords": ["комплимент", "ты красивый", "ты милая"],
        "offer": "{actor} говорит тебе комплимент",
        "accepted": "{responder} покраснел(а) — спасибо 💕",
        "declined": "❌ {responder} смутился(ась) и отвернулся(лась)",
    },
    "cuddle": {
        "label": "Прижаться и посидеть",
        "keywords": ["прижаться", "посидеть рядом", "cuddle"],
        "offer": "{actor} предлагает просто прижаться и посидеть рядом",
        "accepted": "🤗 {responder} прижался(ась) — тепло и спокойно",
        "declined": "❌ {responder} пока не готов(а) к такому",
    },
    "tickle": {
        "label": "Пощекотать",
        "keywords": ["щекот", "tickle", "пощекотать"],
        "offer": "{actor} хочет тебя пощекотать 😊",
        "accepted": "😆 {responder} засмеялся(ась) — это весело!",
        "declined": "❌ {responder} увернулся(ась)",
    },
    "dance": {
        "label": "Пригласить на танец",
        "keywords": ["танец", "танцевать", "dance"],
        "offer": "{actor} приглашает тебя на медленный танец",
        "accepted": "💃 {responder} согласился(ась) — вы танцуете",
        "declined": "❌ {responder} отказался(ась), но улыбнулся(ась)",
    },
    "sweet_msg": {
        "label": "Отправить милое сообщение",
        "keywords": ["сообщение", "написать", "sweet_msg"],
        "offer": "{actor} отправляет тебе милое сообщение",
        "accepted": "{responder} прочитал(а) и улыбнулся(ась) 💕",
        "declined": "❌ {responder} отложил(а) телефон",
    },
    "massage": {
        "label": "Сделать массаж",
        "keywords": ["массаж", "массировать"],
        "offer": "{actor} предлагает сделать тебе лёгкий массаж",
        "accepted": "{responder} согласился — как приятно ✨",
        "declined": "❌ {responder} пока не хочет этого",
    },
}

for key in ACTIONS:
    ACTION_COUNTS[key] = 0


def action_keyboard(action: str, actor_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Принять", callback_data=f"rp:{action}:yes:{actor_id}"),
        InlineKeyboardButton(text="❌ Отказаться", callback_data=f"rp:{action}:no:{actor_id}"),
    ]])


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Все команды", callback_data="show_actions")],
        [InlineKeyboardButton(text="🎲 Испытать удачу", callback_data="luck")],
        [InlineKeyboardButton(text="💬 Предложить команду", callback_data="suggest")],
    ])


def actions_menu() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=item["label"], callback_data=f"action:{action}")
        for action, item in ACTIONS.items()
    ]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    rows.append([InlineKeyboardButton(text="↩ В главное меню", callback_data="main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def cancel_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩ Вернуться в меню", callback_data="main")]
    ])


@dp.callback_query(F.data == "show_actions")
async def show_actions(callback: CallbackQuery):
    STATS["actions_menu"] += 1
    await callback.message.edit_text("Выбери действие 💕", reply_markup=actions_menu())
    await callback.answer()


@dp.callback_query(F.data.startswith("action:"))
async def send_action(callback: CallbackQuery):
    action = callback.data.split(":", 1)[1]
    item = ACTIONS.get(action)
    if not item:
        await callback.answer("Что-то пошло не так", show_alert=True)
        return
    STATS["offers_sent"] += 1
    ACTION_COUNTS[action] += 1
    actor = callback.from_user.first_name or "Кто-то"
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=item["offer"].format(actor=actor),
        reply_markup=action_keyboard(action, callback.from_user.id),
    )
    await callback.answer()


@dp.callback_query(F.data == "suggest")
async def suggest_start(callback: CallbackQuery):
    STATS["suggest_started"] += 1
    PENDING_SUGGEST.add(callback.from_user.id)
    await callback.message.edit_text(
        "Напиши свою идею для бота. Для возврата нажми «↩ Вернуться в меню».",
        reply_markup=cancel_menu(),
    )
    await callback.answer()


@dp.callback_query(F.data == "main")
async def to_main(callback: CallbackQuery):
    # Если человек начал писать идею и передумал — считаем обрыв
    if callback.from_user.id in PENDING_SUGGEST:
        PENDING_SUGGEST.discard(callback.from_user.id)
        STATS["suggest_dropped"] += 1
    await callback.message.edit_text(
        "Ну-ну, кто здесь хочет немного нежностей? 😏\n\n"
        "Выбирай кнопку — и вперёд 💋",
        reply_markup=main_menu(),
    )
    await callback.answer()


@dp.inline_query()
async def inline_actions(inline_query: InlineQuery):
    actor = inline_query.from_user.first_name
    q = inline_query.query.lower().strip()

    if not q:
        keys = list(ACTIONS)
    else:
        keys = [k for k, item in ACTIONS.items() if any(kw in q for kw in item["keywords"])]

    results = []
    for action in keys:
        item = ACTIONS[action]
        results.append(
            InlineQueryResultArticle(
                id=action,
                title=item["label"],
                description="Отправит предложение с кнопками",
                input_message_content=InputTextMessageContent(
                    message_text=item["offer"].format(actor=actor),
                ),
                reply_markup=action_keyboard(action, inline_query.from_user.id),
            )
        )

    if not results:
        results.append(
            InlineQueryResultArticle(
                id="hint",
                title="Нет такого действия",
                description="Выбери действие в меню",
                input_message_content=InputTextMessageContent(
                    message_text="Выбери действие в меню 💕",
                ),
            )
        )

    await inline_query.answer(results, cache_time=1, is_personal=True)


@dp.callback_query(F.data.startswith("rp:"))
async def rp_callback(callback: CallbackQuery):
    _, action, decision, actor_id_str = callback.data.split(":")
    actor_id = int(actor_id_str)

    if callback.from_user.id == actor_id:
        await callback.answer("Нельзя отвечать на собственное сообщение", show_alert=True)
        return

    if decision == "yes":
        STATS["accepted"] += 1
    else:
        STATS["declined"] += 1

    item = ACTIONS[action]
    text = (item["accepted"] if decision == "yes" else item["declined"]).format(
        responder=callback.from_user.first_name,
    )

    if callback.inline_message_id:
        await bot.edit_message_text(inline_message_id=callback.inline_message_id, text=text)
    elif callback.message:
        await callback.message.edit_text(text)

    await callback.answer()


@dp.callback_query(F.data == "luck")
async def luck_start(callback: CallbackQuery):
    STATS["luck_used"] += 1
    await callback.message.edit_text(
        "🎲 Испытаем удачу. Выбери действие — и оно улетит случайному человеку.",
        reply_markup=actions_menu(),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("luck:"))
async def luck_send(callback: CallbackQuery):
    action = callback.data.split(":", 1)[1]
    item = ACTIONS.get(action)
    if not item:
        await callback.answer("Неизвестное действие", show_alert=True)
        return

    uid = callback.from_user.id
    fname = callback.from_user.first_name or "Кто-то"

    others = [(u, f) for u, f in USERS if u != uid]
    if not others:
        await callback.answer("Пока не с кем играть. Пусть кто-нибудь ещё нажмёт /start 😊", show_alert=True)
        return

    target_id, target_name = random.choice(others)

    try:
        await bot.send_message(
            chat_id=target_id,
            text=item["offer"].format(actor=fname),
            reply_markup=action_keyboard(action, uid),
        )
    except Exception:
        await callback.message.edit_text(
            "Не получилось доставить: этот человек, скорее всего, заблокировал бота. Попробуй ещё раз.",
            reply_markup=main_menu(),
        )
        await callback.answer()
        return

    STATS["offers_sent"] += 1
    ACTION_COUNTS[action] += 1

    await callback.message.edit_text(
        f"Твоё «{item['label']}» улетело к {target_name}. Что ответит — узнаем, когда он нажмёт кнопку 💕",
        reply_markup=main_menu(),
    )
    await callback.answer()


@dp.message(Command("id"))
async def cmd_id(message: Message):
    await message.answer(
        f"Твой chat_id: {message.chat.id}\n"
        f"ADMIN_ID сейчас: {ADMIN_ID}"
    )


@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Эта команда только для создателя 🤫")
        return

    top = sorted(ACTION_COUNTS.items(), key=lambda x: x[1], reverse=True)
    top_lines = "\n".join(
        f"• {ACTIONS[k]['label']}: {v}" for k, v in top if v > 0
    ) or "• пока никто ничего не использовал"

    unanswered = STATS["offers_sent"] - STATS["accepted"] - STATS["declined"]

    await message.answer(
        "📊 Статистика бота\n\n"
        f"👥 Уникальных пользователей: {len(USERS)}\n"
        f"🚀 Нажатий /start: {STATS['starts']}\n\n"
        f"💌 Предложений отправлено: {STATS['offers_sent']}\n"
        f"✅ Принято: {STATS['accepted']}\n"
        f"❌ Отклонено: {STATS['declined']}\n"
        f"⌛ Без ответа (обрыв): {unanswered}\n\n"
        f"🎲 Бросков удачи: {STATS['luck_used']}\n\n"
        f"💬 Идей начато: {STATS['suggest_started']} | отправлено: {STATS['suggest_sent']} | брошено: {STATS['suggest_dropped']}\n\n"
        "🔥 Популярность действий:\n"
        f"{top_lines}"
    )


@dp.message(CommandStart())
async def cmd_start(message: Message):
    uid = message.from_user.id
    fname = message.from_user.first_name or "Пользователь"
    STATS["starts"] += 1
    if uid not in [u for u, _ in USERS]:
        USERS.append((uid, fname))

    await message.answer(
        "Ну-ну, кто здесь хочет немного нежностей? 😏\n\n"
        "Выбирай кнопку — и флирт начнётся 💋",
        reply_markup=main_menu(),
    )


@dp.message()
async def handle_message(message: Message):
    if message.from_user.id in PENDING_SUGGEST:
        PENDING_SUGGEST.discard(message.from_user.id)
        if ADMIN_ID:
            try:
                username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"💡 Предложение от {username} (ID: {message.from_user.id}):\n\n{message.text}",
                )
                STATS["suggest_sent"] += 1
                await message.answer("Спасибо, идея ушла создателю ✨", reply_markup=main_menu())
            except Exception:
                await message.answer("Не получилось переслать. Проверь ADMIN_ID.", reply_markup=main_menu())
        else:
            await message.answer("Сохрани текст: создатель ещё не настроен.", reply_markup=main_menu())
        return

    await message.answer("Нажми /start, чтобы начать.", reply_markup=main_menu())


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
