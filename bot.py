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

print("=== BOT v4 ===")

bot = Bot(token=TOKEN)
dp = Dispatcher()

ACTIONS = {
    "hug": {
        "label": "🤗 Предложить обнять",
        "keywords": ["обнять", "обня", "hug"],
        "offer": "{actor} предлагает тебе обнять 🤗",
        "accepted": "🤗 {responder} принял(а) предложение! Обнимашки состоялись",
        "declined": "❌ {responder} отказался(ась) от обнимашек",
    },
    "highfive": {
        "label": "🖐 Предложить дать пять",
        "keywords": ["пять", "пятюню", "highfive"],
        "offer": "{actor} предлагает тебе дать пять 🖐",
        "accepted": "🖐 {responder} дал(а) пять!",
        "declined": "❌ {responder} оставил(а) руку висеть в воздухе",
    },
    "wink": {
        "label": "😉 Подмигнуть",
        "keywords": ["подмиг", "wink"],
        "offer": "{actor} подмигивает тебе 😉",
        "accepted": "😉 {responder} подмигнул(а) в ответ!",
        "declined": "❌ {responder} сделал(а) вид, что не заметил(а)",
    },
}


def action_keyboard(action: str, actor_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="✅ Принять",
            callback_data=f"rp:{action}:yes:{actor_id}",
        ),
        InlineKeyboardButton(
            text="❌ Отказать",
            callback_data=f"rp:{action}:no:{actor_id}",
        ),
    ]])


def find_action(query: str) -> list[str]:
    """Ключи действий, подходящих под текст запроса."""
    if not query.strip():
        return list(ACTIONS)
    q = query.lower().strip()
    return [key for key, item in ACTIONS.items()
            if any(k in q for k in item["keywords"])]


@dp.inline_query()
async def inline_actions(inline_query: InlineQuery):
    actor = inline_query.from_user.first_name
    keys = find_action(inline_query.query)

    results = []
    for action in keys:
        item = ACTIONS[action]
        results.append(
            InlineQueryResultArticle(
                id=f"{action}",
                title=item["label"],
                description="Отправит предложение с кнопками принять/отказать",
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
                description="Напиши: обнять, пять или подмигнуть",
                input_message_content=InputTextMessageContent(
                    message_text="Напиши @имя_бота и слово: обнять, пять или подмигнуть 😉",
                ),
            )
        )

    await inline_query.answer(results, cache_time=1, is_personal=True)


@dp.callback_query(F.data.startswith("rp:"))
async def rp_callback(callback: CallbackQuery):
    _, action, decision, actor_id_str = callback.data.split(":")
    actor_id = int(actor_id_str)

    if callback.from_user.id == actor_id:
        await callback.answer(
            "Нельзя отвечать на собственное предложение 🙂",
            show_alert=True,
        )
        return

    item = ACTIONS[action]
    text = (item["accepted"] if decision == "yes" else item["declined"]).format(
        responder=callback.from_user.first_name,
    )

    # Сообщение отправлено через inline — у него нет обычного chat_id,
    # поэтому редактируем по inline_message_id
    if callback.inline_message_id:
        await bot.edit_message_text(
            inline_message_id=callback.inline_message_id,
            text=text,
        )
    elif callback.message:
        await callback.message.edit_text(text)

    await callback.answer()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Это RP-бот 🎭\n\n"
        "Напиши в поле сообщения @имя_бота — всплывут команды. "
        "Выбери «Предложить обнять» — собеседник получит кнопки "
        "«Принять» и «Отказать»."
    )


@dp.message()
async def fallback(message: Message):
    await message.answer(
        "Работаю через inline: набери @имя_бота в поле сообщения 🙂"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
