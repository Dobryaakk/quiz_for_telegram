from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboard.keybord import main_keyboard, button_back, data_name
from aiogram import Dispatcher

from create import quiz


class FSMStates(StatesGroup):
    waiting_for_photo = State()
    waiting_for_poll_text = State()
    waiting_for_options = State()
    waiting_for_correct_option = State()
    waiting_for_poll_time = State()
    option = State()


async def set_poll_time(message: types.Message):
    await message.answer("Введите время в формате HH:MM")
    await FSMStates.waiting_for_poll_time.set()


async def poll_start(message: types.Message):
    await message.answer('Отлично!\nОтправьте фото для викторины', reply_markup=button_back())
    await FSMStates.waiting_for_photo.set()


async def back_with_fsm_welcome(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer("Создание викторины успешно отменено.\nЧто бы создать викторину нажмите на кнопку ниже",
                         reply_markup=main_keyboard())


async def send_photo(message: types.Message, state: FSMContext):
    global idd
    idd = message.photo[-1].file_id
    async with state.proxy() as data:
        data['photo_id'] = message.photo[-1].file_id
    await FSMStates.waiting_for_poll_text.set()
    await message.answer('Отлично!\nТеперь отправь текст для викторины', reply_markup=data_name())


async def send_poll_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['poll_text'] = message.text
    await FSMStates.waiting_for_options.set()
    await message.answer(
        'Хорошо! Теперь отправь варианты ответов для викторины через перенос строки\nПример:\n1\n2\n3\n',
        reply_markup=button_back())


async def send_options(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['options'] = message.text

    await FSMStates.waiting_for_correct_option.set()
    await message.answer('Спасибо! Теперь отправь номер правильного ответа',
                         reply_markup=button_back())


async def send_correct_option(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['correct_option'] = message.text
    await FSMStates.option.set()
    await message.answer('Теперь отправь обяснение', reply_markup=button_back())


async def send_correction_option(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['option'] = message.text
    await message.answer("Викторина создана", reply_markup=main_keyboard())

    quiz.insert_data(
        idd=idd,
        poll_title=data['poll_text'],
        options=data['options'],
        correct_option=data['correct_option'],
        option=data['option'])

    await state.finish()


async def process_poll_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        time = message.text.strip()

        hours, minutes = map(int, time.split(":"))

        quiz.insert_data_time(hours, minutes)

    await message.answer(f"Время отправки установлено на {hours:02}:{minutes:02}")
    await state.finish()


def register_insert_data(dp: Dispatcher):
    dp.register_message_handler(poll_start, text=['Викторины'])
    dp.register_message_handler(set_poll_time, text=['Время отправки'])
    dp.register_message_handler(send_photo, content_types=['photo'], state=FSMStates.waiting_for_photo)
    dp.register_message_handler(send_poll_text, content_types=['text'], state=FSMStates.waiting_for_poll_text)
    dp.register_message_handler(send_options, content_types=['text'], state=FSMStates.waiting_for_options)
    dp.register_message_handler(send_correct_option, content_types=['text'], state=FSMStates.waiting_for_correct_option)
    dp.register_message_handler(send_correction_option, content_types=['text'], state=FSMStates.option)
    dp.register_message_handler(process_poll_time, lambda message: message.text and message.text[0] != ":",
                                state=FSMStates.waiting_for_poll_time)
    dp.register_message_handler(back_with_fsm_welcome, state="*")
