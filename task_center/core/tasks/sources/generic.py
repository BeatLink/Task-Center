class Source:
    type = "common"                         # Change this to a unique type when inheriting

    def __init__(self):
        self.enabled = False                # Determines whether this database account is enabled
        self.display_name = ""              # The display name for this source shown in the GUI

    # Settings ---------------------------------------------------------------------------------------------------------
    def get_settings_dict(self):
        return {
            "enabled": self.enabled,
            "type": self.type,
            "display_name": self.display_name
        }

    def load_settings_dict(self, settings_dict):
        self.enabled = settings_dict['enabled']
        self.display_name = settings_dict['display_name']

    # Collections ------------------------------------------------------------------------------------------------------
    def create_collection(self, collection):
        raise NotImplemented

    def get_all_collections(self):
        raise NotImplemented

    def get_collection(self, collection_id):
        raise NotImplemented

    def update_collection(self, collection_id, collection):
        raise NotImplemented

    def delete_collection(self, collection_id):
        raise NotImplemented

    def create_task(self, collection_id, task):
        raise NotImplemented

    def get_all_tasks(self, collection_id):
        raise NotImplemented

    def get_task(self, collection_id, task_id):
        raise NotImplemented

    def update_task(self, collection_id, task_id, task):
        raise NotImplemented

    def delete_task(self, collection_id, task_id):
        raise NotImplemented
