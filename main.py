from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from serial_parse import SerialConnect
from charge_cart_GUI import Ui_MainWindow
import sys
from numpy import random
from time import sleep


# python3 -m PyQt6.uic.pyuic -o testing.py -x untitled.ui
# python3 -m PyQt6.uic.pyuic -o charge_cart_GUI.py -x charge_cart_GUI.ui

# How do I have an SerialConnect object shared across Worker class and myWindow class?
# In Worker: connector = SerialConnect()
# In myWindow: message = self.port.port_setup()
# Global object I guess?

# Can create different workers with different signatures
class Worker(QObject):
    finished = pyqtSignal()
    progress1 = pyqtSignal(int)

    log = pyqtSignal(str)
    batteryInfo = pyqtSignal(list)
    SoCprogress = pyqtSignal(float)
    currentProgress = pyqtSignal(float)
    voltProgress = pyqtSignal(float)

    def __init__(self, connector):
        super(Worker, self).__init__()
        self.connector = connector

    def run(self):
        # update 5 times
        while True:
            self.updateBatteryInfo()
            # self.update_SoC()
            # self.update_Volt()
            # self.update_Current()
            sleep(0.1)


    def updateBatteryInfo(self):
        # connect to the port
        # emit a list of batteries
        # self.batteryInfo.emit([{"battery": 3}])
        self.batteryInfo.emit([{"battery": 3}])


        if self.connector.port_setup() == True:
            self.connector.execute()
            self.batteryInfo.emit(self.connector.get_battInfo())
        
        else:
            self.log.emit("connection failed!")

        self.finished.emit()


    def update_SoC(self):
        # trigger functions and pass in values
        # whenever is passed in emit will be passed in whatever we connect with (update_SoC)
        soc = float(self.connector.getSoC())
        self.SoCprogress.emit(soc)
        self.finished.emit()

    def update_Current(self):
        current = float(self.connector.getCurrent())
        self.currentProgress.emit(current)
        self.finished.emit()

    def update_Volt(self):
        voltage = self.connector.getVoltage()
        self.voltProgress.emit(voltage)
        self.finished.emit()




