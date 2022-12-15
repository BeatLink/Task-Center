#!/usr/bin/env python3

# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from task_center.core.collections.collections import Collection


# Edit Dialog ##########################################################################################################
class CollectionEditDialog:
    def __init__(self, core, collection_sidebar_manager):
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
        self.list_id = None

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_cancel_button_clicked(self, _button):
        self.dialog.hide()

    def _on_save_button_clicked(self, _button):
        name = self.name_entry.get_text()
        color_rgba = self.colour_button.get_rgba()
        color = "#{0:02x}{1:02x}{2:02x}".format(
            int(color_rgba.red * 255), int(color_rgba.green * 255), int(color_rgba.blue * 255))
        tasklist = Collection(name, color)
        if name:
            if not self.list_id:
                self.list_id = self.core.sources.list[self.source_id].create_collection(tasklist)
                self.collection_sidebar_manager.sidebars[self.source_id].add_collection(self.list_id, tasklist)
            else:
                self.core.sources.list[self.source_id].update_collection(self.list_id, tasklist)
                self.collection_sidebar_manager.sidebars[self.source_id].edit_collection(self.list_id, tasklist)
            self.dialog.hide()

    # Functions --------------------------------------------------------------------------------------------------------

    def open(self, source_id, list_id=None):
        self.source_id = source_id
        if list_id:
            self.list_id = list_id
            tasklist = self.core.sources.list[self.source_id].get_collection(self.list_id)
            self.name_entry.set_text(tasklist.name)
            self.headerbar.set_title(f"Editing {tasklist.name}")
            gdk_rgba = Gdk.RGBA()
            gdk_rgba.parse(tasklist.color[0:7])
            self.colour_button.set_rgba(gdk_rgba)
        else:
            self.list_id = None
            self.name_entry.set_text("")
            self.headerbar.set_title("New Tasklist")
            gdk_rgba = Gdk.RGBA()
            gdk_rgba.parse("#00ACFF")
            self.colour_button.set_rgba(gdk_rgba)
        self.dialog.show()
