from __future__ import annotations
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMenuBar, QTabWidget
from typing import TYPE_CHECKING
from functools import partial

from util import utils
from util.path_helper import PathHelper
from util import watchdog

from widgets.tree import TreeWindow

from widgets.path_line import FileIO

from sqlite3 import Connection

from parser import *

if TYPE_CHECKING:
    from app import Application

class MainWindow(QMainWindow):
    def __init__(self, app: "Application", connection: Connection):
        super().__init__()
        self.initializing = True
        self.app = app
        self.connection = connection

        self.menu = QMenuBar()
        self.file_menu = self.menu.addMenu("File")
        self.load_recent = self.file_menu.addMenu("Load Recent")


        self.path_helper = PathHelper(self)
        coords = utils.get_spawn_coordinates(1920, 1080)

        self.window_title = "Elden Ring Checklist"
        self.setWindowTitle(self.window_title)
        self.setGeometry(*coords)
        self.data = None
        self.watcher = None
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.file_io = FileIO(self, self.path_helper)

        self.file_io.load_file(init=True)
        self.path = self.file_io.get_path()
        self.data = self.file_io.get_data()

        exit_action = utils.make_action(self, "Exit", self.app.on_close, "Ctrl+Q")
        invalidate_action = utils.make_action(self, "Reload", lambda: self.file_io.load_file("", load_new = False), "f5")
        load_from_current_game = utils.make_action(self, "Locate Save", lambda: self.file_io.load_file(self.path_helper.get_default_save()), "f8")

        self.generate_recent()
        self.file_menu.addAction(invalidate_action)
        self.file_menu.addAction(load_from_current_game)
        self.file_menu.addAction(exit_action)
        self.setMenuBar(self.menu)

        self.tabs = QTabWidget()

        main_layout.addWidget(self.file_io)
        main_layout.addWidget(self.tabs)
        self.boss_window = TreeWindow(self, self.connection, self.data)
        self.tabs.addTab(self.boss_window, "Bosses")
        self.tabs.addTab(QWidget(), "???")

        self.initializing = False

    def generate_recent(self):
        self.load_recent.clear()
        for p, s in self.path_helper.get_recent_list():
            
            action = utils.make_action(self, p, partial(self.file_io.load_file, p, s))
            self.load_recent.addAction(action)

    def set_watcher(self, filepath: str):
        self.watcher = watchdog.FileWatcherThread(filepath)
        self.watcher.file_changed.connect(self.on_file_changed)
        self.watcher.start()

    def stop_watcher(self):
        self.watcher.stop()



    def on_file_changed(self, path: str):
        # This slot is called whenever a watched file is modified
        print("Changed")
        self.file_io.load_character()

    def invalidate_save(self):
        if self.initializing:
            return
        self.boss_window.update()


    

