from __future__ import annotations
from PySide6.QtWidgets import QTreeView, QVBoxLayout, QWidget, QLineEdit, QCheckBox, QHBoxLayout, QPushButton
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QSortFilterProxyModel
from typing import TYPE_CHECKING
from parser.wrapper import CharacterData
from data.consts import DLC, OFFSET, REMEMBRANCE, LINK
from util.utils import make_combo_widget

if TYPE_CHECKING:
    from main_window import MainWindow

import sqlite3

class TreeWindow(QWidget):
    def __init__(self, parent: "MainWindow", connection: sqlite3.Connection, data: CharacterData):
        super().__init__(parent)
        self.main_window = parent
        self.connection = connection
        self.data = data
        self.has_dlc = data.has_dlc() if self.data else True
        self.setWindowTitle("Boss Tracker")

        # Create the base model
        self.base_model = QStandardItemModel()

        # Create the filter proxy model
        proxy_dlc_flag = None if self.has_dlc else 0
        self.proxy_model = BossFilterProxyModel(has_dlc=proxy_dlc_flag)
        self.proxy_model.setSourceModel(self.base_model)

        self.tree = QTreeView()
        self.tree.setModel(self.proxy_model)
        self.tree.setUniformRowHeights(True)
        self.tree.setHeaderHidden(True)

        # Set up the tree view
        self.top_bar = QWidget()

        self.button_widget = QWidget()

        self.expand_button = QPushButton("Expand all")
        self.expand_button.pressed.connect(self.tree.expandAll)

        self.collapse_button = QPushButton("Collapse all")
        self.collapse_button.pressed.connect(self.tree.collapseAll)

        self.left_button_layout = QVBoxLayout()
        self.left_button_layout.addWidget(self.expand_button)
        self.left_button_layout.addWidget(self.collapse_button)
        self.button_widget.setLayout(self.left_button_layout)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search...")
        self.search.textChanged.connect(self.update_search_box)


        self.dlc_box = make_combo_widget("DLC", ["Show all", "Don't show", "Only show"], self.proxy_model.set_show_dlc, not self.has_dlc)
        self.show_box = make_combo_widget("Filter selected", ["Show all", "Show checked", "Show unchecked"], self.proxy_model.set_show_checked_only, 0)

        self.remembrance = QCheckBox

        self.top_layout = QHBoxLayout()
        self.top_layout.addWidget(self.button_widget)
        self.top_layout.addWidget(self.search)
        self.top_layout.addWidget(self.dlc_box)
        self.top_layout.addWidget(self.show_box)
        self.top_bar.setLayout(self.top_layout)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.top_bar)
        layout.addWidget(self.tree)

        # Populate the model
        self.populate_model()
        self.update_all_region_counts()

        # Resize columns
        self.tree.resizeColumnToContents(0)

    def populate_model(self):
        root_item = self.base_model.invisibleRootItem()
        region_items = {}

        query = "SELECT * FROM bosses ORDER BY is_dlc, region, name"
        cursor = self.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        load_check = self.main_window.data is not None
        self.base_model.layoutAboutToBeChanged.emit()
        for boss_id, boss_name, region, remembrance, dlc, save_bit_offset, link in rows:
            if region not in region_items:
                region_item = QStandardItem()
                region_item.setEditable(False)
                region_item.setData(region, Qt.UserRole + 1)
                root_item.appendRow(region_item)
                region_items[region] = region_item

            parent_item = region_items[region]
            boss_item = QStandardItem(boss_name)
            boss_item.setEditable(False)
            boss_item.setCheckable(False)

            if load_check:
                check = Qt.Checked if self.main_window.data.get_flag(save_bit_offset) else Qt.Unchecked
                boss_item.setCheckState(check)
            else:
                boss_item.setCheckState(Qt.Unchecked)

            boss_item.setData(remembrance, REMEMBRANCE)
            boss_item.setData(dlc, DLC)
            boss_item.setData(save_bit_offset, OFFSET)
            boss_item.setData(link, LINK)

            parent_item.appendRow(boss_item)

        self.base_model.layoutChanged.emit()

    def update_all_region_counts(self):
        for i in range(self.base_model.rowCount()):
            region_item = self.base_model.item(i)
            self.update_region_count(region_item)

    def update_region_count(self, region_item: QStandardItem):
        total = region_item.rowCount()
        checked = sum(1 for i in range(total) if region_item.child(i).checkState() == Qt.Checked)
        region_name = region_item.data(Qt.UserRole + 1)
        region_item.setText(f"{region_name} ({checked}/{total})")

    def update(self):
        if self.main_window.data is None:
            return

        root_item = self.base_model.invisibleRootItem()
        self.base_model.layoutAboutToBeChanged.emit()

        for i in range(root_item.rowCount()):
            region_item = root_item.child(i)
            for j in range(region_item.rowCount()):
                boss_item = region_item.child(j)
                offset = boss_item.data(OFFSET)
                new_state = Qt.CheckState.Checked if self.main_window.data.get_flag(offset) else Qt.CheckState.Unchecked
                check_state = boss_item.checkState()
                if new_state != check_state:
                    print(f"Updated boss: {boss_item.text()}")
                    boss_item.setCheckState(new_state)

            self.update_region_count(region_item)

        self.base_model.layoutChanged.emit()

    def update_search_box(self, text):
        if len(text) > 5:
            self.tree.expandAll()
        self.proxy_model.set_search_text(text)


class BossFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, has_dlc):
        super().__init__()
        self.show_dlc = has_dlc
        self.show_checked_only = None
        self.search_text = ""

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)
        item = model.itemFromIndex(index)

        if item.hasChildren():
            for i in range(item.rowCount()):
                if self.filterAcceptsRow(i, index):
                    return True
            return False

        if self.show_dlc is not None:
            if self.show_dlc and not item.data(DLC):
                return False
            elif not self.show_dlc and item.data(DLC):
                return False


        if self.show_checked_only is not None:
            if self.show_checked_only and item.checkState() != Qt.Checked:
                return False
            elif not self.show_checked_only and item.checkState() == Qt.Checked:
                return False

        if self.search_text:
            parent_item = item.parent()
            text = self.search_text.lower()
            if parent_item and text in parent_item.text().lower():
                return True
            if text not in item.text().lower():
                return False

        return True

    def set_show_checked_only(self, index: int):
        match index:
            case 0:
                new = None #Show all
            case 1:
                new = 1 #Checked
            case 2:
                new = 0 #Unchecked
        if self.show_checked_only != new:
            self.show_checked_only = new
            self.invalidateFilter()

    def set_search_text(self, text: str):
        self.search_text = text
        self.invalidateFilter()

    def set_show_dlc(self, index: int):
        match index:
            case 0:
                new = None #Show all
            case 1:
                new = 0 #Don't show
            case 2:
                new = 1 #Only show
        if self.show_dlc != new:
            self.show_dlc = new
            self.invalidateFilter()