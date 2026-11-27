import asyncio
import os
import random

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
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
if not TOKEN:
    raise RuntimeError("Переменная окружения TOKEN не задана")

print("=== BOT v12 ===")

bot = Bot(token=TOKEN)
dp = Dispatcher()

BOT_NAME = "@love_fantasies_rp_bot"

# Те, кто нажал /start: список кортежей (user_id, first_name)
USERS = []

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


def action_keyboard(action: str, actor_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Принять", callback_data=f"rp:{action}:yes:{actor_id}"),
        InlineKeyboardButton(text="❌ Отказаться", callback_data=f"rp:{action}:no:{actor_id}"),
    ]])


def actions_menu() -> InlineKeyboardMarkup:
    """Кнопки действий: открывают inline в текущем чате."""
    buttons = [
        InlineKeyboardButton(
            text=item["label"],
            switch_inline_query_current_chat=item["keywords"][0],
        )
        for item in ACTIONS.values()
    ]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def main_menu() -> InlineKeyboardMarkup:
    """Главное меню: действия + кнопка удачи."""
    buttons = [
        InlineKeyboardButton(
            text=item["label"],
            switch_inline_query_current_chat=item["keywords"][0],
        )
        for item in ACTIONS.values()
    ]
    buttons.append(InlineKeyboardButton(text="🎲 Испытать удачу", callback_data="luck"))
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def luck_menu() -> InlineKeyboardMarkup:
    """Выбор действия для броска удачи."""
    buttons = [
        InlineKeyboardButton(text=item["label"], callback_data=f"luck:{action}")
        for action, item in ACTIONS.items()
    ]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def find_action(query: str) -> list[str]:
    if not query.strip():
        return list(ACTIONS)
    q = query.lower().strip()
    return [key for key, item in ACTIONS.items() if any(k in q for k in item["keywords"])]


@dp.inline_query()
async def inline_actions(inline_query: InlineQuery):
    actor = inline_query.from_user.first_name
    keys = find_action(inline_query.query)

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
                description="Выбери действие в меню или набери что-нибудь",
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
    """Шаг 1: показать выбор действия."""
    await callback.message.edit_text(
        "🎲 Испытаем удачу. Выбери действие — и оно улетит случайному человеку из тех, кто запускал бота.",
        reply_markup=luck_menu(),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("luck:"))
async def luck_send(callback: CallbackQuery):
    """Шаг 2: отправить выбранное действие случайному пользователю."""
    action = callback.data.split(":", 1)[1]
    item = ACTIONS.get(action)
    if not item:
        await callback.answer("Неизвестное действие", show_alert=True)
        return

    uid = callback.from_user.id
    fname = callback.from_user.first_name or "Кто-то"

    others = [(u, f) for u, f in USERS if u != uid]
    if not others:
        await callback.answer(
            "Пока не с кем играть: другие пользователи ещё не запускали бота",
            show_alert=True,
        )
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
            "Не получилось доставить сообщение: этот человек давно не общался с ботом. Попробуй ещё раз.",
            reply_markup=main_menu(),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"Твоё «{item['label']}» улетело к {target_name}. Что ответит — узнаем, когда он нажмёт кнопку 💕",
        reply_markup=main_menu(),
    )
    await callback.answer()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    uid = message.from_user.id
    fname = message.from_user.first_name or "Пользователь"
    if uid not in [u for u, _ in USERS]:
        USERS.append((uid, fname))

    await message.answer(
        "Ну-ну, кто здесь хочет немного нежностей? 😏\n\n"
        "Обнимашки, поцелуи, комплименты… Принять или отказаться решает тот, кому адресовано.\n\n"
        "Нажми на кнопку — выбери собеседника — и флирт начнётся. "
        "А если хочется сюрприза — жми «🎲 Испытать удачу» 💋",
        reply_markup=main_menu(),
    )


@dp.message()
async def fallback(message: Message):
    await message.answer(
        "Давай поиграем. Нажми /start и выбери действие в меню 💕",
        reply_markup=main_menu(),
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
