from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6 import uic
from output import Ui_MainWindow

class UI(QWidget):
    def __init__(self):
        super().__init__()

        # loading the ui file with uic module
        # uic.loadUi("untitled.ui", self)


app = QApplication([])
window = Ui_MainWindow()
window.show()
app.exec()