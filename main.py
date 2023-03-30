from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QObject, QThread, pyqtSignal
import serial_parse_test
from testing1 import Ui_MainWindow
import sys
from numpy import random
from time import sleep


# python3 -m PyQt6.uic.pyuic -o testing.py -x untitled.ui
# python3 -m PyQt6.uic.pyuic -o cart_testing.py -x untitled.ui

class Worker(QObject):
    finished = pyqtSignal()
    progress1 = pyqtSignal(int)

    log = pyqtSignal(str)

    # dict maybe?
    batteryInfo = pyqtSignal(list)

    progress2 = pyqtSignal(int)

    def run(self):
        # update 5 times
        while True:
            self.updateBatteryInfo()
            sleep(5)
            self.update_SoC()


    def updateBatteryInfo(self):
        # connect to the port
        # emit a list of batteries
        self.batteryInfo.emit([{"battery": 3}])

        # connector = serial_parse_test.SerialConnect()
        # if (connector.port_setup() == True):
        #     connector.execute()
        #     self.batteryInfo.emit(connector.get_battInfo())
        #
        # else:
        #     self.log.emit("connection failed!")

        self.finished.emit()


    def update_SoC(self):
        # for i in range(50):
        #     sleep(0.5)

        # trigger functions and pass in values
        # whenever is passed in emit will be passed in whatever we connect with (update_SoC)
        self.progress2.emit(50)
        self.finished.emit()



