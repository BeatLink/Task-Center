from uuid import uuid4
from libdecsync import Decsync
from task_center.core.tasks.sources.generic import Source


class DecSyncSource(Source):
    type = "decsync"

    def __init__(self):
        super().__init__()
        self.decsync_dir = ""  # The path to the DecSync Folder
        self.app_id = "task_center"

    # Settings ---------------------------------------------------------------------------------------------------------
    def get_settings_dict(self):
        settings_dict = super().get_settings_dict()
        settings_dict['decsync_dir_path'] = self.decsync_dir
        return settings_dict

    def load_settings_dict(self, settings_dict):
        super().load_settings_dict(settings_dict)
        self.decsync_dir = settings_dict['decsync_dir_path']

    def _sync(self):
        for id in self.get_all_collections():
            decsync = Decsync(decsync_dir=self.decsync_dir, sync_type="tasks", collection=id, own_app_id=self.app_id)
            decsync.execute_all_new_entries(None)

    def create_collection(self, name, color):
        id = str(uuid4())
        self.update_collection(id=id, name=name, color=color)
        return id

    def get_all_collections(self):
        collections = Decsync.list_collections(decsync_dir=self.decsync_dir, sync_type="tasks")
        collections = {id: self.get_collection(id) for id in collections}
        collections = {key: value for key, value in sorted(collections.items(), key=lambda item: item[1]["name"]) if value['deleted'] != True}
        return collections

    def get_collection(self, id):
        name = Decsync.get_static_info(self.decsync_dir, sync_type="tasks", collection=id, key="name")
        color = Decsync.get_static_info(self.decsync_dir, sync_type="tasks", collection=id, key="color")
        deleted = Decsync.get_static_info(self.decsync_dir, sync_type="tasks", collection=id, key="deleted")
        return {
            "name": name,
            "color": color,
            "deleted": deleted
        }

    def update_collection(self, id, name="", color=""):
        self._sync()
        decsync = Decsync(decsync_dir=self.decsync_dir, sync_type="tasks", collection=id, own_app_id=self.app_id)
        if name:
            decsync.set_entry(["info"], "name", name)
        if color:
            decsync.set_entry(["info"], "color", color)

    def delete_collection(self, id):
        self._sync()
        decsync = Decsync(decsync_dir=self.decsync_dir, sync_type="tasks", collection=id, own_app_id=self.app_id)
        decsync.set_entry(["info"], "deleted", True)
