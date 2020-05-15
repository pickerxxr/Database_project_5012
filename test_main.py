import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

from test import *

class mainWin(QMainWindow, Ui_Dialog):
    def __init__(self, parent = None):
        super(mainWin, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.showMessage)

    def showMessage(self):
        self.textEdit.setText("Hello World")
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = mainWin()
    main_win.show()
    sys.exit(app.exec_())


