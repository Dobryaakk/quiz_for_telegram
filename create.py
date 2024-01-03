from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN

from database.config_db import host, user, password, db_name
from database.db import Quiz

quiz = Quiz(host, user, password, db_name)
storage = MemoryStorage()


bot = Bot(TOKEN)
dp = Dispatcher(bot=bot, storage=storage)
