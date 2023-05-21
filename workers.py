from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from serial_parse import SerialConnect
from charge_cart_GUI import Ui_MainWindow
import sys
from numpy import random
from time import sleep


# 1: dev_mod/ 0: test_mode
global env_dev
env_dev = 0


class Worker_UpdateBatteryInfo(QObject):
    """
        Update only battery Info
    """

    finished = pyqtSignal()
    progress1 = pyqtSignal(int)

    log = pyqtSignal(str)
    batteryInfo = pyqtSignal(list)

    # Shared connector object
    def __init__(self, connector):
        super(Worker_UpdateBatteryInfo, self).__init__()
        self.connector = connector

    def run(self):
        while True:
            self.updateBatteryInfo()
            sleep(0.1)

    def updateBatteryInfo(self):
        # connect to the port
        # emit a list of batteries
        # self.batteryInfo.emit([{"battery": 3}])

        if self.connector.port_setup() == True:
            self.connector.execute()
            self.batteryInfo.emit(self.connector.get_battInfo())

        else:
            self.log.emit("connection failed!")

        # environment toggle
        if (env_dev == 0):
            self.batteryInfo.emit([{"battery": 3}])

        self.finished.emit()


class Worker_UpdateState(QObject):
    """
        Update SoC
        Uddate current line graph
        Update voltage line graph
    """

    finished = pyqtSignal()
    progress1 = pyqtSignal(int)

    log = pyqtSignal(str)
    SoCprogress = pyqtSignal(float)
    currentProgress = pyqtSignal(float)
    voltProgress = pyqtSignal(float)

    def __init__(self, connector):
        super(Worker_UpdateState, self).__init__()
        self.connector = connector

    def run(self):
        while True:
            self.update_SoC()
            self.update_Volt()
            self.update_Current()
            sleep(0.1)

    def update_SoC(self):
        # trigger functions and pass in values
        # whenever is passed in emit method will be passed in whatever we connect with (update_SoC)
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


