
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

    # Lists ------------------------------------------------------------------------------------------------------------
    def create_list(self, tasklist):
        raise NotImplemented

    def get_all_lists(self):
        raise NotImplemented

    def get_list(self, tasklist_id):
        raise NotImplemented

    def update_list(self, tasklist_id, tasklist):
        raise NotImplemented

    def delete_list(self, tasklist_id):
        raise NotImplemented

    # Tasks ------------------------------------------------------------------------------------------------------------
    def create_task(self, tasklist_id, task):
        raise NotImplemented

    def get_all_tasks(self, tasklist_id):
        raise NotImplemented

    def get_task(self, tasklist_id, id):
        raise NotImplemented

    def get_subtasks(self, tasklist_id, id):
        pass

    def update_task(self, tasklist_id, id, task):
        raise NotImplemented

    def delete_task(self, tasklist_id, id, delete_subtasks=False):
        raise NotImplemented
