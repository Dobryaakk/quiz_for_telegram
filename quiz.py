import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.config_db import host, user, password, db_name
from database.db import Quiz

from config import TOKEN

quiz = Quiz(host, user, password, db_name)
bot = Bot(TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
global_message = None
idd = None

markup_back = types.ReplyKeyboardMarkup(resize_keyboard=True)
butt = types.KeyboardButton(text='Отмена')
markup_back.add(butt)


def currency(pred_value):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Лайк' + (' ✅' if pred_value == 1 else ''), callback_data='pred_one'),
         InlineKeyboardButton(text='Нелайк' + (' ✅' if pred_value == 2 else ''), callback_data='pred_two')]
    ])
    return keyboard


markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
butt = types.KeyboardButton(text='Викторины')
butt2 = types.KeyboardButton(text='Время отправки')
markup.add(butt, butt2)

conn = sqlite3.connect('../polls.db')
cursor = conn.cursor()


class FSMStates(StatesGroup):
    waiting_for_photo = State()
    waiting_for_poll_text = State()
    waiting_for_options = State()
    waiting_for_correct_option = State()
    waiting_for_poll_time = State()
    option = State()


@dp.message_handler(text=['Время отправки'])
async def set_poll_time(message: types.Message):
    await message.answer("Введите время в формате HH:MM")
    await FSMStates.waiting_for_poll_time.set()


@dp.message_handler(lambda message: message.text and message.text[0] != ":", state=FSMStates.waiting_for_poll_time)
async def process_poll_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        time = message.text.strip()

        hours, minutes = map(int, time.split(":"))

        quiz.insert_data_time(hours, minutes)

    await message.answer(f"Время отправки установлено на {hours:02}:{minutes:02}")
    await state.finish()


async def send_poll(bot: Bot):
    poll_data = quiz.select_polls()

    if poll_data:
        idd = poll_data[1]
        poll_title = poll_data[2]
        option_1 = poll_data[3]
        option_2 = poll_data[4]
        option_3 = poll_data[5]
        option_4 = poll_data[6]
        option_5 = poll_data[7]
        correct_option = poll_data[8] - 1
        option_6 = poll_data[9]

        await bot.send_photo(1280899097, photo=idd)
        await bot.send_poll(
            1280899097,
            question=poll_title,
            options=[option_1, option_2, option_3, option_4, option_5],
            type='quiz',
            correct_option_id=correct_option,
            is_anonymous=True,
        )

        quiz.delete_polls(poll_data[0], )

    conn.close()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        f'Привет <a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}'
        f'</a>\n\nЯ бот создан для автопостинга в любые чаты/кананлы {message.chat.id}',
        parse_mode='HTML', reply_markup=markup)


@dp.message_handler(text=['Викторины'])
async def poll_start(message: types.Message):
    await message.answer('Отлично!\nОтправьте фото для викторины', reply_markup=markup_back)
    await FSMStates.waiting_for_photo.set()


@dp.message_handler(text=['Отмена'], state="*")
async def back_with_fsm_welcome(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer("Создание викторины успешно отменено.\nЧто бы создать викторину нажмите на кнопку ниже",
                         reply_markup=markup)


@dp.message_handler(content_types=['photo'], state=FSMStates.waiting_for_photo)
async def send_photo(message: types.Message, state: FSMContext):
    global idd
    idd = message.photo[-1].file_id
    async with state.proxy() as data:
        data['photo_id'] = message.photo[-1].file_id
    await FSMStates.waiting_for_poll_text.set()
    await message.answer('Отлично!\nТеперь отправь текст для викторины', reply_markup=markup_back)


@dp.message_handler(content_types=['text'], state=FSMStates.waiting_for_poll_text)
async def send_poll_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['poll_text'] = message.text
    await FSMStates.waiting_for_options.set()
    await message.answer(
        'Хорошо! Теперь отправь варианты ответов для викторины через перенос строки\nПример:\n1\n2\n3\n',
        reply_markup=markup_back)


@dp.message_handler(content_types=['text'], state=FSMStates.waiting_for_options)
async def send_options(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['options'] = message.text

    await FSMStates.waiting_for_correct_option.set()
    await message.answer('Спасибо! Теперь отправь номер правильного ответа', reply_markup=markup_back)


@dp.message_handler(content_types=['text'], state=FSMStates.waiting_for_correct_option)
async def send_correct_option(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['correct_option'] = message.text
    await FSMStates.option.set()
    await message.answer('Теперь отправь обяснение', reply_markup=markup)


@dp.message_handler(content_types=['text'], state=FSMStates.option)
async def send_correct_option(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['option'] = message.text
    await message.answer("Викторина создана")

    quiz.insert_data(
        idd=idd,
        poll_title=data['poll_text'],
        options=data['options'],
        correct_option=data['correct_option'],
        option=data['option'])

    await state.finish()


def get_scheduled_time():
    result = quiz.select_time_send_polls()

    if result:
        return result
    else:
        return 11, 35


if __name__ == "__main__":
    print("<Бот успешно запущен")
    scheduler = AsyncIOScheduler()
    scheduled_time = get_scheduled_time()
    if scheduled_time:
        print(f'Scheduled time: {scheduled_time[0]}:{scheduled_time[1]}')
    else:
        print('Scheduled time not set.')

    scheduler.add_job(
        send_poll,
        trigger="cron",
        hour=scheduled_time[0],
        minute=scheduled_time[1],
        args=(bot,)
    )
    scheduler.start()

    executor.start_polling(dp, skip_updates=True)
