# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from task_center.core.app import TaskCenterCore

# Collection Delete Dialog #############################################################################################
class CollectionDeleteDialog:
    def __init__(self, core: TaskCenterCore):
        self.core = core
        self.source_id = None
        self.collection_id = None
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'collection_delete_dialog.glade').resolve()))
        self.gtk_builder.connect_signals(self)
        self.dialog = self.gtk_builder.get_object('dialog')
        self.headerbar = self.gtk_builder.get_object("headerbar")
        self.cancel_button = self.gtk_builder.get_object('cancel_button')
        self.delete_button = self.gtk_builder.get_object('delete_button')
        self.label = self.gtk_builder.get_object("label")

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_cancel_button_clicked(self, _):
        self.dialog.hide()

    def _on_delete_button_clicked(self, _):
        self.core.tasks_manager.delete_collection(self.source_id, self.collection_id)
        self.dialog.hide()

    # Functions --------------------------------------------------------------------------------------------------------
    def open(self, source_id, collection_id):
        self.source_id = source_id
        self.collection_id = collection_id
        collection = self.core.tasks_manager.get_collection(source_id, collection_id)
        self.headerbar.set_title(f"Delete {collection.name}?")
        self.label.set_text(f"Are you sure you wish to delete collection '{collection.name}'?")
        self.dialog.show()
