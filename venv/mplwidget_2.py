# encoding: utf-8
# Author    : Alan Liu <pickerxxr@gmail.com >
# Datetime  : 2020-7-7
# Product   : ${NBA Management system by Fudan 5012}
# explain   : PyQt5 NBA数据管理系统

from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from matplotlib.figure import Figure


class MplWidget_2(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas_2 = FigureCanvas(Figure())

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas_2)

        self.canvas_2.axes_2 = self.canvas_2.figure.add_subplot(111, polar=False)
        self.setLayout(vertical_layout)
