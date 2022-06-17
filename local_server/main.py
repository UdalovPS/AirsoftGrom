from PyQt5 import QtWidgets, uic
import sys
from widget_text import WidgetText
from PyQt5.QtCore import QTimer
from server import Server
from PyQt5.QtNetwork import *
from postgre_sql_orm import DatabasePSQL
import threading
import requests
import time


LNG = 'eng'


class MainClass(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainClass, self).__init__()
        self.ui = uic.loadUi('main_gui.ui')
        self.text = WidgetText(LNG)
        self.server = Server(self)
        self.server.listen(QHostAddress.Any, 14141)
        self.thread_obj = ThreadSender()
        self.my_thred = threading.Thread(target=self.thread_obj.send_in_web_server)
        self.my_thred.start()

        self.ui.openPort.clicked.connect(lambda: self.start_send_in_server())
        self.ui.closePort.clicked.connect(lambda: self.stop_send_in_server())
        self.ui.reset_1.clicked.connect(lambda: self.clear_point(0))
        self.ui.reset_2.clicked.connect(lambda: self.clear_point(1))
        self.ui.reset_3.clicked.connect(lambda: self.clear_point(2))
        self.ui.reset_4.clicked.connect(lambda: self.clear_point(3))
        self.ui.reset_5.clicked.connect(lambda: self.clear_point(4))
        self.ui.reset_6.clicked.connect(lambda: self.clear_point(5))
        self.ui.reset_7.clicked.connect(lambda: self.clear_point(6))
        self.ui.reset_8.clicked.connect(lambda: self.clear_point(7))
        self.ui.reset_9.clicked.connect(lambda: self.clear_point(8))
        self.ui.reset_10.clicked.connect(lambda: self.clear_point(9))

        self.server.activate.connect(self.activate_mark)

        self.blue_res = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.yellow_res = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.reset_list = [self.ui.reset_1, self.ui.reset_2, self.ui.reset_3,
                           self.ui.reset_4, self.ui.reset_5, self.ui.reset_6,
                           self.ui.reset_7, self.ui.reset_8, self.ui.reset_9,
                           self.ui.reset_10
                           ]
        self.points_list = [self.ui.point_1_label, self.ui.point_2_label,
                            self.ui.point_3_label, self.ui.point_4_label,
                            self.ui.point_5_label, self.ui.point_6_label,
                            self.ui.point_7_label, self.ui.point_8_label,
                            self.ui.point_9_label, self.ui.point_10_label
                           ]
        self.blue_res_list = (self.ui.blue_1, self.ui.blue_2, self.ui.blue_3,
                              self.ui.blue_4, self.ui.blue_5, self.ui.blue_6,
                              self.ui.blue_7, self.ui.blue_8, self.ui.blue_9,
                              self.ui.blue_10
                              )
        self.yellow_res_list = (self.ui.yellow_1, self.ui.yellow_2,
                                self.ui.yellow_3, self.ui.yellow_4,
                                self.ui.yellow_5, self.ui.yellow_6,
                                self.ui.yellow_7, self.ui.yellow_8,
                                self.ui.yellow_9, self.ui.yellow_10
                                )
        self.mark_tuple = (self.ui.mark_1, self.ui.mark_2, self.ui.mark_3,
                           self.ui.mark_4, self.ui.mark_5, self.ui.mark_6,
                           self.ui.mark_7, self.ui.mark_8, self.ui.mark_9,
                           self.ui.mark_10
                           )

        self.sql_table_name = 'pointBlank'
        self.sql_fields = 'p1_blue INTEGER, p1_yellow INTEGER,' \
                          'p2_blue INTEGER, p2_yellow INTEGER,' \
                          'p3_blue INTEGER, p3_yellow INTEGER,' \
                          'p4_blue INTEGER, p4_yellow INTEGER,' \
                          'p5_blue INTEGER, p5_yellow INTEGER'
        self.sql_blue_fields_list = ('p1_blue', 'p2_blue',
                                     'p3_blue', 'p4_blue',
                                     'p5_blue' )

        self.sql_yellow_fields_list = ('p1_yellow', 'p2_yellow',
                                      'p3_yellow', 'p4_yellow',
                                      'p5_yellow')
        self.insert_fields = 'p1_blue, p1_yellow, p2_blue, p2_yellow,' \
                             'p3_blue, p3_yellow, p4_blue, p4_yellow,' \
                             'p5_blue, p5_yellow'

        self.widget_text()

    def make_server(self):
        server = Server(self)
        return server

    def widget_text(self):
        self.ui.setWindowTitle(self.text.title)
        for reset_btn in self.reset_list:
            reset_btn.setText(self.text.reset)
        i = 0
        for point in self.points_list:
            point.setText(self.text.point_names[i])
            i += 1
        self.ui.openPort.setText(self.text.open_port)
        self.ui.closePort.setText(self.text.close_port)

    def start_send_in_server(self):
        self.thread_obj.activate()

    def stop_send_in_server(self):
        self.thread_obj.terminate()

    # def close_port(self):
    #     self.serial.close_port()
    #     # self.myFirstFlow.quit()
    #     # self.subFlow.terminate()
    #     self.subFlow.stop()

    def insert_in_widget_blue(self, index):
        self.blue_res[index] += 1
        self.blue_res_list[index].setText(str(self.blue_res[index]))

    def insert_in_widget_yellow(self, index):
        self.yellow_res[index] += 1
        self.yellow_res_list[index].setText(str(self.yellow_res[index]))

    def activate_mark(self, data):
        index = data // 10 - 1
        print('index:', index)
        key = data % 10
        print('key:', key)
        PointDb().update_point(index, key)
        if key == 0:
            self.mark_tuple[index].setStyleSheet('QLabel {background-color: green;}')
        elif key == 1:
            self.insert_in_widget_blue(index)
            self.mark_tuple[index].setStyleSheet('QLabel {background-color: blue;}')
        elif key == 2:
            self.insert_in_widget_yellow(index)
            self.mark_tuple[index].setStyleSheet('QLabel {background-color: yellow;}')
        QTimer.singleShot(500, lambda i=index: self.deactivate_mark(i))

    def deactivate_mark(self, index):
        self.mark_tuple[index].setStyleSheet('QLabel {background-color: red;}')

    def clear_point(self, index):
        self.blue_res[index] = 0
        self.yellow_res[index] = 0
        self.blue_res_list[index].setText(str(self.blue_res[index]))
        self.yellow_res_list[index].setText(str(self.yellow_res[index]))


    # def make_db(self):
    #     db = SQLHandler()
    #     db.create_table(self.sql_table_name, self.sql_fields)
    #
    # def insert_in_table(self):
    #     db = SQLHandler()
    #     db.insert_in_table(self.sql_table_name, self.insert_fields, '0,0,0,0,0,0,0,0,0,0')
    #
    # def update_sql_table(self, field, data):
    #     db = SQLHandler()
    #     sett = "{0} = {1}".format(field, data)
    #     db.update_fields(self.sql_table_name, sett)


class ThreadSender:
    def __init__(self):
        self._running = True

    def activate(self):
        print('running - True')
        self._running = True

    def terminate(self):
        print('running - False')
        self._running = False

    def send_in_web_server(self):
        while self._running == True:
            print('send in server')
            data = PointDb().select_point_list_from_db()
            string_data = ""
            for i in data:
                string_data += str(i)
            string_data = string_data[1:]
            print(string_data)
            url = requests.get(f'http://212.109.195.150:80/point/{string_data}/')
            time.sleep(5)


class PointDb(DatabasePSQL):
    def __init__(self):
        super(PointDb, self).__init__()
        self.table_name = 'cloud_point'

    def update_point(self, index, key):
        field_value = f"point_{index + 1} = {key + 1}"
        self.update_fields(self.table_name, field_value)

    def select_point_list_from_db(self):
        data = self.select_in_table(self.table_name, '*')
        if data:
            return data[0]
        else:
            return 'В данный момент данных по захвату точек нет'


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    open = MainClass()
    open.ui.show()
    app.exec()
