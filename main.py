from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow
# import serial_parse_test as data_parsing
from testing1 import Ui_MainWindow
import sys


# python3 -m PyQt6.uic.pyuic -o testing.py -x untitled.ui
# python3 -m PyQt6.uic.pyuic -o cart_testing.py -x untitled.ui


class MyWindow(Ui_MainWindow, QtWidgets.QWidget):
    def  __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(MainWindow)
        # force to show the main page first
        self.CellTab.setCurrentIndex(0)

        # charging state
        self.state = "Pause"






        # connect all the buttons
        self.setCurrent_pb.clicked.connect(self.adjustCurrent)
        self.connect_pb.clicked.connect(self.connectPort)
        self.startBalancing_pb.clicked.connect(self.startBalancing)
        self.startCharging_pb.clicked.connect(self.Charging)



        # self.timer = QtCore.QTimer()
        # self.timer.setInterval(10)
        # self.timer.timeout.connect(self.update)
        # self.timer.start()
        # self.update()
        # self.setCurrent_input.repaint()


    def paintEvent(self, event):
        self.setCurrent_input.setText("This is working")
        print(self.setCurrent_input.toPlainText())

    def update(self):
        self.repaint()


    # all the functions being called
    def adjustCurrent(self):
        self.logging_texbox.appendPlainText("current set")

    def connectPort(self):
        self.logging_texbox.appendPlainText("connecting to STLink...")


        # wait until debug serial connection
        ''' 
        message = data_parsing.port_setup()
        if message == "Failed":
            self.logging_texbox.appendPlainText(message)
        else:
            self.logging_texbox.appendPlainText(message)
            self.logging_texbox.appendPlainText("STLink connected")
            
        '''

    def startBalancing(self):
        self.logging_texbox.appendPlainText("start balancing")

    def Charging(self):
        if self.state == "Pause":
            self.logging_texbox.appendPlainText("Charging...")
            self.state = "Charging"
        else:
            self.logging_texbox.appendPlainText("Stop Charging...")
            self.state = "Pause"

        self.startCharging_pb.setText(self.state)






    # def update(self):
    #     self.plainTextEdit.adjustSize()





# def window():
#     app = QApplication(sys.argv)
#     win = MyWindow()
#
#     win.show()
#     sys.exit(app.exec())


# virtual data for testing
cell_data = {
    "cell_0": {
        "voltage": 3.6,
        "temp": 25,
    },

    "cell_1": {
        "voltage": 2.6,
        "temp": 100,
    },

    "cell_2": {
        "voltage": 1.3,
        "temp": 75,
    }

}
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MyWindow()
    MainWindow.show()
    sys.exit(app.exec())