class MyWindow(Ui_MainWindow, QtWidgets.QWidget):
    def  __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(MainWindow)

        # force to show the main page first
        self.CellTab.setCurrentIndex(0)
        self.SOC_progressBar.setValue(0)

        # charging state
        self.state = "Charging"
        self.progressVal = 0

        # Make sure this is false
        self.isConntecd = True

        # connect all the buttons
        self.setCurrent_pb.clicked.connect(self.adjustCurrent)

        self.connect_pb.clicked.connect(self.updateData)

        self.startBalancing_pb.clicked.connect(self.getMeanMaxMinofVoltage)
        self.startCharging_pb.clicked.connect(self.charging)

        # maybe I should add another button for start?
        # self.connect_pb.clicked.connect(self.updateBatteryInfo())


        self.BoxesList = []
        self.BoxesList.append(self.box1_odd)
        self.BoxesList.append(self.box1_even)
        self.BoxesList.append(self.box2_odd)
        self.BoxesList.append(self.box2_even)
        self.BoxesList.append(self.box3_odd)
        self.BoxesList.append(self.box3_even)
        self.BoxesList.append(self.box4_odd)
        self.BoxesList.append(self.box4_even)
        self.BoxesList.append(self.box5_odd)
        self.BoxesList.append(self.box5_even)

    def updateData(self):
        # Stop GUI from freezing as program runs
        # https://realpython.com/python-pyqt-qthread

        # ================================================
        # Create QThread and Worker objects
        self.thread = QThread()
        # Create a worker object
        self.worker = Worker()

        # Move worker to the thread
        self.worker.moveToThread(self.thread)

        # Connect signals and slots
        self.thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.thread.quit)

        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # self.worker.progress1.connect(self.updateBatteryInfo)
        self.worker.batteryInfo.connect(self.updateBatteryInfo)
        self.worker.log.connect(self.updateLog)


        self.worker.progress2.connect(self.update_SoC)

        # Start thread
        self.thread.start()





    # all the functions being called
    def adjustCurrent(self):
        self.logging_texbox.appendPlainText("current set")

    def connectPort(self):
        self.logging_texbox.appendPlainText("connecting to STLink...")
        # wait until debug serial connection
        # message = data_parsing.port_setup()
        # if message == "Failed":
        #     self.logging_texbox.appendPlainText(message)
        # else:
        #     self.logging_texbox.appendPlainText(message)
        #     self.logging_texbox.appendPlainText("STLink connected")
        #     self.isConntecd = True



    def startBalancing(self):
        self.logging_texbox.appendPlainText("start balancing")

    def charging(self):
        if self.state == "Pause":
            self.logging_texbox.appendPlainText("Charging...")
            self.state = "Charging"
        else:
            self.logging_texbox.appendPlainText("Stop Charging...")
            self.state = "Pause"

        self.startCharging_pb.setText(self.state)


    # Testing: only for updating
    def virtualBatteryInfo_Splited(self):
        virtual70Cell = []

        for batch in range(0, 5):
            virtualdict = {}
            for cell in range(1,15):
                virtualdict[f"cell_{14 * batch + cell}"] = {"voltage": random.randint(100) , "temp": random.randint(100)}

            virtual70Cell.append(virtualdict)


        print(virtual70Cell)
        return virtual70Cell


    def virtualBatteryInfo_UnSplited(self):
        virtualdict = {}
        for cell in range(0, 70):
            virtualdict[f"cell_{cell}"] = {"voltage": random.randint(100) , "temp": random.randint(100)}

        print(virtualdict)
        return virtualdict

    def getMeanMaxMinofVoltage(self, batteryInfo):
        # Testing
        virtual70Cells = self.virtualBatteryInfo_UnSplited()

        totalVoltage = 0
        maxVol = virtual70Cells[f"cell_1"]["voltage"]
        minVol = virtual70Cells[f"cell_1"]["voltage"]
        maxTemp = virtual70Cells[f"cell_1"]["temp"]
        minTemp = virtual70Cells[f"cell_1"]["temp"]

        for i in range(70):
            singleVol = virtual70Cells[f"cell_{i}"]["voltage"]
            singleTemp = virtual70Cells[f"cell_{i}"]["temp"]
            totalVoltage += singleVol
            if(singleVol > maxVol):
                maxVol = singleVol
            if (singleVol < minVol):
                minVol = singleVol

            if(singleTemp > maxTemp):
                maxTemp = singleTemp
            if (singleTemp < minTemp):
                minTemp = singleTemp




        mean = totalVoltage/70

        self.maxVolt_textbox.setText(str(maxVol))
        self.minVolt_textbox.setText(str(minVol))
        self.maxTemp_textbox.setText(str(maxTemp))
        self.minTemp_textbox.setText(str(minTemp))






    def updateBatteryInfo(self, batteryInfo):
        # batteryInfo
        '''
        batteryInfo = [
        {
            "cell_1": {
                "voltage": 36,
                "temp": 25,
            },

            "cell_2": {
                "voltage": 36,
                "temp": 25,
            }
        },

        {
            "cell_3": {
                "voltage": 3.6,
                "temp": 25,
            },

            "cell_4": {
                "voltage": 3.6,
                "temp": 25,
            }
        }
        ]

        '''




        # self.logging_texbox.appendPlainText("updating battery Info")

        batch_Index = 0
        Num_Cell_Per_Batch = 13
        Num_Batch = 5
        cellIndex = 1
        virtual70Cells = self.virtualBatteryInfo_Splited()
        print(virtual70Cells)

        # iterate through 10 tables (5 pairs)
        for BoxesIndex in range(0,Num_Batch*2,2):
            curCellBatch = virtual70Cells[batch_Index]

            self.log(curCellBatch)


            lowerBound = cellIndex
            rowIndex = 0

            print("From", cellIndex)
            print("To", lowerBound+Num_Cell_Per_Batch)
            print("CurrentCell", cellIndex)

            # iterate over 7 cells in a batch / two tables
            for cellIndex in range(cellIndex, lowerBound+Num_Cell_Per_Batch, 2):
                # dictionary
                odd = str(curCellBatch[f"cell_{cellIndex}"]["voltage"])
                even = str(curCellBatch[f"cell_{cellIndex+1}"]["voltage"])

                print(cellIndex)
                self.BoxesList[BoxesIndex].setItem(rowIndex, 0, QtWidgets.QTableWidgetItem(odd))
                self.BoxesList[BoxesIndex+1].setItem(rowIndex, 0, QtWidgets.QTableWidgetItem(even))

                rowIndex+=1

            batch_Index+=1
            cellIndex = lowerBound+Num_Cell_Per_Batch
            cellIndex+=1


    def update_SoC(self, n):
        self.SOC_progressBar.setValue(n)
        self.logging_texbox.appendPlainText("updating state of charge")

    def updateLog(self, log):
        self.logging_texbox.appendPlainText(log)

    def log(self, message):
        self.logging_texbox.appendPlainText(str(message))



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MyWindow()
    MainWindow.show()
    sys.exit(app.exec())




