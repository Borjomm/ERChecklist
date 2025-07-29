from pathlib import Path

from PySide6.QtCore import QSettings, QStandardPaths
from data import consts

class PathHelper():
    def __init__(self, ui_handler: callable):
        self.ui_handler = ui_handler
        self.settings = QSettings(consts.CREATOR, consts.APP)
        self._path = self.settings.value("most_recent")
        value = self.settings.value("recent_list")
        self._recent_list = value if value else []
        if not self._path:
            print("Finding default savefile")
            self._path = self.get_default_save()
            if self._path:
                self.settings.setValue("most_recent", self._path)
        print(f"Savefile path: {self._path}")
        
    
    def get_default_save(self):
        roaming_dir = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)).parent
        elden_ring_dir = roaming_dir / 'EldenRing'
        if not elden_ring_dir.exists():
            return None
        steam_id_folders = [f for f in elden_ring_dir.iterdir() if f.is_dir()]
        if not steam_id_folders:
            return None
        most_recent = None
        path = None
        for folder in steam_id_folders:
            save_file = elden_ring_dir / folder / 'ER0000.sl2'
            if not save_file.exists():
                save_file = elden_ring_dir / folder / 'ER0000.co2'
                if not save_file.exists():
                    continue
            mtime = save_file.stat().st_mtime
            if not most_recent or most_recent < mtime:
                most_recent = mtime
                path = save_file
        if not path:
            return None
        return str(path)
    
    def get_path(self):
        if not self._path:
            self._path = self.get_default_save()
        return self._path
    
    def write_to_settings(self, path, slot):
        self.settings.setValue("most_recent", path)
        self.settings.setValue("char_slot", slot)
        self.add_to_recent_list(path, slot)

    def add_to_recent_list(self, path, slot):
        new_entry = (path, slot)
        found_index = -1
        for i, (e_path, _) in enumerate(self._recent_list):
            if e_path == path:
                found_index = i
                break
        
        if found_index != -1:
            self._recent_list.pop(found_index)
        self._recent_list.insert(0, new_entry)
        self._recent_list = self._recent_list[:5]
        self.settings.setValue("recent_list", self._recent_list)
        self.ui_handler()

    def get_character_slot(self):
        value = self.settings.value("char_slot")
        return value if value else 0
    
    def get_recent_list(self):
        return self._recent_list
    
    def cleanup(self):
        self._recent_list = [item for item in self._recent_list if Path(item[0]).exists()]
        self.settings.setValue("recent_list", self._recent_list)

    
            
        
        