from aiogram import Bot

from create import quiz
from config import CHAT_ID


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

        await bot.send_photo(CHAT_ID, photo=idd)
        await bot.send_poll(
            CHAT_ID,
            question=poll_title,
            options=[option_1, option_2, option_3, option_4, option_5],
            type='quiz',
            correct_option_id=correct_option,
            is_anonymous=True,
        )

        quiz.delete_polls(poll_data[0], )