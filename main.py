from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from serial_parse import SerialConnect
from charge_cart_GUI import Ui_MainWindow
import sys
from numpy import random
from workers import Worker_UpdateState, Worker_UpdateBatteryInfo
from datetime import datetime


class MyWindow(Ui_MainWindow, QtWidgets.QWidget):
    def  __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(MainWindow)
        self.graphSetup()
        self.sio = SerialConnect()

        # force to show the main page first
        self.Main.setCurrentIndex(0)
        self.SOC_progressBar.setValue(0)

        # charging state
        self.state = "Charging"
        self.progressVal = 0
        self.setCurrent_input.setText("5")

        # Make sure this is false when not connect
        self.isConnected = True

        # connect all the buttons
        # self.connect_pb.clicked.connect(self.updateData)
        # self.connect_pb.clicked.connect(self.updateBatteryInfo)
        self.connect_pb.clicked.connect(self.connectPort)
        self.setCurrent_pb.clicked.connect(self.adjustCurrent)
        self.startBalancing_pb.clicked.connect(self.startBalancing)
        self.startCharging_pb.clicked.connect(self.chargingStateMachine)

        self.volBoxesList = []
        self.volBoxesList.append(self.box1_odd)
        self.volBoxesList.append(self.box1_even)
        self.volBoxesList.append(self.box2_odd)
        self.volBoxesList.append(self.box2_even)
        self.volBoxesList.append(self.box3_odd)
        self.volBoxesList.append(self.box3_even)
        self.volBoxesList.append(self.box4_odd)
        self.volBoxesList.append(self.box4_even)
        self.volBoxesList.append(self.box5_odd)
        self.volBoxesList.append(self.box5_even)

        self.tempBoxesList = []
        self.tempBoxesList.append(self.B1_odd)
        self.tempBoxesList.append(self.B1_even)
        self.tempBoxesList.append(self.B2_odd)
        self.tempBoxesList.append(self.B2_even)
        self.tempBoxesList.append(self.B3_odd)
        self.tempBoxesList.append(self.B3_even)
        self.tempBoxesList.append(self.B4_odd)
        self.tempBoxesList.append(self.B4_even)
        self.tempBoxesList.append(self.B5_odd)
        self.tempBoxesList.append(self.B5_even)

    def updateData(self):
        # Stop GUI from freezing as program runs
        # https://realpython.com/python-pyqt-qthread

        # ================================================
        # Create QThread and Worker objects
        self.thread1 = QThread()
        self.thread2 = QThread()

        # Create a worker object
        self.battWorker = Worker_UpdateBatteryInfo(self.sio)
        self.stateWorker = Worker_UpdateState(self.sio)

        # Move worker to the thread
        self.battWorker.moveToThread(self.thread1)
        self.stateWorker.moveToThread(self.thread2)

        # Connect signals and slots
        self.thread1.started.connect(self.battWorker.run)
        self.thread2.started.connect(self.stateWorker.run)

        self.battWorker.finished.connect(self.thread1.quit)
        self.battWorker.finished.connect(self.battWorker.deleteLater)
        self.stateWorker.finished.connect(self.thread2.quit)
        self.stateWorker.finished.connect(self.stateWorker.deleteLater)

        # self.worker.progress1.connect(self.updateBatteryInfo)
        self.thread1.finished.connect(self.thread1.deleteLater)
        self.thread2.finished.connect(self.thread2.deleteLater)

        self.battWorker.batteryInfo.connect(self.updateBatteryInfo)
        self.battWorker.log.connect(self.updateLog)

        self.stateWorker.SoCprogress.connect(self.update_SoC)
        self.stateWorker.currentProgress.connect(self.update_Current)
        self.stateWorker.voltProgress.connect(self.update_voltage)

        # Start thread
        self.thread1.start()
        self.thread2.start()


    # all the functions being called
    def adjustCurrent(self):
        self.logging_texbox.appendPlainText("current set")

    def connectPort(self):
        self.logging_texbox.appendPlainText("connecting to STLink...")
        # wait until debug serial connection
        port_isFound = self.sio.port_setup()

        if not port_isFound:
            self.logging_texbox.appendPlainText("port not found :(")
        else:
            self.logging_texbox.appendPlainText("port found :)")
            self.logging_texbox.appendPlainText("STLink connected")
            self.isConnected = True
            # start populating data (workers)
            self.updateData()


    def graphSetup(self):
        self.graphWidget_current.setBackground('w')
        self.graphWidget_current.setLabel('left', 'Ampere')
        self.graphWidget_current.addLegend()

        self.graphWidget_volt.setBackground('w')
        self.graphWidget_volt.setLabel('left', 'Volt')
        self.graphWidget_volt.addLegend()

    # TODO: Add logic (maybe add an option for input)
    def startBalancing(self):
        self.logging_texbox.appendPlainText("start balancing")
        self.sio.balancePack()

    # TODO: See the document charging procedure
    def chargingStateMachine(self):
        def checkResponse(expected, response, state):
            if response == expected:
                self.log(response)
                state = state + 1
            if response == "error":
                self.log("There is some error")
            else:
                self.log(response)

        if self.state == "Pause":
            self.log("Charging...")

            state = 0
            # a. setForceChargeMode
            if state == 0:
                expectedMessage = "Working"
                response = self.sio.setForceChargeMode()
                checkResponse(expectedMessage, response, state)
            # b. canStartCharger
            if state == 1:
                expectedMessage = "Working"
                response = self.sio.canStartCharger()
                checkResponse(expectedMessage, response, state)
            # c. hvToggle
            if state == 2:
                expectedMessage = "Working"
                response = self.sio.canStartCharger()
                checkResponse(expectedMessage, response, state)
            # d. setMaxCharge
            if state == 3:
                expectedMessage = "Working"
                response = self.sio.setMaxCurrent()
                checkResponse(expectedMessage, response, state)
            # e. startCharge
            if state == 4:
                expectedMessage = "Working"
                response = self.sio.startCharging()
                checkResponse(expectedMessage, response, state)
                self.state = "Charging"
                self.startCharging_pb.setLabel("Stop Charging");


            # currentVal = self.setCurrent_input.toPlainText()
            #
            # if currentVal.isnumeric():
            #     currentVal = f"current {currentVal}"
            #     self.sio.startCharging(currentVal)
            #
            #     self.startCharging_pb.setText(self.state)
            # else:
            #     self.log(f"invalid input, current passed is not a number")

        else:
            self.StopChargingStateMachine()

    # TODO: See the document charging procedure
    def StopChargingStateMachine(self):
        def checkResponse(expected, response, state):
            if response == expected:
                self.log(response)
                state = state + 1
            if response == "error":
                self.log("There is some error")
            else:
                self.log(response)

        if self.state == "Charging":
            self.log("Charging...")
            self.state = "Charging"

            state = 0
            # a. StopCharging
            if state == 0:
                expectedMessage = "Working"
                response = self.sio.StopCharging()
                checkResponse(expectedMessage, response, state)
            # b. hvToggle
            if state == 1:
                expectedMessage = "charging done"
                response = self.sio.hvToggle()
                if response == expectedMessage:
                    self.log(response)
                    self.state = "Pulse"
                    self.startCharging_pb.setLabel("Charging");
        else:
                self.log("Not Charging...")




    def updateBatteryInfo(self, batteryInfo):
        Num_Cell_Per_Batch = 7
        Num_Batch = 5
        cells = self.sio.get_battInfo();
        cell_data = cells[0].strip().split("\r\n")
        cellSummary = cells[1]

        if cell_data == "error":
            print("ERROR received from getBattInfo")

        self.update_voltage(100)

        # populate voltage table
        for BoxesIndex in range(Num_Batch):
            for rowIndex in range(0, Num_Cell_Per_Batch):
                even_data = cell_data[(BoxesIndex * Num_Cell_Per_Batch * 2) + (rowIndex * 2)]
                odd_data = cell_data[(BoxesIndex * Num_Cell_Per_Batch * 2) + (rowIndex * 2) + 1]

                volt_even_val = even_data.split("\t")[1]
                volt_odd_val = odd_data.split("\t")[1]

                self.volBoxesList[BoxesIndex * 2].setItem(rowIndex, 0, QtWidgets.QTableWidgetItem(volt_even_val))
                self.volBoxesList[(BoxesIndex * 2) + 1].setItem(rowIndex, 0, QtWidgets.QTableWidgetItem(volt_odd_val))

                temp_even_val = even_data.split("\t")[2]
                temp_odd_val = odd_data.split("\t")[2]

                self.tempBoxesList[BoxesIndex * 2].setItem(rowIndex, 0, QtWidgets.QTableWidgetItem(temp_even_val))
                self.tempBoxesList[(BoxesIndex * 2) + 1].setItem(rowIndex, 0, QtWidgets.QTableWidgetItem(temp_odd_val))


        # Update main page
        self.maxVolt_textbox().setText(cellSummary["MaxVoltage"])
        self.minVolt_textbox().setText(cellSummary["MinTemp"])
        self.maxTemp_textbox().setText(cellSummary["MaxTemp"])
        self.minTemp_textbox().setText(cellSummary["MinTemp"])
        self.packCurrent_textbox().setText(cellSummary["IBUS"])
        self.rawVolt_textbox().setText(cellSummary["PackVoltage"])

        self.logTimeStamp()



    def update_SoC(self, percent):
        self.SOC_progressBar.setValue(percent)
        self.logging_texbox.appendPlainText("updating state of charge")

    def update_Current(self, current):
        self.packCurrent_textbox.setValue(str(current))
        self.graphWidget_current.append(str(current))
        self.logging_texbox.appendPlainText("updating current")

    def update_voltage(self, voltage):
        self.rawVolt_textbox.setText(str(voltage))
        #self.graphWidget_volt.append(str(voltage))
        self.logging_texbox.appendPlainText("updating voltage")

    def updateLog(self, log):
        self.logging_texbox.appendPlainText(log)

    def log(self, message):
        self.logging_texbox.appendPlainText(str(message))

    def logTimeStamp(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.log("Timestamp-" + current_time)




    # Testing only: create a virtual data
    # Also see document/CommandOutput example
    # ---------------------------------------------------
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

        print(virtualdict)
        return virtualdict


    # https://gist.github.com/nz-angel/31890d2c6cb1c9105e677cacc83a1ffd
    # Allows to split a dictionary into chunks of equal size (list).
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
    # ---------------------------------------------------





if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MyWindow()
    MainWindow.show()
    sys.exit(app.exec())




