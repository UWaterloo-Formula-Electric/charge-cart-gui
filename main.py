from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow
import sys


# python3 -m PyQt6.uic.pyuic -o testing.py -x untitled.ui
# python3 -m PyQt6.uic.pyuic -o cart_testing.py -x untitled.ui

class MyWindow(QMainWindow):
    def  __init__(self):
        super(MyWindow,self).__init__()
        self.setGeometry(200, 200, 300, 300)
        self.setWindowTitle("Tony's Candy Shop")
        self.initUI()

    def initUI(self):
        self.label1 = QtWidgets.QLabel(self)
        # this class is a QMainWindow object, so
        # instead of putting in an QMainWindow object, we just put self
        self.label1.setText("my first label")
        self.label1.move(50, 0)

        b1 = QtWidgets.QPushButton(self)
        b1.setText("click me")
        b1.move(100, 100)
        b1.clicked.connect(self.clicking_event)

    def clicking_event(self):
        self.label1.setText("you have pressed the button")
        self.update()

    def update(self):
        self.label1.adjustSize()



def button_clicked():
    print()

def window():
    app = QApplication(sys.argv)
    win = MyWindow()

    win.show()
    sys.exit(app.exec())


window()