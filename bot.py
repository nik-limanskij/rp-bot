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

print("=== BOT v16 ===")

bot = Bot(token=TOKEN)
dp = Dispatcher()

BOT_NAME = "@love_fantasies_rp_bot"
USERS = []
INVITED_BY = {}
REFERRALS = {}

STATS = {
    "starts": 0,
    "actions_menu": 0,
    "offers_sent": 0,
    "accepted": 0,
    "declined": 0,
    "luck_used": 0,
    "suggest_started": 0,
    "suggest_sent": 0,
    "suggest_dropped": 0,
}

ACTION_COUNTS = {}
PENDING_SUGGEST = set()

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
        "offer": "{actor}
