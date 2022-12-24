from task_center.core.appinfo import AppInfoManager
from task_center.core.tasks import TasksManager
from task_center.core.settings import SettingsManager


class TaskCenterCore:
    def __init__(self):
        self.app_info_manager = AppInfoManager()
        self.settings_manager = SettingsManager(self.app_info_manager)
        self.tasks_manager = TasksManager(self.settings_manager)
