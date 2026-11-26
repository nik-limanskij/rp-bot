import asyncio
import random

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

import os
...
TOKEN = os.environ["TOKEN"]

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Словарь: название команды -> список вариантов ответа
RP_COMMANDS = {
    "обнять": [
        "{actor} нежно обнял {target} 🤗",
        "{actor} приобнял {target} за плечи 🫂",
    ],
    "дать_пять": [
        "{actor} дал пять {target} ✋",
        "{actor} звонко хлопнул ладонью о ладонь {target} 🖐",
    ],
    "подмигнуть": [
        "{actor} подмигнул {target} 😉",
    ],
}

def get_target(message: types.Message):
    """Определяем, на кого направлено действие."""
    if message.reply_to_message:
        return message.reply_to_message.from_user.first_name
    return None

@dp.message(Command(*RP_COMMANDS))
async def rp_command(message: types.Message):
    command = message.text.lstrip("/").split(" ")[0].lower()

    if command not in RP_COMMANDS:
        return

    target = get_target(message)
    if not target:
        await message.answer(
            "Ответь на сообщение того, с кем хочешь взаимодействовать!"
        )
        return

    actor = message.from_user.first_name
    template = random.choice(RP_COMMANDS[command])
    await message.answer(template.format(actor=actor, target=target))

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
