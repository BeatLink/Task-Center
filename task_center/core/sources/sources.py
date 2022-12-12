from task_center.core.sources.caldav import CaldavSource
from task_center.core.sources.database import DatabaseSource
from task_center.core.sources.decsync import DecSyncSource

MODELS = {
    "decsync": DecSyncSource,
    "database": DatabaseSource,
    "caldav": CaldavSource
}


# Sources -------------------------------------------------------------------------------------------------------
class Sources:
    def __init__(self, settings):
        self.settings = settings
        self.list = {}
        self.load_from_settings()

    # Settings ---------------------------------------------------------------------------------------------------------
    def load_from_settings(self):
        self.settings.load()
        if "sources" not in self.settings.settings_dict:
            self.settings.settings_dict['sources'] = {}
            self.settings.save()
        for id, source_setting in self.settings.settings_dict['sources'].items():
            self.list[id] = MODELS[source_setting['type']]()
            self.list[id].load_settings_dict(self.settings.settings_dict['sources'][id])

    def save_settings(self):
        self.settings.settings_dict['sources'] = {
            source_id: source.get_settings_dict() for (source_id, source) in self.list.items()
        }
        self.settings.save()