class MyWindow(Ui_MainWindow, QtWidgets.QWidget):
    def  __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(MainWindow)
        self.graphSetup()


        self.sio = SerialConnect()
        self.sio.port_setup()

        # force to show the main page first
        self.CellTab.setCurrentIndex(0)
        self.SOC_progressBar.setValue(0)

        # charging state
        self.state = "Charging"
        self.progressVal = 0
        self.setCurrent_input.setText("5")

        # Make sure this is false
        self.isConntecd = True

        # connect all the buttons
        self.setCurrent_pb.clicked.connect(self.adjustCurrent)
        # self.connect_pb.clicked.connect(self.updateData)
        self.startBalancing_pb.clicked.connect(self.startBalancing)
        self.startCharging_pb.clicked.connect(self.chargingStateMachine)

        # maybe I should add another button for start?
        self.connect_pb.clicked.connect(self.updateBatteryInfo)


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
        self.connector = SerialConnect()
        self.worker = Worker(self.connector)


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


        self.worker.SoCprogress.connect(self.update_SoC)
        self.worker.currentProgress.connect(self.update_Current)
        self.worker.voltProgress.connect(self.update_voltage)

        # Start thread
        self.thread.start()





    # all the functions being called
    def adjustCurrent(self):
        self.logging_texbox.appendPlainText("current set")

    def connectPort(self):
        self.logging_texbox.appendPlainText("connecting to STLink...")
        # wait until debug serial connection
        message = self.connector.port_setup()


        if message == "Failed":
            self.logging_texbox.appendPlainText(message)
        else:
            self.logging_texbox.appendPlainText(message)
            self.logging_texbox.appendPlainText("STLink connected")
            self.isConntecd = True


    def graphSetup(self):
        self.graphWidget_current.setBackground('w')
        self.graphWidget_current.setLabel('left', 'Ampere')
        self.graphWidget_current.addLegend()

        self.graphWidget_volt.setBackground('w')
        self.graphWidget_volt.setLabel('left', 'Volt')
        self.graphWidget_volt.addLegend()

    # Testing block
    def startBalancing(self):
        self.logging_texbox.appendPlainText("start balancing")
        unsplited_data = self.virtualBatteryInfo_UnSplited()

        splited_data = self.split_BatteryData(unsplited_data, 14)

        correct_formed = self.virtualBatteryInfo_Splited()



    def chargingStateMachine(self):
        if self.state == "Pause":
            self.log("Charging...")
            self.state = "Charging"

            # move this to serial_parse class
            self.sio.sendRequest("forceChargeCommand 1")
            self.log("forceChargeCommand 1")

            canStartCharger_Message = self.sio.sendRequest("canStartCharger")
            self.log(canStartCharger_Message)

            message = self.sio.sendRequest("hvToggle")
            self.log(message)


            currentVal = self.setCurrent_input.toPlainText()

            if currentVal.isnumeric():
                currentVal = f"current {currentVal}"
                self.sio.startCharging(currentVal)

                self.startCharging_pb.setText(self.state)
            else:
                self.log(f"invalid input, current passed is not a number")

        else:
            self.log("already charging")




    def StopChargingStateMachine(self):
        if self.state == "charging":
            self.log("Stop Charging...")
            self.state = "Pause"
            message = self.sio.StopCharging()

            if message == "charging done":
                self.sio.sendRequest("hvToggle")

            self.startCharging_pb.setText(self.state)

        else:
            self.log("not charging")





    # Testing: only for updating
    def virtualBatteryInfo_Splited(self):
        virtual70Cell = []

        for batch in range(0, 5):
            virtualdict = {}
            for cell in range(1,15):
                virtualdict[f"cell_{14 * batch + cell}"] = {"voltage": random.randint(100) , "temp": random.randint(100)}

            virtual70Cell.append(virtualdict)


        # print(virtual70Cell)
        return virtual70Cell


    def virtualBatteryInfo_UnSplited(self):
        virtualdict = {}
        for cell in range(1, 71):
            virtualdict[f"cell_{cell}"] = {"voltage": random.randint(100) , "temp": random.randint(100)}

        # print(virtualdict)
        return virtualdict


    # https://gist.github.com/nz-angel/31890d2c6cb1c9105e677cacc83a1ffd
    def split_BatteryData(self, input_dict, chunk_size=14):
        res = []
        new_dict = {}
        for k, v in input_dict.items():
            if len(new_dict) < chunk_size:
                new_dict[k] = v
            else:
                res.append(new_dict)
                new_dict = {k: v}
        res.append(new_dict)
        return res


    def getMeanMaxMinOfVoltage(self, batteryInfo):
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
            if singleVol > maxVol:
                maxVol = singleVol
            if singleVol < minVol:
                minVol = singleVol

            if singleTemp > maxTemp:
                maxTemp = singleTemp
            if singleTemp < minTemp:
                minTemp = singleTemp




        mean = totalVoltage/70

        self.maxVolt_textbox.setText(str(maxVol))
        self.minVolt_textbox.setText(str(minVol))
        self.maxTemp_textbox.setText(str(maxTemp))
        self.minTemp_textbox.setText(str(minTemp))
        self.rawVolt_textbox.setText(str(mean))




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
        Num_Cell_Per_Batch = 7
        Num_Batch = 5
        cellIndex = 1
        # virtual70Cells = self.virtualBatteryInfo_Splited()

        virtual70Cells = self.sio.get_battInfo()

        cell_data = virtual70Cells.strip().split("\r\n")

        if virtual70Cells == "error":
            print("ERROR received from getBattInfo")

        # print(virtual70Cells)
        self.update_voltage(100)

        for BoxesIndex in range(Num_Batch):
            for rowIndex in range(0, Num_Cell_Per_Batch):
                even_data = cell_data[ (BoxesIndex * Num_Cell_Per_Batch * 2) + (rowIndex * 2) ]
                odd_data = cell_data[ (BoxesIndex * Num_Cell_Per_Batch * 2) + (rowIndex * 2) + 1 ]

                even_val = even_data.split("\t")[1]
                odd_val = odd_data.split("\t")[1]

                self.BoxesList[BoxesIndex * 2].setItem(rowIndex, 0, QtWidgets.QTableWidgetItem(even_val))
                self.BoxesList[(BoxesIndex * 2) + 1].setItem(rowIndex, 0, QtWidgets.QTableWidgetItem(odd_val))

        # iterate through 10 tables (5 pairs)
        '''for BoxesIndex in range(0,Num_Batch*2,2):
            curCellBatch = virtual70Cells[batch_Index]

            print(f"curCellBatch = '{curCellBatch}'")

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
            cellIndex+=1'''


    def update_SoC(self, percent):
        self.SOC_progressBar.setValue(percent)
        self.logging_texbox.appendPlainText("updating state of charge")

    def update_Current(self, current):
        self.packCurrent_textbox.setValue(str(current))
        self.graphWidget_current.append(random.randint(100))
        self.logging_texbox.appendPlainText("updating current")


    def update_voltage(self, voltage):
        # self.graphWidget_volt.append(random.randint(100))
        self.logging_texbox.appendPlainText("updating voltage")

    def update_V_Graph(self):
        # self.graphWidget_volt.append(random.randint(0,100))
        pass

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




