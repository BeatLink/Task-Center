import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from task_center.ui.gtk.setting_window.datastores.edit_dialog.edit_dialog import DatastoreEditDialog


class DatastoreList:
    def __init__(self, datastores):
        # Settings Setup
        self.datastores = datastores

        # GtkBuilder Setup
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'datastore_list.glade').resolve()))
        self.gtk_builder.connect_signals(self)

        # Dialog Setup
        self.box = self.gtk_builder.get_object('box')
        self.type_menu = self.gtk_builder.get_object("type_menu")
        self.edit_dialog = DatastoreEditDialog(self.datastores)

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_add_datastore_button_clicked(self, _button):
        self.edit_dialog.open(None)
