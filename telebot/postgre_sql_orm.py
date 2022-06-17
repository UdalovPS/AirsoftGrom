import psycopg2
from config import ConfigDatabase


class DatabasePSQL:
    def __init__(self):
        self.host = ConfigDatabase().host
        self.user = ConfigDatabase().user
        self.password = ConfigDatabase().password
        self.db_name = ConfigDatabase().db_name

    def connect_to_db(self):
        connection = psycopg2.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.db_name
        )
        connection.autocommit = True
        return connection

    def make_cursor(self, con):
        return con.cursor()

    def decorate_open_commit_close(self, *args):
        def real_decorate(func):
            try:                                        #open database
                con = self.connect_to_db()
                with self.make_cursor(con) as cursor:   #make cursor
                    return func(cursor, *args)          #all func with database
            except Exception as _ex:
                print("[INFO] Error while working with PosgreSQL", _ex)
            finally:
                if con:                                 #close database
                    con.close()
                    print("[INFO] PostgreSQL connection closed")
        return real_decorate

    def show_version(self):
        @self.decorate_open_commit_close
        def func(cursor):
            cursor.execute("SELECT version();")
            data = cursor.fetchone()
            print(f"Server version: {data}")

    def create_table(self, table_name, fields_with_parameters):
        @self.decorate_open_commit_close(table_name, fields_with_parameters)
        def func(cursor, table_name, fields_with_parameters):
            cursor.execute(
                f"""CREATE TABLE IF NOT EXISTS {table_name}(
                    {fields_with_parameters});"""
            )
            print(f"[INFO] Table <{table_name}> created successfully")

    def drop_table(self, table_name):
        @self.decorate_open_commit_close(table_name)
        def func(cursor, table_name):
            cursor.execute(
                f"""DROP TABLE IF EXISTS {table_name};"""
            )
            print(f'[INFO] Table <{table_name}> was deleted')

    def insert_data_in_table(self, table_name, fields, data):
        @self.decorate_open_commit_close(table_name, fields, data)
        def func(cursor, table_name, fields, data):
            print(f'INSERT INTO {table_name} ({fields}) VALUES {data};')
            cursor.execute(
                f"""INSERT INTO {table_name} ({fields}) VALUES {data};"""
            )
            print('[INFO] Data was successfully inserted')

    def delete_data_from_table(self, table_name, conditions):
        @self.decorate_open_commit_close(table_name, conditions)
        def func(cursor, table_name, conditions):
            cursor.execute(
                f"""DELETE FROM {table_name} WHERE {conditions};"""
            )
            print(f'[INFO] Data from <{table_name}> was deleted')

    def select_in_table(self, table_name, fields, conditions=None):
        @self.decorate_open_commit_close(table_name, fields, conditions)
        def func(cursor, table_name, fields, conditions):
            if not conditions:                  #if conditions is not exists
                cursor.execute(
                    f"""SELECT {fields} FROM {table_name};"""
                )
            else:                               # if conditions is exist
                cursor.execute(
                    f"""SELECT {fields} FROM {table_name}
                        WHERE {conditions};"""
                )
            data = cursor.fetchall()
            print(f'[INFO] Data <{data}> was selected from <{table_name}>')
            return data
        return func

    def update_fields(self, table_name, fields_value, conditions=None):
        @self.decorate_open_commit_close(table_name, fields_value, conditions)
        def func(cursor, table_name, fields_value, conditions):
            if conditions:
                cursor.execute(
                    f"""UPDATE {table_name} SET {fields_value}
                        WHERE {conditions};"""
                )
                print(f'[INFO] Data <{fields_value}> from <{table_name}> where <{conditions}> was updated ')
            else:
                cursor.execute(
                    f"""UPDATE {table_name} SET {fields_value};"""
                )


    def inner_join_in_table(self, main_table, sub_tables, fields, conditions):
        @self.decorate_open_commit_close(main_table, sub_tables, fields, conditions)
        def func(cursor, main_table, sub_tables, fields, conditions):
            cursor.execute(
                f"""SELECT {fields} FROM {main_table} INNER JOIN {sub_tables}
                    ON {conditions};"""
            )
            data = cursor.fetchall()
            print(f'[INFO] Data <{data}> was join from <{main_table}>, <{sub_tables}>')
            return data
        return func

    def three_table_join_in_table(self, main_table, sub_table_1, sub_table_2,
                                  fields, conditions_1, conditions_2):
        @self.decorate_open_commit_close(main_table, sub_table_1, sub_table_2,
                                         fields, conditions_1, conditions_2)
        def func(cursor, main_table, sub_table_1, sub_table_2, fields,
                 conditions_1, conditions_2):
            cursor.execute(
                f"""SELECT {fields} FROM {main_table} JOIN {sub_table_1}
                    ON {conditions_1} JOIN {sub_table_2} ON {conditions_2};"""
            )
            data = cursor.fetchall()
            print(f'[INFO] Data <{data}> was join from <{main_table}>, <{sub_table_1}>, <{sub_table_2}>')
            return data
        return func

    def common_request_select(self, cmn_request):
        @self.decorate_open_commit_close(cmn_request)
        def func(cursor, cmn_request):
            cursor.execute(
                f"""{cmn_request};"""
            )
            data = cursor.fetchall()
            print(f'[INFO] Data <{data}> was selected>')
            return data
