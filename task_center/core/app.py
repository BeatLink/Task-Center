from task_center.core.appinfo import AppInfo
from task_center.core.sources.sources import Sources
from task_center.core.settings.settings import Settings


class TaskCenterCore:
    def __init__(self):
        self.app_info = AppInfo()
        self.settings = Settings(self.app_info)
        self.sources = Sources(self.settings)
