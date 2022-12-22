#!/usr/bin/env python3

# Imports ##############################################################################################################
import pathlib
import gi

from task_center.core.app import TaskCenterCore

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from task_center.core.tasks.models.collection import Collection


# Edit Dialog ##########################################################################################################
class CollectionEditDialog:
    def __init__(self, core: TaskCenterCore, collection_sidebar_manager):
        # GtkBuilder
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'collection_edit_dialog.glade').resolve()))
        self.gtk_builder.connect_signals(self)

        # Widgets
        self.dialog = self.gtk_builder.get_object('dialog')
        self.headerbar = self.gtk_builder.get_object("headerbar")
        self.name_entry = self.gtk_builder.get_object('name_entry')
        self.colour_button = self.gtk_builder.get_object('colour_button')

        # Internal Variables
        self.core = core
        self.collection_sidebar_manager = collection_sidebar_manager
        self.source_id = None
        self.collection_id = None

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_cancel_button_clicked(self, _button):
        self.dialog.hide()

    def _on_save_button_clicked(self, _button):
        name = self.name_entry.get_text()
        color_rgba = self.colour_button.get_rgba()
        color = "#{0:02x}{1:02x}{2:02x}".format(
            int(color_rgba.red * 255), int(color_rgba.green * 255), int(color_rgba.blue * 255))
        collection = Collection(name, color)
        if name:
            if not self.collection_id:
                self.collection_id = self.core.tasks_manager.create_collection(self.source_id, collection)
                self.collection_sidebar_manager.sidebars[self.source_id].add_collection_row(self.collection_id, collection)
            else:
                self.core.tasks_manager.update_collection(self.source_id, self.collection_id, collection)
                self.collection_sidebar_manager.sidebars[self.source_id].edit_collection_row(self.collection_id, collection)
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
            self.collection_id = None
            self.name_entry.set_text("")
            self.headerbar.set_title("New Tasklist")
            gdk_rgba = Gdk.RGBA()
            gdk_rgba.parse("#00ACFF")
            self.colour_button.set_rgba(gdk_rgba)
        self.dialog.show()
