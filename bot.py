

API_TOKEN = "YOUR TELEGRAM BOT FATHERs TOKEN"
CHAT_ID = "YOUR CAHT ID"  # куда слать авто-отчёты

import os
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message

# --- Твои функции отчётов ---
from server_report import get_server_report
from process_report import get_process_report
from users_report import get_users_report

TAIL_LINES = 10
log_dir = '/home/your_site/your_server/logs/'

filename = datetime.now().strftime("%d.%m.%y") + ".txt"
LOG_FILE = os.path.join(log_dir, filename)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Кнопки ---
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Показать лог", callback_data="show_log")],
        [InlineKeyboardButton(text="📊 Server", callback_data="server")],
        [InlineKeyboardButton(text="⚙️ Processes", callback_data="processes")],
        [InlineKeyboardButton(text="👤 Users", callback_data="users")]
    ]
)

# --- Обработка команды /start ---
@dp.message(F.text == "/start")
async def start_command(message: Message):
    await message.answer(
        "Привет! Я бот для отчётов сервера и процессов. Ниже кнопки для выбора отчёта:",
        reply_markup=keyboard
    )

# --- Асинхронное отслеживание лога ---
async def watch_log():
    try:
        if not os.path.exists(LOG_FILE):
            print("Сегодняшнего файла лога ещё нет:", LOG_FILE)
            return

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            f.seek(0, 2)  # перейти в конец файла

            while True:
                line = f.readline()
                if line:
                    await bot.send_message(
                        chat_id=CHAT_ID,
                        text=line.strip(),
                        reply_markup=keyboard
                    )
                else:
                    await asyncio.sleep(1)

    except Exception as e:
        print("Ошибка при отслеживании лога:", e)

# --- Обработка кнопок ---
@dp.callback_query(F.data == "show_log")
async def show_full_log(callback_query: CallbackQuery):
    try:
        if not os.path.exists(LOG_FILE):
            await callback_query.answer(text="Лог за сегодня отсутствует.", show_alert=True)
            return

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        last_lines = lines[-TAIL_LINES:]
        content = "".join(last_lines)

        for chunk in [content[i:i+4000] for i in range(0, len(content), 4000)]:
            await callback_query.message.answer(chunk, reply_markup=keyboard)

        await callback_query.answer()

    except Exception as e:
        await callback_query.answer(text=f"Ошибка: {e}", show_alert=True)

@dp.callback_query(F.data == "server")
async def server_report_handler(callback_query: CallbackQuery):
    await callback_query.message.answer(get_server_report(), reply_markup=keyboard)
    await callback_query.answer()

@dp.callback_query(F.data == "processes")
async def processes_report_handler(callback_query: CallbackQuery):
    await callback_query.message.answer(get_process_report(), reply_markup=keyboard)
    await callback_query.answer()

@dp.callback_query(F.data == "users")
async def users_report_handler(callback_query: CallbackQuery):
    await callback_query.message.answer(get_users_report(), reply_markup=keyboard)
    await callback_query.answer()

# --- Авто-отчёт каждый час ---
async def hourly_report():
    while True:
        try:
            text = get_server_report() + "\n\n" + get_process_report()
            await bot.send_message(chat_id=CHAT_ID, text=text, reply_markup=keyboard)
        except Exception as e:
            print("Ошибка при авто-отчёте:", e)
        await asyncio.sleep(3600)  # раз в час

# --- Главная функция ---
async def main():
    asyncio.create_task(watch_log())
    asyncio.create_task(hourly_report())
    print("BOT STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
