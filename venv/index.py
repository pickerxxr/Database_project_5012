# PyQt5 NBAs数据管理系统 开发
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
import sys


# 实现 ui和Logic的分离
from connect_mssql import connect_mssql, close_conn

ui, _ = loadUiType('main.ui')


class MainApp(QMainWindow, ui):

    # 定义构造方法
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.handle_ui_change()
        self.handle_buttons()

    # UI 的变化处理
    def handle_ui_change(self):
        self.player_button.clicked.connect(self.open_player_tab)
        self.team_button.clicked.connect(self.open_team_tab)
        self.games_button.clicked.connect(self.open_games_tab)
        self.player_compare_button.clicked.connect(self.open_compare_tab)
        self.heat_map_button.clicked.connect(self.open_heat_tab)
        self.line_button.clicked.connect(self.open_line_tab)

    # 处理所有button的消息和槽的通信
    def handle_buttons(self):
        self.connect_button.clicked.connect(self.add_data_all)

    # 选项卡的联动
    def open_player_tab(self):
        self.tabWidget_allfunc.setCurrentIndex(0)

    def open_team_tab(self):
        self.tabWidget_allfunc.setCurrentIndex(1)

    def open_games_tab(self):
        self.tabWidget_allfunc.setCurrentIndex(2)

    def open_compare_tab(self):
        self.tabWidget_allfunc.setCurrentIndex(3)

    def open_heat_tab(self):
        self.tabWidget_allfunc.setCurrentIndex(4)

    def open_line_tab(self):
        self.tabWidget_allfunc.setCurrentIndex(5)

    # 数据库的连接处理
    # 导入所有数据
    def add_data_all(self):
        user_id = self.username_input.text()
        user_pwd = self.password_input.text()
        conn = connect_mssql(user_id, user_pwd)
        cursor = conn.cursor


def main():
    app = QApplication([])
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
