from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config
from db import BotDB

from apscheduler.schedulers.asyncio import AsyncIOScheduler
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

bot = Bot(token=config.token, parse_mode='HTML')
dp = Dispatcher(bot, storage=MemoryStorage())
DB = BotDB('accountant.db')

all_list = None
ban_users_list = None

