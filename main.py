# main.py
import sys
from datetime import datetime
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from mydesign import Ui_MainWindow  # your generated file

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # update once per second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()  # show immediately

    def update_time(self):
        now = datetime.now()
        # show HH:MM:SS on the LCD
        self.ui.lcdNumber.display(now.strftime("%H:%M:%S"))
        # optional: progress bar = seconds in the current minute
        self.ui.progressBar.setMaximum(59)
        self.ui.progressBar.setValue(now.second)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Main()
    win.show()
    sys.exit(app.exec_())
