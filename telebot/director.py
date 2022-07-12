from config import ConfigTelebot
from postgre_sql_orm import DatabasePSQL


class Director:
    def __init__(self, message_obj):
        self.message = message_obj
        self.step_db = StepDB()
        self.person_db = PersonDb()
        self.step_id = self.select_step_id()

    def check_registration(self):
        data = self.person_db.select_reg_data(self.message.chat.id)
        text = ""
        if data:
            for list in data:
                if list[6] == None or list[6] == 1:
                    pay_status = 'не оплачено'
                else:
                    pay_status = 'оплачено'
                if list[5] == 2:
                    side = 'синие'
                elif list[5] == 3:
                    side = 'желтые'
                else:
                    side = 'любая'
                one_person = f"Фамилия: <b>{list[0]}</b>\n" \
                             f"Имя: <b>{list[1]}</b>\n" \
                             f"Отчество: <b>{list[2]}</b>\n" \
                             f"Команда: <b>{list[3]}</b>\n" \
                             f"Город: <b>{list[4]}</b>\n" \
                             f"Сторона: <b>{side}</b>\n" \
                             f"Статус оплаты: <b>{pay_status}</b>\n{'.'*60}\n"
                text += one_person
            return text
        else:
            return "Данные о регистрации отсутствуют"

    def update_side(self, side):
        self.person_db.update_personal_data(self.person_db.select_max_pk(self.message.chat.id),
                                            'side', side)
        self.person_db.update_personal_data(self.person_db.select_max_pk(self.message.chat.id),
                                            'pay_status', 1)
        self.step_db.delete_step_row(self.message.chat.id)
        return "Заявка зарегистрирована"

    def start(self):
        self.step_db.delete_step_row(self.message.chat.id)
        self.step_db.insert_new_dialogs(self.message.chat.id)
        return self.choice_answer()

    def select_step_id(self):
        step_id = self.step_db.select_step_id(self.message.chat.id)
        return step_id

    def choice_answer(self):
        if self.step_id == 0:
            return "Чтобы подать заявку для регистрации на игру напиши /reg\n" \
                   "Чтобы просмотреть данные по поданным заявкам напиши /check"
        elif self.step_id == 1:
            """last name message"""
            self.step_db.update_step_id(self.message.chat.id, 2)
            return "Напишите свою фамилию"
        elif self.step_id == 2:
            """first name message"""
            self.person_db.insert_new_person(self.message.chat.id, self.message.text)
            self.step_db.update_step_id(self.message.chat.id, 3)
            return "Напишите свое имя"
        elif self.step_id == 3:
            """patronymic message"""
            self.step_db.update_step_id(self.message.chat.id, 4)
            self.person_db.update_personal_data(self.person_db.select_max_pk(self.message.chat.id),
                                                'first_name', self.message.text)
            return "Напишите свое отчество"
        elif self.step_id == 4:
            """team answer"""
            self.step_db.update_step_id(self.message.chat.id, 5)
            self.person_db.update_personal_data(self.person_db.select_max_pk(self.message.chat.id),
                                                'patronymic', self.message.text)
            return "Напишите название своей команды"
        elif self.step_id == 5:
            """sity message"""
            self.step_db.update_step_id(self.message.chat.id, 6)
            self.person_db.update_personal_data(self.person_db.select_max_pk(self.message.chat.id),
                                                'team', self.message.text)
            return "Из какого вы города?"
        elif self.step_id == 6:
            """side message"""
            self.person_db.update_personal_data(self.person_db.select_max_pk(self.message.chat.id),
                                                'sity', self.message.text)
            return "Выберите сторону"


class StepDB(DatabasePSQL):
    def __init__(self):
        super(StepDB, self).__init__()
        self.table_name = 'cloud_dialogs'

    def select_step_id(self, chat_id):
        conditions = f"chat_id = {chat_id}"
        data = self.select_in_table(self.table_name, 'step_id', conditions)
        if data:
            return data[0][0]
        else:
            return 0

    def delete_step_row(self, chat_id):
        conditions = f"chat_id = {chat_id}"
        self.delete_data_from_table(self.table_name, conditions)

    def insert_new_dialogs(self, chat_id):
        self.insert_data_in_table(self.table_name, 'step_id, chat_id', f"(1,{chat_id})")

    def update_step_id(self, chat_id, step_id):
        conditions = f"chat_id = {chat_id}"
        field_value = f"step_id = {step_id}"
        self.update_fields(self.table_name, field_value, conditions)


class PersonDb(DatabasePSQL):
    def __init__(self):
        super(PersonDb, self).__init__()
        self.table_name = 'cloud_reg'

    def select_max_pk(self, chat_id):
        conditions = f"chat_id = {chat_id}"
        data = self.select_in_table(self.table_name, "MAX(id)", conditions)
        return data[0][0]

    def insert_new_person(self, chat_id,  text):
        self.insert_data_in_table(self.table_name, 'last_name, chat_id', f"('{text.lower()}', {chat_id})")

    def update_personal_data(self, pk, field, text):
        conditions = f"id = {pk}"
        if type(text) == str:
            field_value = f"{field} = '{text.lower()}'"
        else:
            field_value = f"{field} = '{text}'"
        self.update_fields(self.table_name, field_value, conditions)

    def select_reg_data(self, chat_id):
        conditions = f"chat_id = {chat_id}"
        fields = "last_name, first_name, patronymic, team, sity, side, pay_status"
        data = self.select_in_table(self.table_name, fields, conditions)
        if data:
            return data
        else:
            return None
