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

