import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from PySide6.QtCore import Signal, QThread, QTimer

class WatchdogHandler(FileSystemEventHandler):
    def __init__(self, target_file, callback):
        super().__init__()
        self._callback = callback
        self._target_file = os.path.abspath(target_file)

    def on_modified(self, event):
        if not event.is_directory:
            if os.path.abspath(event.src_path) == self._target_file:
                self._callback(event.src_path)


class FileWatcherThread(QThread):
    file_changed = Signal(str)

    def __init__(self, file_to_watch: str):
        super().__init__()
        self._target_file = os.path.abspath(file_to_watch)
        self._watch_dir = os.path.dirname(self._target_file)
        self._observer = Observer()
        self._is_reloading = False
        self._running = True

    def run(self):
        handler = WatchdogHandler(self._target_file, self._on_file_change)
        self._observer.schedule(handler, self._watch_dir, recursive=False)
        self._observer.start()
        
        while self._running:
            time.sleep(0.1)
        if self._observer.is_alive():
            self._observer.stop()
            self._observer.join()

    def _on_file_change(self, src_path):
        # emit Qt signal into the main thread
        if self._is_reloading:
            return
        self._is_reloading = True
        self.file_changed.emit(src_path)
        QTimer.singleShot(2000, self._reset_reloading_flag)



    def _reset_reloading_flag(self):
        self._is_reloading = False
        print("Reload cooldown finished.")

    def stop(self):
        self._running = False
        time.sleep(0.1)