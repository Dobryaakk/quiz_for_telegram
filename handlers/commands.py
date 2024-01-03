from aiogram import types
from create import Dispatcher

from keyboard.keybord import main_keyboard
from create import quiz


async def start(message: types.Message):
    await message.answer(
        f'Привет <a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}'
        f'</a>\n\nЯ бот создан для автопостинга в любые чаты/кананлы',
        parse_mode='HTML', reply_markup=main_keyboard())


async def show_quiz(message: types.Message):
    await message.answer(
        f'На данный момент викторин в базе {quiz.show_quiz()[0]}',
        parse_mode='HTML', reply_markup=main_keyboard())


def register_commands(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start', 'help'])
    dp.register_message_handler(show_quiz, commands=['show_quiz'])
