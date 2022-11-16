#!/usr/bin/env python3

# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


# List Container #######################################################################################################
class DatastoreDeleteDialog:
    def __init__(self, datastores):
        # Variables
        self.datastore_id = None
        self.datastores = datastores

        # GtkBuilder
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'delete_dialog.glade').resolve()))
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
        del self.datastores.list[self.datastore_id]
        self.datastores.save_settings()
        self.dialog.hide()

    # Functions --------------------------------------------------------------------------------------------------------
    def open(self, datastore_id):
        self.datastore_id = datastore_id
        datastore = self.datastores.list[self.datastore_id]
        self.headerbar.set_title(f"Delete {datastore.display_name}?")
        self.label.set_text(f"Are you sure you wish to delete the datastore '{datastore.display_name}'?")
        self.dialog.show()
