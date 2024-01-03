from aiogram import executor
from create import dp, bot

from handlers import commands, insert_data, send_quiz
from create import quiz

from apscheduler.schedulers.asyncio import AsyncIOScheduler


def start():
    commands.register_commands(dp)
    insert_data.register_insert_data(dp)


def get_scheduled_time():
    result = quiz.select_time_send_polls()

    if result:
        return result
    else:
        return 11, 35


if __name__ == "__main__":
    start()
    print("<Бот успешно запущен")
    scheduler = AsyncIOScheduler()
    scheduled_time = get_scheduled_time()
    if scheduled_time:
        print(f'Scheduled time: {scheduled_time[0]}:{scheduled_time[1]}')
    else:
        print('Scheduled time not set.')

    scheduler.add_job(
        send_quiz.send_poll,
        trigger="cron",
        hour=scheduled_time[0],
        minute=scheduled_time[1],
        args=(bot,)
    )
    scheduler.start()

    executor.start_polling(dp, skip_updates=True)