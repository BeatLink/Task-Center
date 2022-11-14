
class CommonDatastore:
    type = "common"                         # Change this to a unique type when inheriting

    def __init__(self):
        self.enabled = False                # Determines whether this database account is enabled
        self.display_name = ""              # The display name for this datastore shown in the GUI

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
    def create_list(self, name, color):
        raise NotImplemented

    def get_all_lists(self):
        raise NotImplemented

    def get_list(self, id):
        raise NotImplemented

    def update_list(self, id, name="", color=""):
        raise NotImplemented

    def delete_list(self, id):
        raise NotImplemented

    # Tasks ------------------------------------------------------------------------------------------------------------
    def create_task(self):
        raise NotImplemented

    def get_all_tasks(self):
        raise NotImplemented

    def get_task(self):
        raise NotImplemented

    def update_task(self):
        raise NotImplemented

    def delete_task(self):
        raise NotImplemented
