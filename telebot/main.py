import logging
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime

from config import ConfigTelebot
from postgre_sql_orm import DatabasePSQL
from director import Director


bot = Bot(token=ConfigTelebot().api_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands='reg')
async def reg_msg(message: types.Message):
    """start registration"""
    data = Director(message).start()
    data = Director(message)
    await message.answer(data.choice_answer())


@dp.message_handler(commands='check')
async def reg_msg(message: types.Message):
    """cheak regisntations"""
    data = Director(message).check_registration()
    await message.answer(data)


# @dp.message_handler(content_types=['text'])
# async def reg_msg(message: types.Message):
#     """start registration"""
#     data = Director(message)
#     print('Step ID now:', data.step_id)
#     if data.step_id == 6:
#         keyboard = types.InlineKeyboardMarkup()
#         keyboard.add(types.InlineKeyboardButton(text='Синие \U0001F537', callback_data='blue'))
#         keyboard.add(types.InlineKeyboardButton(text='Желтые \U0001F536', callback_data='yellow'))
#         keyboard.add(types.InlineKeyboardButton(text='Любая', callback_data='all'))
#         await message.answer(text=data.choice_answer(), reply_markup=keyboard)
#     else:
#         await message.answer(data.choice_answer())


@dp.callback_query_handler(text='blue')
async def select_quests_list(call: types.CallbackQuery):
    data = Director(call.message).update_side(2)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.message.answer(data)


@dp.callback_query_handler(text='yellow')
async def select_quests_list(call: types.CallbackQuery):
    data = Director(call.message).update_side(3)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.message.answer(data)


@dp.callback_query_handler(text='all')
async def select_quests_list(call: types.CallbackQuery):
    data = Director(call.message).update_side(1)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.message.answer(data)


@dp.message_handler(commands='вата')
async def test_msg(message: types.Message):
    data = ActQuestsDb().select_quest_list_from_db(side=1)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(data)

@dp.message_handler(commands='мир')
async def test_msg(message: types.Message):
    data = ActQuestsDb().select_quest_list_from_db(side=2)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(data)

@dp.message_handler(commands='test')
async def test_msg(message: types.Message):
    await message.answer('Test message')

