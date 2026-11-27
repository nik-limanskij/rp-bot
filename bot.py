import asyncio
import os
import random

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("Не задана переменная окружения TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

RP_COMMANDS = {
    "hug": [
        "{actor} нежно обнял(а) {target} 🤗",
        "{actor} приобнял(а) {target} за плечи 🫂",
    ],
    "highfive": [
        "{actor} дал(а) пять {target} ✋",
        "{actor} звонко хлопнул(а) ладонью о ладонь {target} 🖐",
    ],
    "wink": [
        "{actor} подмигнул(а) {target} 😉",
    ],
}


def get_target(message: types.Message) -> str | None:
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.first_name
    return None


@dp.message(Command(*RP_COMMANDS, ignore_case=True))
async def rp_command(message: types.Message, command: CommandObject):
    template = random.choice(RP_COMMANDS[command.command])

    target = get_target(message)
    if not target:
        await message.reply(
            "Ответь на сообщение того, с кем хочешь взаимодействовать!"
        )
        return

    actor = message.from_user.first_name if message.from_user else "Кто-то"
    await message.reply(template.format(actor=actor, target=target))


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
