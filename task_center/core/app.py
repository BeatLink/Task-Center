from task_center.core.appinfo import AppInfo
from task_center.core.datastores.datastores import Datastores
from task_center.core.settings.settings import Settings


class TaskCenterCore:
    def __init__(self):
        self.appinfo = AppInfo()
        self.settings = Settings(self.appinfo)
        self.datastores = Datastores(self.settings)
