from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread
from serial_parse import SerialConnect
from charge_cart_GUI import Ui_MainWindow
import sys
from workers import Worker_UpdateBatteryInfo
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
        self.SOC_progressBar.setMaximum(10000)

        # charging state
        self.state = "Charging"
        self.progressVal = 0
        self.setCurrent_input.setText("5")

        # Make sure this is false when not connect
        self.isConnected = False
        self.portSetup()

        # connect all the buttons
        self.connect_pb.clicked.connect(self.connectPort)
        self.setCurrent_pb.clicked.connect(self.adjustCurrent)
        self.startBalancing_pb.clicked.connect(self.startBalancing)
        self.startCharging_pb.clicked.connect(self.chargingStateMachine)
        self.rescan_pb.clicked.connect(self.portSetup)

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

        # Create a worker object
        self.battWorker = Worker_UpdateBatteryInfo(self.sio)

        # Move worker to the thread
        self.battWorker.moveToThread(self.thread1)

        # Connect signals and slots
        self.thread1.started.connect(self.battWorker.run)
        self.battWorker.finished.connect(self.thread1.quit)
        self.battWorker.finished.connect(self.battWorker.deleteLater)
        self.thread1.finished.connect(self.thread1.deleteLater)
        self.battWorker.batteryInfo.connect(self.updateBatteryInfo)
        self.battWorker.log.connect(self.updateLog)

        # Start thread
        self.thread1.start()

    # all the functions being called
    def adjustCurrent(self):
        self.logging_texbox.appendPlainText("current set")

    def portSetup(self):
        # TODO: maybe add an option to find a port again?
        ports = self.sio.port_setup()
        if len(ports) != 0:
            self.portDropDown.clear()
            self.portDropDown.addItems(ports)
        else:
            print("no port found")

        if self.isConnected:
            self.rescan_pb.setDisabled(True);

    def connectPort(self):
        if self.isConnected:
            self.disconnectPort()

        selectedPort = self.portDropDown.currentText()
        self.logging_texbox.appendPlainText(f"connecting to port: {selectedPort}")
        isConnected = self.sio.connectPort(selectedPort)

        if not isConnected:
            self.logging_texbox.appendPlainText("connection failed")
        else:
            self.logging_texbox.appendPlainText("connection success")
            self.isConnected = True
            self.connect_pb.setText("Disconnect")
            # start populating data (workers)
            self.updateData()

    def disconnectPort(self):
        self.sio.disconnectPort()
        self.isConnected = False
        self.connect_pb.setText("Connect!")


    def graphSetup(self):
        self.graphWidget_current.setBackground('w')
        self.graphWidget_current.setLabel('left', 'Ampere')
        self.graphWidget_current.addLegend()

        self.graphWidget_volt.setBackground('w')
        self.graphWidget_volt.setLabel('left', 'Volt')
        self.graphWidget_volt.addLegend()

        dataPntMun = 20
        self.x = list(range(dataPntMun))
        self.y_vol = [0 for _ in range(dataPntMun)]
        self.y_cur = [0 for _ in range(dataPntMun)]
        self.voltage_line = self.graphWidget_volt.plot(self.x, self.y_vol, pen='r')
        self.current_line = self.graphWidget_current.plot(self.x, self.y_cur, pen='r')

    def update_graphs(self, voltage, current):
        self.logging_texbox.appendPlainText("updating graphs")
        self.x = self.x[1:]
        self.x.append(self.x[-1] + 1)

        self.y_vol = self.y_vol[1:]  # Remove the first
        self.y_cur = self.y_cur[1:]  # Remove the first
        self.y_vol.append(voltage)
        self.y_cur.append(current)

        self.voltage_line.setData(self.x, self.y_vol)
        self.current_line.setData(self.x, self.y_cur)

    def startBalancing(self):
        self.logging_texbox.appendPlainText("start balancing")
        self.sio.balancePack(cell=10, switch="on")

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
        cells = self.sio.get_battInfo()
        cell_data = cells[0].strip().split("\r\n")
        cellSummary = cells[1]

        if cell_data == "error":
            print("ERROR received from getBattInfo")

        # populate voltage table
        for BoxesIndex in range(Num_Batch):
            for rowIndex in range(0, Num_Cell_Per_Batch):
                even_data = cell_data[(BoxesIndex * Num_Cell_Per_Batch * 2) + (rowIndex * 2)]
                odd_data = cell_data[(BoxesIndex * Num_Cell_Per_Batch * 2) + (rowIndex * 2) + 1]

                volt_even_val = even_data.split("\t")[1][:-3]
                volt_odd_val = odd_data.split("\t")[1][:-3]

                self.volBoxesList[BoxesIndex * 2].setItem(rowIndex, 0, QtWidgets.QTableWidgetItem(volt_even_val))
                self.volBoxesList[(BoxesIndex * 2) + 1].setItem(rowIndex, 0, QtWidgets.QTableWidgetItem(volt_odd_val))

                temp_even_val = even_data.split("\t")[2][:-3]
                temp_odd_val = odd_data.split("\t")[2][:-3]

                self.tempBoxesList[BoxesIndex * 2].setItem(rowIndex, 0, QtWidgets.QTableWidgetItem(temp_even_val))
                self.tempBoxesList[(BoxesIndex * 2) + 1].setItem(rowIndex, 0, QtWidgets.QTableWidgetItem(temp_odd_val))

        # Update main page
        self.maxVolt_textbox.setText(cellSummary["MaxVoltage"])
        self.minVolt_textbox.setText(cellSummary["MinTemp"])
        self.maxTemp_textbox.setText(cellSummary["MaxTemp"])
        self.minTemp_textbox.setText(cellSummary["MinTemp"])
        self.packCurrent_textbox.setText(cellSummary["IBUS"])
        self.rawVolt_textbox.setText(cellSummary["PackVoltage"])

        # use pack voltage and pack current to update graph
        self.update_graphs(float(cellSummary["PackVoltage"]), float((cellSummary["IBUS"])))
        self.logTimeStamp()
        self.update_SoC(self.sio.getSoC())

    def update_SoC(self, percent):
        self.SOC_progressBar.setValue(int(percent * 100))
        self.SOC_progressBar.setFormat("%.02f %%" % percent)
        self.logging_texbox.appendPlainText("updating state of charge")

    def updateLog(self, log):
        self.logging_texbox.appendPlainText(log)

    def log(self, message):
        self.logging_texbox.appendPlainText(str(message))

    def logTimeStamp(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.log("Timestamp-" + current_time)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MyWindow()
    MainWindow.show()
    sys.exit(app.exec())




