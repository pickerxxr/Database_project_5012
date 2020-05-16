# PyQt5 NBAs数据管理系统 开发
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
import sys


# 实现 ui和Logic的分离
ui, _ = loadUiType('main.ui')

class MainApp(QMainWindow, ui):

    # 定义构造方法
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)




def main():
    app = QApplication([])
    window = MainApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()