import pathlib
import json

class Settings:
    def __init__(self, appinfo):
        # Setup Settings File
        self.settings_folder = pathlib.Path(appinfo.application_folders.user_config_dir)
        self.settings_folder.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.settings_folder / "settings.json"

        # The settings itself
        self.settings_dict = {}

    def load(self):
        if not self.settings_file.exists():
            self.save()
        with self.settings_file.open("r") as settings_file:
            self.settings_dict = json.load(settings_file)

    def save(self):
        with self.settings_file.open("w") as settings_file:
            json.dump(self.settings_dict, settings_file, indent=4)