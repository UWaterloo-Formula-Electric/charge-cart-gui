from PyQt6.QtCore import QObject, QThread, pyqtSignal
from time import sleep


class Worker_UpdateBatteryInfo(QObject):
    """
        Update only battery Info
    """

    finished = pyqtSignal()
    progress1 = pyqtSignal(int)

    log = pyqtSignal(str)
    batteryInfo = pyqtSignal(str)

    # Shared connector object
    def __init__(self, connector):
        super(Worker_UpdateBatteryInfo, self).__init__()
        self.connector = connector

    def run(self):
        while True:
            self.updateBatteryInfo()
            # update every 1 second
            sleep(1)

    def updateBatteryInfo(self):
        # In main class
        # connect to the port
        # emit a list of batteries

        if self.connector.getConnectionStatus:
            # self.connector.execute()
            self.batteryInfo.emit(self.connector.get_battInfo()[0])

        else:
            self.log.emit("connection failed!")

        self.finished.emit()


class Worker_UpdateState(QObject):
    """
        Update SoC
        Update current line graph
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
            #self.update_SoC()
            #self.update_Graph()
            sleep(0.1)

    def update_SoC(self):
        # trigger functions and pass in values
        # whenever is passed in emit method will be passed in whatever we connect with (update_SoC)
        soc = float(self.connector.getSoC())
        self.SoCprogress.emit(soc)
        self.finished.emit()

    def update_Graph(self):
        current = float(self.connector.getCurrent())
        self.currentProgress.emit(current)
        self.finished.emit()


