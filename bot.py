import asyncio
import os

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

print("=== BOT v8 ===")

bot = Bot(token=TOKEN)
dp = Dispatcher()

BOT_NAME = "@love_fantasies_rp_bot"

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
                description=f"Набери {BOT_NAME} и слово: обнять, поцеловать, погладить, ущипнуть или шлепнуть",
                input_message_content=InputTextMessageContent(
                    message_text=f"Набери {BOT_NAME} и слово из списка — обнять, поцеловать, погладить, ущипнуть, шлепнуть",
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


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Ну-ну, кто здесь хочет немного нежностей? 😏\n\n"
        "Я передаю желания: обнимашки, поцелуи, поглаживания, "
        "щипки и шлепки. Принять или отказаться — решает тот, кому адресовано.\n\n"
        f"Набери {BOT_NAME} в поле сообщения и выбери действие. "
        "Смелее — флирт сам себя не начнёт 💋"
    )


@dp.message()
async def fallback(message: Message):
    await message.answer(
        f"Жду признаний. Набери {BOT_NAME} и слово из списка: "
        "обнять, поцеловать, погладить, ущипнуть или шлепнуть 💕"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
