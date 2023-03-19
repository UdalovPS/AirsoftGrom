import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from sqlalchemy import *
from sqlalchemy.orm import create_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import ConfigTelebot, ConfigDatabase


Base = declarative_base()
engine = create_engine(f"postgresql+psycopg2://{ConfigDatabase().user}:{ConfigDatabase().password}@127.0.01/{ConfigDatabase().db_name}")
metadata = MetaData(bind=engine)


bot = Bot(token=ConfigTelebot().api_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


def loadSession():
    """"""
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


class RegState(StatesGroup):
    name = State()
    team = State()


class Command(StatesGroup):
    rote = State()
    vzvod = State()
    team = State()
    concrete_team = State()
    text = State()


class DeCommand(StatesGroup):
    deact = State()


class CommandersData(Base):
    __table__ = Table('cloud_commandersmodel', metadata, autoload=True)


class RegData(Base):
    __table__ = Table('cloud_playerregistermodel', metadata, autoload=True)


class MapData(Base):
    __table__ = Table('cloud_informationmodel', metadata, autoload=True)


class PointsData(Base):
    __table__ = Table('cloud_pointsmodel', metadata, autoload=True)


class MainQuestsData(Base):
    __table__ = Table('cloud_sidequestsmodel', metadata, autoload=True)


class RoteQuestsData(Base):
    __table__ = Table('cloud_rotequestsmodel', metadata, autoload=True)


class VzvodQuestsData(Base):
    __table__ = Table('cloud_vzvodquestsmodel', metadata, autoload=True)


class TeamQuestsData(Base):
    __table__ = Table('cloud_teamquestsmodel', metadata, autoload=True)


class PlayersData(Base):
    __table__ = Table('cloud_playersmodel', metadata, autoload=True)


class TeamsData(Base):
    __table__ = Table('cloud_teamsmodel', metadata, autoload=True)


@dp.message_handler(commands=['deact'])
async def deact_command(message: types.Message):
    session = create_session(bind=engine)
    author = session.query(PlayersData).filter(PlayersData.user_id == message.from_user.id).first()
    if author:
        if author.role != 3:
            all_text = "Вы не отдавали приказов"
            side_commands = session.query(MainQuestsData).filter(MainQuestsData.author_id == message.from_user.id, MainQuestsData.status == 1).all()
            rote_commands = session.query(RoteQuestsData).filter(RoteQuestsData.author_id == message.from_user.id, RoteQuestsData.status == 1).all()
            vzvod_commands = session.query(VzvodQuestsData).filter(VzvodQuestsData.author_id == message.from_user.id, VzvodQuestsData.status == 1).all()
            team_commands = session.query(TeamQuestsData).filter(TeamQuestsData.author_id == message.from_user.id, TeamQuestsData.status == 1).all()
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            if side_commands:
                all_text = "Какой приказ отменить?"
                for re in side_commands:
                    keyboard.add(types.KeyboardButton(text=f"{re.text} 0"))
            if rote_commands:
                all_text = "Какой приказ отменить?"
                for re in rote_commands:
                    keyboard.add(types.KeyboardButton(text=f"{re.text} 1"))
            if vzvod_commands:
                all_text = "Какой приказ отменить?"
                for re in vzvod_commands:
                    keyboard.add(types.KeyboardButton(text=f"{re.text} 2"))
            if team_commands:
                all_text = "Какой приказ отменить?"
                for re in team_commands:
                    keyboard.add(types.KeyboardButton(text=f"{re.text} 3"))
            await message.answer(text=all_text, reply_markup=keyboard)
            await DeCommand.deact.set()
        else:
            await message.answer(text="У вас нет полномочий")
    else:
        await message.answer(text="У вас нет полномочий")


@dp.message_handler(state=DeCommand.deact)
async def deact_cmd(message: types.Message, state: FSMContext):
    session = loadSession()
    number = message.text[-1]
    text = message.text[:-2]
    if number == "0":
        data = session.query(MainQuestsData).filter(MainQuestsData.text == text).update({'status': 0})
    if number == "1":
        data = session.query(RoteQuestsData).filter(RoteQuestsData.text == text).update({'status': 0})
    if number == "2":
        data = session.query(VzvodQuestsData).filter(VzvodQuestsData.text == text).update({'status': 0})
    if number == "3":
        data = session.query(TeamQuestsData).filter(TeamQuestsData.text == text).update({'status': 0})
    session.commit()
    await message.answer(text=f"Приказ: <b>{text}</b> отменен", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


@dp.message_handler(commands=['act'])
async def act_command(message: types.Message, state: FSMContext):
    session = create_session(bind=engine)
    data = session.query(PlayersData).filter(PlayersData.user_id == message.from_user.id).first()
    team = session.query(TeamsData).filter(TeamsData.id == data.team_id).first()
    await state.update_data(side=False)
    await state.update_data(rote=team.rote)
    await state.update_data(vzvod=team.vzvod)
    await state.update_data(team=False)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if data:
        if data.role == 3:
            await message.answer('У вас нет полномочий')
        elif data.role == 0:        #Штабной офицер
            button_1 = types.KeyboardButton(text='Всей стороне')
            button_2 = types.KeyboardButton(text='101 Роте')
            button_3 = types.KeyboardButton(text='102 Роте')
            button_4 = types.KeyboardButton(text='103 Роте')
            button_5 = types.KeyboardButton(text='104 Роте')
            button_6 = types.KeyboardButton(text='107 Роте')
            keyboard.add(button_1, button_2, button_3, button_4, button_5, button_6)
            await message.answer(text='Кому хотите отдать приказ?', reply_markup=keyboard)
            await Command.rote.set()
        elif data.role == 1:        #Ротный офицер
            button_1 = types.KeyboardButton(text='Всей роте')
            button_2 = types.KeyboardButton(text='1 Взводу')
            button_3 = types.KeyboardButton(text='2 Взводу')
            button_4 = types.KeyboardButton(text='3 Взводу')
            keyboard.add(button_1, button_2, button_3, button_4)
            await message.answer(text='Кому хотите отдать приказ', reply_markup=keyboard)
            await Command.vzvod.set()
    else:
        await message.answer('У вас нет полномочий')


@dp.message_handler(state=Command.rote)
async def choice_rote(message: types.Message, state: FSMContext):
    if message.text == "Всей стороне":
        await state.update_data(side=True)
        await message.answer('Напишите приказ')         #end team thread
        await Command.text.set()
    elif message.text in ['101 Роте', '102 Роте', '103 Роте', '104 Роте', '107 Роте']:
        await state.update_data(rote=message.text[:3])
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button_1 = types.KeyboardButton(text='Всей роте')
        button_2 = types.KeyboardButton(text='1 Взводу')
        button_3 = types.KeyboardButton(text='2 Взводу')
        button_4 = types.KeyboardButton(text='3 Взводу')
        keyboard.add(button_1, button_2, button_3, button_4)
        await message.answer(text='Кому хотите отдать приказ?', reply_markup=keyboard)
        await Command.vzvod.set()


@dp.message_handler(state=Command.vzvod)
async def choice_vzvod(message: types.Message, state: FSMContext):
    if message.text == "Всей роте":
        await state.update_data(vzvod=False)
        await message.answer('Введите приказ')          #end rote thread
        await Command.text.set()
    elif message.text in ['1 Взводу', '2 Взводу', '3 Взводу']:
        await state.update_data(vzvod=message.text[0])
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button_1 = types.KeyboardButton(text='Всему взводу')
        button_2 = types.KeyboardButton(text='Конкретной команде')
        keyboard.add(button_1, button_2)
        await message.answer(text='Кому хотите отдать приказ?', reply_markup=keyboard)
        await Command.team.set()


@dp.message_handler(state=Command.team)
async def choice_team(message: types.Message, state: FSMContext):
    if message.text == 'Всему взводу':
        await message.answer('Введите приказ')          #end vzvod thread
        await Command.text.set()
    elif message.text == 'Конкретной команде':
        data = await state.get_data()
        vzvod = data['vzvod'][0]
        rote = data['rote']
        session = create_session(bind=engine)
        teams = session.query(TeamsData).filter(TeamsData.rote == int(rote), TeamsData.vzvod == int(vzvod)).all()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for re in teams:
            button = types.KeyboardButton(text=re.name)
            keyboard.add(button)
        await message.answer('Выберите команду', reply_markup=keyboard)
        await Command.concrete_team.set()


@dp.message_handler(state=Command.concrete_team)
async def choice_team(message: types.Message, state: FSMContext):
    session = create_session(bind=engine)
    data = session.query(TeamsData).filter(TeamsData.name == message.text).first()
    await state.update_data(team=data.id)
    await message.answer('Введите приказ')
    await Command.text.set()


@dp.message_handler(state=Command.text)
async def print_command(message: types.Message, state: FSMContext):
    data = await state.get_data()
    do_func = True
    if data['side'] != False and do_func == True:
        await message.answer(f'Приказ: <b>{message.text}</b> Отдан', reply_markup=types.ReplyKeyboardRemove())
        new_command = MainQuestsData(status=1, text=message.text, author_id=message.from_user.id)
        session = loadSession()
        session.add(new_command)
        session.commit()
        await state.finish()
        do_func = False
    elif data['team'] != False and do_func == True:
        session = create_session(bind=engine)
        team_data = session.query(TeamsData).filter(TeamsData.id == data['team']).first()
        await message.answer(f'Приказ: <b>{message.text}</b> команде: <u>{team_data.name}</u> отдан', reply_markup=types.ReplyKeyboardRemove())
        new_command = TeamQuestsData(status=1, text=message.text, author_id=message.from_user.id, team_id=data['team'])
        session = loadSession()
        session.add(new_command)
        session.commit()
        await state.finish()
        do_func = False
    elif data['vzvod'] == False and do_func == True:
        await message.answer(f'Приказ: <b>{message.text}</b> <u>{data["rote"]} Роте</u> отдан', reply_markup=types.ReplyKeyboardRemove())
        new_command = RoteQuestsData(status=1, text=message.text, author_id=message.from_user.id, rota=data['rote'])
        session = loadSession()
        session.add(new_command)
        session.commit()
        await state.finish()
        do_func = False
    if do_func == True:
        await message.answer(f'Приказ: <b>{message.text}</b> <u>{data["vzvod"]} Взводу {data["rote"]} Роты</u> отдан', reply_markup=types.ReplyKeyboardRemove())
        new_command = VzvodQuestsData(status=1, text=message.text, author_id=message.from_user.id, rota=data['rote'], vzvod=data['vzvod'])
        session = loadSession()
        session.add(new_command)
        session.commit()
        await state.finish()


@dp.message_handler(commands=['reg'])
async def user_register(message: types.Message):
    session = create_session(bind=engine)
    data = session.query(RegData).filter(RegData.user_id == message.from_user.id).first()
    if data:
        await message.answer(f"Игрок с данным ID:<b>{message.from_user.id}</b> уже зарегистрирован")
    else:
        await message.answer("Введите свой позывной")
        await RegState.name.set()


@dp.message_handler(state=RegState.name)
async def get_username(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите название команды")
    await RegState.next()


@dp.message_handler(state=RegState.team)
async def get_address(message: types.Message, state: FSMContext):
    data = await state.get_data()
    new_user = RegData(name=data['name'], team=message.text, user_id=message.from_user.id, reg=False)
    session = loadSession()
    session.add(new_user)
    session.commit()
    await message.answer(f"Заявка подана\n"
                         f"Позывной: {data['name']}\n"
                         f"Команда: {message.text}\n"
                         f"ID: {message.from_user.id}")
    await state.finish()


@dp.message_handler(content_types=['text'])
async def main_message(message: types.Message):
    session = create_session(bind=engine)
    data = session.query(PlayersData).filter(PlayersData.user_id == message.from_user.id).first()
    if data:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Информацию по карте \U0001F5FA', callback_data='map'))
        keyboard.add(types.InlineKeyboardButton(text='Оперативная информация \U0001F4F0', callback_data='info'))
        keyboard.add(types.InlineKeyboardButton(text='Основные квесты \U0001F310', callback_data='main_quests'))
        keyboard.add(types.InlineKeyboardButton(text='Ротные задачи \U0001FA96', callback_data='rote_quests'))
        keyboard.add(types.InlineKeyboardButton(text='Задачи взвода \U0001F517', callback_data='vzvod_quests'))
        keyboard.add(types.InlineKeyboardButton(text='Персональные задачи \U00002122', callback_data='team_quests'))
        keyboard.add(types.InlineKeyboardButton(text='Связь \U0001F4DE', callback_data='radio'))
        await message.answer(text='Что хочешь узнать, боец? \U0001F60E', reply_markup=keyboard)
    else:
        await message.answer(text="Вы не зарегистрированы. Обратитесь к командованию стороны за инструкциями")


@dp.callback_query_handler(text='info')
async def select_info(call: types.CallbackQuery):
    session = create_session(bind=engine)
    data = session.query(MapData).filter(MapData.status == 1).all()
    # print(f"[LOGGING: {data}]")
    if data:
        all_text = ""
        for re in data:
            one_text = f"{re.text}\n{'.'*20}\n"
            all_text += one_text
    else:
        all_text = "В данный момент инфомация отсутствует"
    await call.message.delete()
    await call.message.answer(text=all_text)


@dp.callback_query_handler(text='map')
async def select_info_about_map(call: types.CallbackQuery):
    session = create_session(bind=engine)
    data = session.query(PointsData).first()
    # print(f"[LOGGING: {data}]")
    all_text = ""
    all_text += f"<b>Пуск А:</b> {point_descripter(data.mark_1)}\n"
    all_text += f"<b>Пуск Б:</b> {point_descripter(data.mark_2)}\n"
    all_text += f"<b>Пуск В:</b> {point_descripter(data.mark_3)}\n"
    all_text += f"<b>Пуск Г:</b> {point_descripter(data.mark_4)}\n"
    all_text += f"<b>Пуск Я:</b> {point_descripter(data.mark_5)}\n"
    all_text += f"<b>Зенит:</b> {point_descripter(data.mark_6)}\n"
    all_text += f"<b>Ударник:</b> {point_descripter(data.mark_7)}\n"
    all_text += f"<b>Спутник:</b> {point_descripter(data.mark_8)}\n"
    all_text += f"<b>Надир:</b> {point_descripter(data.mark_9)}\n"
    await call.message.delete()
    await call.message.answer(text=all_text)


def point_descripter(number: int) -> str:
    """This function get number of point and return description"""
    if number == 0:
        total = "Нейтральная"
    if number == 1:
        total = "\U0001F7E9 Зеленые"
    if number == 2:
        total = "\U00002B1C Белые"
    if number == 3:
        total = "\U00002694 Идет бой"
    return total


@dp.callback_query_handler(text='main_quests')
async def select_main_quests(call: types.CallbackQuery):
    session = create_session(bind=engine)
    data = session.query(MainQuestsData).filter(MainQuestsData.status == 1).all()
    print(f"[LOGGING: Main quests {data}]")
    if data:
        all_text = ""
        for re in data:
            one_text = f"{re.text}\n{'.'*20}\n"
            all_text += one_text
    else:
        all_text = "В данный момент основные квесты отсутствуют"
    await call.message.delete()
    await call.message.answer(text=all_text)


@dp.callback_query_handler(text='rote_quests')
async def select_rote_quests(call: types.CallbackQuery):
    session = create_session(bind=engine)
    player = session.query(PlayersData).filter(PlayersData.user_id == call.from_user.id).first()
    team = session.query(TeamsData).filter(TeamsData.id == player.team_id).first()
    data = session.query(RoteQuestsData).filter(RoteQuestsData.rota == team.rote, RoteQuestsData.status == 1).all()
    print(f"[LOGGING: Main quests {data}]")
    if data:
        all_text = ""
        for re in data:
            author = session.query(PlayersData).filter(PlayersData.user_id == re.author_id).first().name
            one_text = f"<b>{author}:</b> <u>{re.rota} Рота</u>\n {re.text}\n{'.'*20}\n"
            all_text += one_text
    else:
        all_text = "В данный момент задачи для вашей <b>Роты</b> отсутствуют"
    await call.message.delete()
    await call.message.answer(text=all_text)


@dp.callback_query_handler(text='vzvod_quests')
async def select_vzvod_quests(call: types.CallbackQuery):
    session = create_session(bind=engine)
    player = session.query(PlayersData).filter(PlayersData.user_id == call.from_user.id).first()
    team = session.query(TeamsData).filter(TeamsData.id == player.team_id).first()
    data = session.query(VzvodQuestsData).filter(VzvodQuestsData.rota == team.rote, VzvodQuestsData.vzvod == team.vzvod, VzvodQuestsData.status == 1).all()
    # print(f"[LOGGING: Main quests {data}]")
    if data:
        all_text = ""
        for re in data:
            author = session.query(PlayersData).filter(PlayersData.user_id == re.author_id).first().name
            one_text = f"<b>{author}:</b> <u>{re.rota} Рота {re.vzvod} Взвод</u>\n {re.text}\n{'.'*20}\n"
            all_text += one_text
    else:
        all_text = "В данный момент персональных задач для вашего <b>ВЗВОДА</b> нет"
    await call.message.delete()
    await call.message.answer(text=all_text)


@dp.callback_query_handler(text='team_quests')
async def select_team_quests(call: types.CallbackQuery):
    session = create_session(bind=engine)
    player = session.query(PlayersData).filter(PlayersData.user_id == call.from_user.id).first()
    team = session.query(TeamsData).filter(TeamsData.id == player.team_id).first()
    data = session.query(TeamQuestsData).filter(TeamQuestsData.team_id == team.id, TeamQuestsData.status == 1).all()
    # print(f"[LOGGING: Main quests {data}]")
    if data:
        all_text = ""
        for re in data:
            author = session.query(PlayersData).filter(PlayersData.user_id == re.author_id).first().name
            one_text = f"<b>{author}:</b> <u>{team.name}</u> \n{re.text}\n{'.'*20}\n"
            all_text += one_text
    else:
        all_text = "В данный момент персональных задач для вашей <b>КОМАНДЫ</b> нет"
    await call.message.delete()
    await call.message.answer(text=all_text)


@dp.callback_query_handler(text='radio')
async def select_radio_information(call: types.CallbackQuery):
    session = create_session(bind=engine)
    comm_data = session.query(CommandersData).filter(CommandersData.rote == 0).all()
    all_text = ''
    for re in comm_data:
        all_text += f"<u>{re.name}</u>\nТел:<b>{re.phone}</b>\nЧастота:<b>{re.frequency}</b>\n{'.'*20}\n"
    # # print(f"[LOGGING: {data}]")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='101 РОТА', callback_data='r101'))
    keyboard.add(types.InlineKeyboardButton(text='102 РОТА', callback_data='r102'))
    keyboard.add(types.InlineKeyboardButton(text='103 РОТА', callback_data='r103'))
    keyboard.add(types.InlineKeyboardButton(text='104 РОТА', callback_data='r104'))
    keyboard.add(types.InlineKeyboardButton(text='107 РОТА', callback_data='r107'))
    await call.message.delete()
    await call.message.answer(text=all_text, reply_markup=keyboard)


@dp.callback_query_handler(text=['r101', 'r102', 'r103', 'r104', 'r107'])
async def select_radio_about_one_rote(call: types.CallbackQuery):
    rote = call.data[1:]
    session = create_session(bind=engine)
    teams = session.query(TeamsData).filter(TeamsData.rote == rote).all()
    all_text = f"<b>{rote}</b> РОТА\n"
    com_rote = session.query(CommandersData).filter(CommandersData.rote == rote).order_by(CommandersData.vzvod).all()
    if com_rote:
        for re in com_rote:
            if re.vzvod == 0:
                all_text += f"<u>{re.name}</u>\nТел:<b>{re.phone}</b>\nЧастота:<b>{re.frequency}</b>\n{'.'*20}\n"
            else:
                all_text += f"<b>{re.vzvod}</b> <u>{re.name}</u>\nТел:<b>{re.phone}</b>\nЧастота:<b>{re.frequency}</b>\n{'.'*20}\n"
    if teams:
        keyboard = types.InlineKeyboardMarkup()
        for re in teams:
            keyboard.add(types.InlineKeyboardButton(text=re.name, callback_data=f't{re.id}'))
        await call.message.delete()
        await call.message.answer(text=all_text, reply_markup=keyboard)
    else:
        await call.message.delete()
        await call.message.answer(text='Данные отсутствуют')


@dp.callback_query_handler()
async def select_radio_about_one_team(call: types.CallbackQuery):
    session = create_session(bind=engine)
    team = session.query(TeamsData).filter(TeamsData.id == call.data[1:]).first()
    players = session.query(PlayersData).filter(PlayersData.team_id == call.data[1:]).all()
    all_text = f"Команда: <b>{team.name}</b>\nЧастота: <u>{team.frequency}</u>\n"
    if players:
        for re in players:
            one_text = f"{re.name}: <b>{re.phone}</b>\n{'.'*20}\n"
            all_text += one_text
    await call.message.delete()
    await call.message.answer(text=all_text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
