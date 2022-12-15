#!/usr/bin/env python3

# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


# List Container #######################################################################################################
class CollectionDeleteDialog:
    def __init__(self, core, collection_sidebar_manager):
        # Variables
        self.core = core
        self.source_id = ""
        self.collection_id = None
        self.collection_sidebar_manager = collection_sidebar_manager

        # GtkBuilder
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'collection_delete_dialog.glade').resolve()))
        self.gtk_builder.connect_signals(self)

        # Widgets
        self.dialog = self.gtk_builder.get_object('dialog')
        self.headerbar = self.gtk_builder.get_object("headerbar")
        self.cancel_button = self.gtk_builder.get_object('cancel_button')
        self.delete_button = self.gtk_builder.get_object('delete_button')
        self.label = self.gtk_builder.get_object("label")


    def _on_cancel_button_clicked(self, _):
        self.dialog.hide()

    def _on_delete_button_clicked(self, _):
        self.core.sources.list[self.source_id].delete_collection(self.collection_id)
        self.collection_sidebar_manager.sidebars[self.source_id].delete_collection(self.collection_id)
        self.dialog.hide()

    # Functions --------------------------------------------------------------------------------------------------------
    def open(self, source_id, collection_id):
        self.source_id = source_id
        self.collection_id = collection_id
        collection = self.core.sources.list[self.source_id].get_collection(self.collection_id)
        self.headerbar.set_title(f"Delete {collection.name}?")
        self.label.set_text(f"Are you sure you wish to delete collection '{collection.name}'?")
        self.dialog.show()
