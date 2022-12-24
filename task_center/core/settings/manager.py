import pathlib
import json

class SettingsManager:
    def __init__(self, appinfo):
        # Setup Settings File
        self.settings_folder = pathlib.Path(appinfo.application_folders.user_config_dir)
        self.settings_folder.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.settings_folder / "settings.json"

        # The settings itself
        self._settings_dict = {}

    # Settings ----------------------------------------------------------------------------------------------------------
    def get_all_settings(self):
        self.load()
        return self._settings_dict.keys()

    def get_setting(self, key):
        self.load()
        if key in self._settings_dict:
            return self._settings_dict[key]

    def set_setting(self, key, value):
        self._settings_dict[key] = value
        self.save()

    def delete_setting(self, key):
        del self._settings_dict[key]
        self.save()

    # Loading / Saving -------------------------------------------------------------------------------------------------
    def load(self):
        if not self.settings_file.exists():
            self.save()
        with self.settings_file.open("r") as settings_file:
            self._settings_dict = json.load(settings_file)

    def save(self):
        with self.settings_file.open("w") as settings_file:
            json.dump(self._settings_dict, settings_file, indent=4)