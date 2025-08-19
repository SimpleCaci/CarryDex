import sys, time
from PyQt5 import QtWidgets, QtCore, QtGui
from MainClockWindow import Ui_MainClockWindow
from RecordingWindow import Ui_RecordingWindow
import speech_recognition as sr

import math
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QPoint, QTimer
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import QWidget

from PyQt5.QtWidgets import QWidget, QStackedWidget, QApplication, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QRegion
import sys



from radial_transition import RadialTransition
#TASKS:
#MainClockApp -> LCD bar fills up as the seconds or time go up
#RecorderApp: Convert Print statements to visuals
#Fix my importations to not make it repeat





class MainClockApp(QtWidgets.QMainWindow):
    def  __init__(self):
        super().__init__()
        self.ui = Ui_MainClockWindow()
        self.ui.setupUi(self)  #setupUi takes the python file converted from .ui and builds all the widgest and layouts 

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000) #update every second (in ms)


    def update_clock(self):
        #using strftime to grab the date since it formats it already
        date = time.strftime("%A, %B %d, %Y") #Gives Date in Format of; Monday, August 17, 2025
        self.ui.textBrowser.setText(date)

        #grabbing a struct_time object so I can change the number on each of the lcd display (Hour, Minute, Second)
        now = time.localtime()
        hour = now.tm_hour
        minute = now.tm_min
        second = now.tm_sec
        self.ui.lcdNumber.display(hour)
        self.ui.lcdNumber_2.display(minute)
        self.ui.lcdNumber_3.display(second)

        #Total seconds passed / Seconds in a total day  -> x 100 (for percentage)
        percentageOfDayDone = (((hour*60*60) + (minute * 60) + (second))) / (24*60*60) * 100
        self.ui.progressBar.setValue(int(percentageOfDayDone))


        print(f"Time Updated: {hour} : {minute} : {second} - {percentageOfDayDone} % completed")





    


class RecorderApp(QtWidgets.QMainWindow):
    #We send and create using signals to prevent crashing/error from directly updating the UI from thread
    #Signal sends messages safely from worker thread to the GUI thread
    sigText = QtCore.pyqtSignal(str) 
    sigErr  = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.ui = Ui_RecordingWindow()
        self.ui.setupUi(self)

        self.recognizer = sr.Recognizer()
        self._stopper = None
        self._bg_mic = None

        self.sigText.connect(self.ui.textBrowser.append)
        self.sigErr.connect(lambda e: self.ui.textBrowser.append(f"[ERROR] {e}"))

        self.ui.pushButton.setText("Hold to Record")
        self.ui.pushButton.pressed.connect(self.start_listening)
        self.ui.pushButton.released.connect(self.stop_listening)


        #STYLING
        self.ui.textBrowser.setStyleSheet("font-size: 16pt; font-family: Arial;")


    def start_listening(self):
        if self._stopper:  # already running
            return
        # quick ambient calibration (open a temp mic just for this)
        try:
            with sr.Microphone() as src:
                self.recognizer.adjust_for_ambient_noise(src, duration=0.3)
        except Exception as e:
            self.sigErr.emit(str(e))
            return

        # start background listener; keep mic object alive
        self._bg_mic = sr.Microphone()
        self._stopper = self.recognizer.listen_in_background(
            self._bg_mic, self._callback, phrase_time_limit=5
        )
        self.ui.pushButton.setText("Listening… (hold)")

    def stop_listening(self):
        if self._stopper:
            # stop background thread immediately
            self._stopper(wait_for_stop=False)
            self._stopper = None
        self._bg_mic = None


        QtCore.QTimer.singleShot(1000, self.save_and_clear) #prevents UI from being blocked up, wait 1s for last callback (Better than using sleep)

        self.ui.pushButton.setText("Hold to Record")



    # runs in a background thread → DO NOT touch UI directly here
    def _callback(self, recog, audio):
        try:
            text = recog.recognize_google(audio)
            if text:
                self.sigText.emit(text)
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            self.sigErr.emit(f"Recognizer error: {e}")

    def save_recorded_message(self):
        text = self.ui.textBrowser.toPlainText()
        currentTime = time.strftime("%H:%M:%S") #uses internal system clock (so it'll work even without device connected  to wifi)
        print(f'saving {text} at {currentTime}')
        
        with open("recordingLog.txt", "a", encoding="utf-8") as file: #a -> append
            file.write(f"/n {currentTime} : {text}")

    def save_and_clear(self):
        self.save_recorded_message()
        self.ui.textBrowser.clear()





class Root(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        

        self.clock = MainClockApp()
        self.rec   = RecorderApp()

        # add their central widgets inside the stack
        self.stack.addWidget(self.clock)
        self.stack.addWidget(self.rec)
        self.stack.setCurrentIndex(0)

        # transition effect
        self.transition = RadialTransition(self.stack)

        # shortcuts to switch with transition
        QtWidgets.QShortcut("F1", self, activated=lambda: self.radial_to(self.clock))
        QtWidgets.QShortcut("F2", self, activated=lambda: self.radial_to(self.rec))

    def radial_to(self, next):
        pos = self.stack.mapFromGlobal(QtGui.QCursor.pos())
        if not self.stack.rect().contains(pos):
            pos = None

        self.transition.raise_() 
        # To go to a new page with a radial transition
        self.transition.start(
            center=QPoint(self.width()//2, self.height()//2),
            duration=600,
            reverse=False,
            mid_callback=lambda: self.stack.setCurrentWidget(next),  # switch page at max circle
            finished_callback=lambda: self.transition.start(
                center=QPoint(self.width()//2, self.height()//2),
                duration=600,
                reverse=True
            )
        )




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Root()
    w.show() #creating a variable to make sure it's not garbage collected
    sys.exit(app.exec_())
