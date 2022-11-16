# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from uuid import uuid4
from task_center.core.datastores.datastores import MODELS


# Edit Dialog ##########################################################################################################
class DatastoreEditDialog:
    def __init__(self, datastores):
        # Settings Setup
        self.datastores = datastores
        self.datastore_id = ""

        # GtkBuilder Setup
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'edit_dialog.glade').resolve()))
        self.gtk_builder.connect_signals(self)

        # Widgets Setup
        self.dialog = self.gtk_builder.get_object('dialog')
        self.save_button = self.gtk_builder.get_object("save_button")
        self.headerbar = self.gtk_builder.get_object("headerbar")
        self.grid = self.gtk_builder.get_object("grid")
        self.enabled_switch = self.gtk_builder.get_object("enabled_switch")
        self.name_entry = self.gtk_builder.get_object("name_entry")
        self.type_combobox = self.gtk_builder.get_object("type_combobox")
        self.type_label = self.gtk_builder.get_object("type_label")
        self.type_stack = self.gtk_builder.get_object("type_stack")
        self.decsync_filechooser_box = self.gtk_builder.get_object("decsync_filechooser_box")
        self.decsync_filechooser_button = self.gtk_builder.get_object("decsync_filechooser_button")
        self.decsync_filechooser_clear_button = self.gtk_builder.get_object("decsync_filechooser_clear_button")
        self.caldav_url_entry = self.gtk_builder.get_object("caldav_url_entry")
        self.caldav_username_entry = self.gtk_builder.get_object("caldav_username_entry")
        self.caldav_password_entry = self.gtk_builder.get_object("caldav_password_entry")

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_cancel_button_clicked(self, *_):
        self.dialog.hide()

    def _on_save_button_clicked(self, _button):
        self._save_settings()
        self.dialog.hide()

    def _on_type_combobox_changed(self, _combobox):
        id = self.type_combobox.get_active_id()
        self.type_stack.set_visible_child_name(id)

    def _on_decsync_filechooser_button_file_set(self, *_):
        if self.decsync_filechooser_button.get_uri():
            self.decsync_filechooser_clear_button.set_visible(True)

    def _on_decsync_filechooser_clear_button_clicked(self, *_):
        self.decsync_filechooser_button.unselect_all()
        self.decsync_filechooser_clear_button.set_visible(False)

    # Internal functions -----------------------------------------------------------------------------------------------
    def _save_settings(self):
        datastore_type = self.type_combobox.get_active_id()
        if not self.datastore_id:
            self.datastore_id = str(uuid4())
            self.datastores.list[self.datastore_id] = MODELS[datastore_type]()
        self.datastores.list[self.datastore_id].enabled = self.enabled_switch.get_active()
        self.datastores.list[self.datastore_id].display_name = self.name_entry.get_text()
        if datastore_type == "caldav":
            self.datastores.list[self.datastore_id].url = self.caldav_url_entry.get_text()
            self.datastores.list[self.datastore_id].username = self.caldav_username_entry.get_text()
            self.datastores.list[self.datastore_id].password = self.caldav_password_entry.get_text()
        elif datastore_type == "decsync":
            path = self.decsync_filechooser_button.get_uri() if self.decsync_filechooser_button.get_uri() else ""
            path = path.replace("file://", "")
            self.datastores.list[self.datastore_id].decsync_dir = path
        self.datastores.save_settings()

    def _initialize(self):
        self.enabled_switch.set_active(False)
        self.name_entry.set_text("")
        self.type_combobox.set_active_id("caldav")
        self.caldav_url_entry.set_text("")
        self.caldav_username_entry.set_text("")
        self.caldav_password_entry.set_text("")
        self.decsync_filechooser_button.unselect_all()
        self.decsync_filechooser_clear_button.set_visible(False)
        self.headerbar.set_title("Adding Datastore")

    def _load_settings(self):
        self.datastores.load_from_settings()
        self.enabled_switch.set_active(self.datastores.list[self.datastore_id].enabled)
        self.name_entry.set_text(self.datastores.list[self.datastore_id].display_name)
        self.headerbar.set_title(f"Editing {self.datastores.list[self.datastore_id].display_name}")
        self.type_combobox.set_active_id(self.datastores.list[self.datastore_id].type)
        if self.datastores.list[self.datastore_id].type == "caldav":
            self.caldav_url_entry.set_text(self.datastores.list[self.datastore_id].url)
            self.caldav_username_entry.set_text(self.datastores.list[self.datastore_id].username)
            self.caldav_password_entry.set_text(self.datastores.list[self.datastore_id].password)
        elif self.datastores.list[self.datastore_id].type == "decsync":
            path = self.datastores.list[self.datastore_id].decsync_dir
            if path:
                self.decsync_filechooser_button.set_uri(f"file://{path}")
                self.decsync_filechooser_clear_button.set_visible(True)
            else:
                self.decsync_filechooser_button.unselect_all()
                self.decsync_filechooser_clear_button.set_visible(False)

    # Functions --------------------------------------------------------------------------------------------------------
    def open(self, datastore_id=None):
        self.datastore_id = datastore_id
        if self.datastore_id:
            self._load_settings()
        else:
            self._initialize()
        self.dialog.show_now()
