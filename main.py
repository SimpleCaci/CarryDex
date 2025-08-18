import sys
from PyQt5 import QtWidgets, QtCore
from RecordingWindow import Ui_RecordingWindow
import speech_recognition as sr

class RecorderApp(QtWidgets.QMainWindow):
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

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = RecorderApp()
    w.show()
    sys.exit(app.exec_())
