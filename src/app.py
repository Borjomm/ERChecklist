from PySide6.QtWidgets import QApplication

import sys
import signal
import traceback
import sqlite3
import os

from main_window import MainWindow

class Application(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        sys.excepthook = self.exception_hook
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        self.aboutToQuit.connect(self.on_close)
        self.setStyle("fusion")
        self.connection = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'gamedata.db'))
        self.window = MainWindow(self, self.connection)
        self.window.show()
        sys.exit(self.exec())

    def handle_signal(self, sig, frame):
        print(f"Received signal {sig}, exiting...")
        self.quit()

    def exception_hook(self, exc_type, exc_value, exc_tb):
        traceback.print_exception(exc_type, exc_value, exc_tb)
        try:
            if hasattr(self, "connection"):
                self.connection.commit()
                self.connection.close()
        except Exception as e:
            print("Failed to save during exception:", e)
        sys.exit(1)

    def on_close(self):
        if hasattr(self, "connection"):
            self.connection.commit()
            self.connection.close()
        if hasattr(self, "window"):
            if hasattr(self.window, "watcher"):
                if self.window.watcher.isRunning():
                    self.window.watcher.stop()