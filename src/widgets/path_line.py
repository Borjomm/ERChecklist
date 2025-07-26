from __future__ import annotations
from PySide6.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QPushButton, QFileDialog, QComboBox
from PySide6.QtCore import QSettings
from util.utils import load_save
from util.path_helper import PathHelper
from typing import TYPE_CHECKING, Optional
from parser import invalidate
import os

if TYPE_CHECKING:
    from main_window import MainWindow


from parser.wrapper import CharacterData

class FileIO(QWidget):
    def __init__(self, parent: "MainWindow", path_helper: PathHelper):
        super().__init__(parent)
        self.initializing = True
        self.path_helper = path_helper
        self.main_window = parent
        self._data = None
        self._path = None
        self.current_index = None
        self.character_map = {}
        save_file = path_helper.get_path()
        text = save_file if save_file else ""
        self.line = QLineEdit(text=str(text), parent=self, readOnly=True)
        self.button = QPushButton("Choose Save...", parent=self)
        self.button.clicked.connect(self.open_file)

        self.characters = QComboBox()

        layout = QHBoxLayout()
        layout.addWidget(self.line)
        layout.addWidget(self.button)
        layout.addWidget(self.characters)
        self.setLayout(layout)

    def open_file(self):
        default = self.path_helper.get_default_save()
        if self._path:
            dir = os.path.dirname(self._path)
        elif default:
            dir = os.path.dirname(default)
        else:
            dir = os.getcwd()
        file_path, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select a savefile",
            dir=dir,
            filter="Elden Ring Savefiles (*.sl2);;Seamless Coop Savefiles (*.co2)"
        )
        if file_path:
            self.load_file(file_path)

    def load_file(self, path="", selection=0, load_new = True, init=False):
        if not path:
            path = self.path_helper.get_path()
        if load_new:
            self._path = path
        else:
            path = self._path
        if not path:
            return
        if init:
            selection = self.path_helper.get_character_slot()
        invalidate()
        headers = load_save(path, 0, True)
        k = 0
        selection_list = []
        self.character_map = {}
        for i, header in enumerate(headers):
                if header.name:
                    self.character_map[k] = i
                    selection_list.append(f"{header.name} - SL{header.level}")
                    k += 1
        if selection_list:
            self.characters.clear()
            self.characters.blockSignals(True)
            self.characters.addItems(selection_list)
            if self.initializing:
                self.characters.currentIndexChanged.connect(self.load_character)
                self.initializing = False
            if load_new:
                self.characters.setCurrentIndex(selection)
                self.characters.blockSignals(False)
                self.load_character(selection)
            else:
                self.characters.setCurrentIndex(self.current_index)
                self.characters.blockSignals(False)

    def get_path(self):
        return self._path
    
    def load_character(self, index: Optional[int] = None, invalidate_headers: bool = False):
        if invalidate_headers:
            invalidate()
        if index is None:
            index = self.current_index
        if index is None:
            return
        real_index = self.character_map.get(index)
        if real_index is None:
            return
        self._data: CharacterData = load_save(self._path, index, header_mode=False)
        if not self._data:
            return
        self.current_index = index
        if self.main_window.watcher and self.main_window.watcher.isRunning():
            self.main_window.stop_watcher()
        self.main_window.set_watcher(self._path)
        self.line.setText(self._path)
        self.main_window.invalidate_save()
        self.path_helper.write_to_settings(self._path, index)

    def get_data(self):
        return self._data

