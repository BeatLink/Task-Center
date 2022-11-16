import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from task_center.ui.gtk.settings_dialog.datastores.datastore_list.datastore_list import DatastoreList


class SettingsDialog:
    def __init__(self, core):
        # Settings Setup
        self.core = core

        # GtkBuilder Setup
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'settings_dialog.glade').resolve()))
        self.gtk_builder.connect_signals(self)

        # Dialog Setup
        self.dialog = self.gtk_builder.get_object('dialog')
        self.stack = self.gtk_builder.get_object("stack")

        # Datastore List Setup
        self.datastore_list = DatastoreList(self.core.datastores)
        self.datastore_list.edit_dialog.dialog.set_transient_for(self.dialog)
        self.stack.add_titled(self.datastore_list.box, "datastores", "Data Sources")
        self.stack.connect("notify::visible-child", self._on_stack_selection_changed)

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_dialog_delete_event(self, _window, _event):
        self.dialog.hide()
        return True

    def _on_stack_selection_changed(self, _stack, _changed_property):
        if self.stack.get_visible_child_name() == "datastores":
            self.datastore_list.refresh_list()

    # Functions --------------------------------------------------------------------------------------------------------
    def open(self):
        self.datastore_list.refresh_list()
        self.dialog.show()