@dp.message_handler(content_types=['text'])
async def message_with_buttons(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Активные задания \U0001F4CB', callback_data='quests'))
    keyboard.add(types.InlineKeyboardButton(text='Счет в игре \U0001F4DF', callback_data='score'))
    keyboard.add(types.InlineKeyboardButton(text='Информацию по точкам \U0001F4E1', callback_data='point'))
    keyboard.add(types.InlineKeyboardButton(text='Расписание игры \U0001F55B', callback_data='time'))
    await message.answer(text='Что хочешь узнать, боец? \U0001F60E', reply_markup=keyboard)

@dp.callback_query_handler(text='quests')
async def select_quests_list(call: types.CallbackQuery):
    data = QuestsDb().select_quest_list_from_db()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.message.answer(data)

@dp.callback_query_handler(text='score')
async def select_score_list(call: types.CallbackQuery):
    data = ScoresDb().select_scores_list_from_db()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.message.answer(data)

@dp.callback_query_handler(text='point')
async def select_score_list(call: types.CallbackQuery):
    data = PointDb().select_point_list_from_db()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.message.answer(data)

@dp.callback_query_handler(text='time')
async def select_score_list(call: types.CallbackQuery):
    data = TimeTableDb().select_point_list_from_db()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.message.answer(data)


class QuestsDb(DatabasePSQL):
    def __init__(self):
        super(QuestsDb, self).__init__()
        self.table_name = 'cloud_quests'

    def select_quest_list_from_db(self):
        conditions = f'mark = 1'
        data = self.select_in_table(self.table_name, '*', conditions)
        if data:
            data_for_message = self.formate_data_for_telegram(data)
            return data_for_message
        else:
            return 'Активных заданий нет'

    def formate_data_for_telegram(self, data_list):
        message = ""
        for data in data_list:
            one_quest = f"<b><u>{data[1]}</u></b>\n" \
                        f"Начало:  <em><u>{data[2].strftime('%H:%M')}</u></em>\n" \
                        f"Окончание:  <em><u>{data[3].strftime('%H:%M')}</u></em>\n\n" \
                        f"Для стороны синих:\n" \
                        f"\U0001F537{data[4]}\U0001F537\n\n" \
                        f"Для стороны желтых:\n" \
                        f"\U0001F536{data[5]}\U0001F536\n\n" \
                        f"Награда:\n" \
                        f"<u>{data[6]}</u>\n" \
                        f"{'.'*60}\n"
            message += one_quest
        return message


class ActQuestsDb(DatabasePSQL):
    def __init__(self):
        super(ActQuestsDb, self).__init__()
        self.table_name = 'cloud_actquests'

    def select_quest_list_from_db(self, side):
        conditions = f'mark = 1 AND side = {side}'
        data = self.select_in_table(self.table_name, 'name, text, point', conditions)
        if data:
            data_for_message = self.formate_data_for_telegram(data)
            return data_for_message
        else:
            return 'Активных заданий нет'

    def formate_data_for_telegram(self, data_list):
        message = ""
        for data in data_list:
            one_quest = f"<b><u>{data[1]}</u></b>\n\n" \
                        f"{data[4]}\n\n" \
                        f"Награда:\n" \
                        f"<u>{data[6]}</u>\n"
            message += one_quest
        return message


class ScoresDb(DatabasePSQL):
    def __init__(self):
        super(ScoresDb, self).__init__()
        self.main_name = 'cloud_scores'
        self.sub_table = 'cloud_quests'

    def select_scores_list_from_db(self):
        fields = 'cloud_quests.number, cloud_quests.name, blue_scores, yellow_scores'
        conditions = 'cloud_quests.id = cloud_scores.score_id_id'
        data = self.inner_join_in_table(self.main_name, self.sub_table, fields, conditions)
        if data:
            data_for_message = self.format_data_for_telegram(data)
            return data_for_message
        else:
            return 'В данный момент данных по очкам нет'

    def format_data_for_telegram(self, data_list):
        total_blue = 0
        total_yellow = 0
        message = ""
        for data in data_list:
            one_score = f"Задание №:<b>{data[0]}</b>\n" \
                        f"<u><b>{data[1]}</b></u>\n" \
                        f"Сторона синих: <b><u><em>{data[2]}</em></u></b> |\n| " \
                        f"Сторона желтых: <b><u><em>{data[3]}</em></u></b>\n" \
                        f"{'.'*60}\n"
            message += one_score
            total_blue += data[2]
            total_yellow += data[3]
        total_str = f"Общий счет:\n" \
                    f"Сторона синих: <b><u><em>{total_blue}</em></u></b> |\n| " \
                    f"Сторона желтых: <b><u><em>{total_yellow}</em></u></b>\n" \
                    f"{'.'*60}\n"
        return total_str + message


class PointDb(DatabasePSQL):
    def __init__(self):
        super(PointDb, self).__init__()
        self.table_name = 'cloud_point'

    def select_point_list_from_db(self):
        data = self.select_in_table(self.table_name, '*')
        if data:
            data_for_message = self.format_data_for_telegram(data[0])
            return data_for_message
        else:
            return 'В данный момент данных по захвату точек нет'

    def format_data_for_telegram(self, data_list):
        message = "Данные по точкам:\n"
        n = 1
        for point in data_list[1:]:
            if point == 2:
                text = 'Синие'
            elif point == 3:
                text = 'Желтые'
            else:
                text = 'Нейтральная'
            if n == 6:
                number = 'Шахта'
            elif n == 7:
                number = 'Завод'
            elif n == 8:
                number = 'ГОК'
            else:
                number = n
            one_point = f"Точка - <b>{number}</b>:  <u>{text}</u>\n"
            n += 1
            message += one_point
            if n == 9:
                return message


class TimeTableDb(DatabasePSQL):
    def __init__(self):
        super(TimeTableDb, self).__init__()
        self.table_name = 'cloud_timetable'

    def select_point_list_from_db(self):
        data = self.select_in_table(self.table_name, '*')
        if data:
            data_for_message = self.format_data_for_telegram(data)
            return data_for_message
        else:
            return 'расписания нет'

    def format_data_for_telegram(self, data_list):
        message = ""
        for data in data_list:
            one_score = f"Начало:  <em><u>{data[1].strftime('%H:%M')}</u></em>\n" \
                        f"Окончание:  <em><u>{data[2].strftime('%H:%M')}</u></em>\n\n" \
                        f"{data[3]}\n" \
                        f"{'.'*60}\n"
            message += one_score
        return message

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
