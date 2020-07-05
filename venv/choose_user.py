# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'choose_user.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
from index import MainApp
from normal_user import normal_user

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
import sys
import pyodbc

# 实现 ui和Logic的分离
from appdirs import unicode

from connect_mssql import connect_mssql, close_conn, connect_directly

ui, _ = loadUiType('choose_user.ui')

class Choice(QMainWindow, ui):

    # 定义构造方法
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.handle_buttons()
        self.show()

    def handle_buttons(self):
        self.pushButton.clicked.connect(self.pop_window_1)
        self.pushButton_2.clicked.connect(self.pop_window_2)
        self.pushButton_3.clicked.connect(self.close)

    def pop_window_1(self):
        form1 = QtWidgets.QDialog()
        ui = normal_user()
        ui.setupUi(form1)
        form1.exec_()

    def pop_window_2(self):
        form2 = QtWidgets.QDialog()
        ui = MainApp()
        ui.setupUi(form2)
        form2.exec_()

def main():
    app = QApplication([sys.argv])
    window = Choice()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
