# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from task_center.core.app import TaskCenterCore
from task_center.core.tasks.models.collection import Collection

# Edit Dialog ##########################################################################################################
class CollectionEditDialog:
    def __init__(self, core: TaskCenterCore):
        self.core = core
        self.source_id = None
        self.collection_id = None
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'collection_edit_dialog.glade').resolve()))
        self.gtk_builder.connect_signals(self)
        self.dialog = self.gtk_builder.get_object('dialog')
        self.save_button = self.gtk_builder.get_object("save_button")
        self.headerbar = self.gtk_builder.get_object("headerbar")
        self.name_entry = self.gtk_builder.get_object('name_entry')
        self.colour_button = self.gtk_builder.get_object('colour_button')

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_cancel_button_clicked(self, _button):
        self.dialog.hide()

    def _on_save_button_clicked(self, _button):
        name = self.name_entry.get_text()
        color_rgba = self.colour_button.get_rgba()
        color = "#{0:02x}{1:02x}{2:02x}".format(
            int(color_rgba.red * 255),
            int(color_rgba.green * 255),
            int(color_rgba.blue * 255))
        collection = Collection(name, color)
        if self.collection_id:
            self.core.tasks_manager.update_collection(self.source_id, self.collection_id, collection)
        else:
            self.core.tasks_manager.create_collection(self.source_id, collection)
        self.dialog.hide()

    # Functions --------------------------------------------------------------------------------------------------------
    def open(self, source_id, collection_id=None):
        self.source_id = source_id
        if collection_id:
            self.collection_id = collection_id
            collection = self.core.tasks_manager.get_collection(self.source_id, self.collection_id)
            self.name_entry.set_text(collection.name)
            self.headerbar.set_title(f"Editing {collection.name}")
            gdk_rgba = Gdk.RGBA()
            gdk_rgba.parse(collection.color[0:7])
            self.colour_button.set_rgba(gdk_rgba)
        else:
            self.name_entry.set_text("")
            self.headerbar.set_title("New Collection")
            gdk_rgba = Gdk.RGBA()
            gdk_rgba.parse("#00ACFF")
            self.colour_button.set_rgba(gdk_rgba)
        self.dialog.show()
