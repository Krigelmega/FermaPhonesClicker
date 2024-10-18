import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InputFile
import sqlite3
import datetime

from data.userstates import UserStates

db_path = "C:/bd/games.db"

async def startmain():
    bot = Bot('7164809029:AAHiy9eC_6zwdvV8nMenUt3rDIxRhiQbhxA')
    storage = MemoryStorage()
    await bot.delete_webhook(drop_pending_updates=True)
    dp = Dispatcher(bot, storage=storage)
    Message = types.Message

    def fetch_all_data(table_name):
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            return cursor.fetchall()

    def fetch_all_data_and_min_hour_to_claim_session(table_name):
        data = []
        min_hour_to_claim = None
        min_session_name = None

        while data == []:
            try:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()

                    # Получаем все данные из таблицы
                    cursor.execute(f"SELECT * FROM {table_name}")
                    data = cursor.fetchall()

                    if data:
                        # Получаем строку с минимальным значением hour_to_claim
                        cursor.execute(
                            f"SELECT session_name, hour_to_claim FROM {table_name} ORDER BY hour_to_claim ASC LIMIT 1")
                        min_row = cursor.fetchone()
                        min_session_name = min_row[0]
                        min_hour_to_claim = min_row[1]

                    return data, min_session_name, min_hour_to_claim
            except sqlite3.Error as e:
                print(f"Ошибка при работе с базой данных: {e}")
                continue

    @dp.message_handler(commands=['start'])
    async def start(message: types.Message, state: FSMContext):
        # Инициализация данных
        await state.update_data(
            all_hamster_balance=0,
            avg_hamster_profit=0,
            all_hamster_profit=0,
            all_memefi_balance=0,
            avg_memefi_boss_health=0,
            all_yescoin_balance=0,
            avb_yescoin_balance=0,
            all_pocketfi_balance=0,
            avb_pocketfi_balance=0,
            all_blum_balance=0,
            freeze_blum_balance=0,
            blum_min_time=0
        )

        await send_info(message, state)
        await UserStates.sdf.set()

    async def send_info(message: types.Message, state: FSMContext):
        data = await state.get_data()
        all_hamster_balance = int(str(data['all_hamster_balance']).replace(',', ''))
        avg_hamster_profit = int(str(data['avg_hamster_profit']).replace(',', ''))
        all_hamster_profit = int(str(data['all_hamster_profit']).replace(',', ''))
        all_memefi_balance = int(str(data['all_memefi_balance']).replace(',', ''))
        avg_memefi_boss_health = int(str(data['avg_memefi_boss_health']).replace(',', ''))
        all_yescoin_balance = int(str(data['all_yescoin_balance']).replace(',', ''))
        avb_yescoin_balance = int(str(data['avb_yescoin_balance']).replace(',', ''))
        all_pocketfi_balance = int(float(str(data['all_pocketfi_balance']).replace(',', '')))
        avb_pocketfi_balance = int(float(str(data['avb_pocketfi_balance']).replace(',', '')))
        all_blum_balance = int(float(str(data['all_blum_balance']).replace(',', '')))
        freeze_blum_balance = float(str(data['freeze_blum_balance']).replace(',', ''))
        blum_min_time = int(float(str(data['blum_min_time']).replace(',', '')))

        # Получение данных из БД
        hamster_data = fetch_all_data('hamster')
        for client in hamster_data:
            all_hamster_balance += int(client[2])
            avg_hamster_profit += int(client[3])
        all_hamster_profit = avg_hamster_profit
        avg_hamster_profit //= len(hamster_data)

        await state.update_data(all_hamster_balance=all_hamster_balance)
        await state.update_data(avg_hamster_profit=avg_hamster_profit)

        all_hamster_balance = f"{all_hamster_balance:,}"
        avg_hamster_profit = f"{avg_hamster_profit:,}"
        all_hamster_profit = f"{all_hamster_profit:,}"

        memefi_data = fetch_all_data('memefi')
        for client in memefi_data:
            all_memefi_balance += int(client[2])
            avg_memefi_boss_health += int(client[3])
        avg_memefi_boss_health //= len(memefi_data)

        await state.update_data(all_memefi_balance=all_memefi_balance)
        await state.update_data(avg_memefi_boss_health=avg_memefi_boss_health)

        all_memefi_balance = f"{all_memefi_balance:,}"
        avg_memefi_boss_health = f"{avg_memefi_boss_health:,}"

        yescoin_data = fetch_all_data('yescoin')
        for client in yescoin_data:
            all_yescoin_balance += int(client[3])
            avb_yescoin_balance += int(client[2])

        await state.update_data(all_yescoin_balance=all_yescoin_balance)
        await state.update_data(avb_yescoin_balance=avb_yescoin_balance)

        all_yescoin_balance = f"{all_yescoin_balance:,}"
        avb_yescoin_balance = f"{avb_yescoin_balance:,}"

        pocketfi_data = fetch_all_data('pocketfi')
        for client in pocketfi_data:
            all_pocketfi_balance += client[2]
            avb_pocketfi_balance += client[3]

        await state.update_data(all_pocketfi_balance=all_pocketfi_balance)
        await state.update_data(avb_pocketfi_balance=avb_pocketfi_balance)

        all_pocketfi_balance = f"{int(all_pocketfi_balance):,}"
        avb_pocketfi_balance = f"{int(avb_pocketfi_balance):,}"

        blum_data, min_session_name, min_hour_to_claim = fetch_all_data_and_min_hour_to_claim_session('blum')
        for client in blum_data:
            all_blum_balance += client[2]
            freeze_blum_balance += client[3]

        await state.update_data(all_blum_balance=all_blum_balance)
        await state.update_data(freeze_blum_balance=freeze_blum_balance)
        await state.update_data(blum_min_time=blum_min_time)

        all_blum_balance = f"{int(all_blum_balance):,}"
        freeze_blum_balance = f"{freeze_blum_balance:,}"
        blum_min_time = str(min_hour_to_claim / 60)[:1]


        button = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button.add(types.KeyboardButton("⭐️ Получить информацию ⭐️"))
        await message.answer(f'🪴 ИНФО ПАНЕЛЬ ФЕРМЫ 🪴\n\n\n'
                             f'| <b>Hamster Kombat</b> |\n\n'
                             f'💰 Всего монет: <b>{all_hamster_balance}</b>\n'
                             f'⚖️ Средний доход: <b>{avg_hamster_profit}</b>\n'
                             f'💸 Общий доход: <b>{all_hamster_profit}</b>\n\n'
                             f'| <b>MemeFI</b> |\n\n'
                             f'💰 Всего монет: <b>{all_memefi_balance}</b>\n'
                             f'⚖️ Средний xp босса: <b>{avg_memefi_boss_health}</b>\n\n'
                             f'| <b>YesCoin</b> |\n\n'
                             f'💰 Всего монет: <b>{all_yescoin_balance}</b>\n'
                             f'❄️ Заморожено монет: <b>{avb_yescoin_balance}</b>\n\n'
                             f'| <b>PocketFI</b> |\n'
                             f'💰 Всего монет: <b>{all_pocketfi_balance}</b>\n'
                             f'❄️ Заморожено монет: <b>{avb_pocketfi_balance}</b>\n\n'
                             f'| <b>Blum</b> |\n'
                             f'💰 Всего монет: <b>{all_blum_balance}</b>\n'
                             f'❄️ Заморожено монет: <b>{freeze_blum_balance}</b>\n'
                             f'⏳ Мин. время до сбора: <b>{blum_min_time}</b> ч.', parse_mode='HTML',
                             reply_markup=button)


        await UserStates.sdf.set()

    @dp.message_handler(state=UserStates.sdf)
    async def sdf_handler(message: types.Message, state: FSMContext):
        old_data = await state.get_data()
        new_data = await state.get_data()

        diff_hamster_balance = int(str(new_data['all_hamster_balance']).replace(',', '')) - int(
            str(old_data['all_hamster_balance']).replace(',', ''))
        diff_avg_hamster_profit = int(str(new_data['avg_hamster_profit']).replace(',', '')) - int(
            str(old_data['avg_hamster_profit']).replace(',', ''))
        diff_all_hamster_profit = int(str(new_data['all_hamster_profit']).replace(',', '')) - int(
            str(old_data['all_hamster_profit']).replace(',', ''))

        diff_memefi_balance = int(str(new_data['all_memefi_balance']).replace(',', '')) - int(
            str(old_data['all_memefi_balance']).replace(',', ''))
        diff_avg_memefi_boss_health = int(str(new_data['avg_memefi_boss_health']).replace(',', '')) - int(
            str(old_data['avg_memefi_boss_health']).replace(',', ''))

        diff_yescoin_balance = int(str(new_data['all_yescoin_balance']).replace(',', '')) - int(
            str(old_data['all_yescoin_balance']).replace(',', ''))
        diff_avb_yescoin_balance = int(str(new_data['avb_yescoin_balance']).replace(',', '')) - int(
            str(old_data['avb_yescoin_balance']).replace(',', ''))

        diff_pocketfi_balance = int(float(str(new_data['all_pocketfi_balance']).replace(',', '')) - float(
            str(old_data['all_pocketfi_balance']).replace(',', '')))
        diff_avb_pocketfi_balance = float(str(new_data['avb_pocketfi_balance']).replace(',', '')) - float(
            str(old_data['avb_pocketfi_balance']).replace(',', ''))

        diff_blum_balance = float(str(new_data['all_blum_balance']).replace(',', '')) - float(
            str( old_data['all_blum_balance']).replace(',', ''))
        diff_freeze_blum_balance = float(str(new_data['freeze_blum_balance']).replace(',', '')) - float(
            str(old_data['freeze_blum_balance']).replace(',', ''))
        diff_blum_min_time = float(new_data['blum_min_time']) - float(old_data['blum_min_time'])

        await message.answer(f'🪴 ИНФО ПАНЕЛЬ ФЕРМЫ 🪴\n\n\n'
                             f'| <b>Hamster Kombat</b> |\n\n'
                             f'💰 Всего монет: <b>{new_data["all_hamster_balance"]:,}</b>\n\t\t\tΔ: <b>{diff_hamster_balance:,}</b>\n'
                             f'⚖️ Средний доход: <b>{new_data["avg_hamster_profit"]:,}</b>\n\t\t\tΔ: <b>{diff_avg_hamster_profit:,}</b>\n'
                             f'💸 Общий доход: <b>{new_data["all_hamster_profit"]:,}</b>\n\t\t\tΔ: <b>{diff_all_hamster_profit:,}</b>\n\n'
                             f'| <b>MemeFI</b> |\n\n'
                             f'💰 Всего монет: <b>{new_data["all_memefi_balance"]:,}</b>\n\t\t\tΔ: <b>{diff_memefi_balance:,}</b>\n'
                             f'⚖️ Средний xp босса: <b>{new_data["avg_memefi_boss_health"]:,}</b>\n\t\t\tΔ: <b>{diff_avg_memefi_boss_health:,}</b>\n\n'
                             f'| <b>YesCoin</b> |\n\n'
                             f'💰 Всего монет: <b>{new_data["all_yescoin_balance"]:,}</b>\n\t\t\tΔ: <b>{diff_yescoin_balance:,}</b>\n'
                             f'❄️ Заморожено монет: <b>{new_data["avb_yescoin_balance"]:,}</b>\n\t\t\tΔ: <b>{diff_avb_yescoin_balance:,}</b>\n\n'
                             f'| <b>PocketFI</b> |\n'
                             f'💰 Всего монет: <b>{int(float(new_data["all_pocketfi_balance"])):,}</b>\n\t\t\tΔ: <b>{int(float(diff_pocketfi_balance))}</b>\n'
                             f'❄️ Заморожено монет: <b>{new_data["avb_pocketfi_balance"]:,}</b>\n\t\t\tΔ: <b>{diff_avb_pocketfi_balance}</b>\n\n'
                             f'| <b>Blum</b> |\n'
                             f'💰 Всего монет: <b>{int(new_data["all_blum_balance"]):,}</b>\n\t\t\tΔ: <b>{diff_blum_balance}</b>\n'
                             f'❄️ Заморожено монет: <b>{int(new_data["freeze_blum_balance"]):,}</b>\n\t\t\tΔ: <b>{diff_freeze_blum_balance}</b>\n'
                             f'⏳ Мин. время до сбора: <b>{new_data["blum_min_time"]}</b> ч.\n\t\t\tΔ: <b>{diff_blum_min_time}</b>',
                             parse_mode='HTML')


    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(startmain())