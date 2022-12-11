#!/usr/bin/env python3

# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


# List Container #######################################################################################################
class SourceDeleteDialog:
    def __init__(self, sources):
        # Variables
        self.source_id = None
        self.sources = sources

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
        del self.sources.list[self.source_id]
        self.sources.save_settings()
        self.dialog.hide()

    # Functions --------------------------------------------------------------------------------------------------------
    def open(self, source_id):
        self.source_id = source_id
        source = self.sources.list[self.source_id]
        self.headerbar.set_title(f"Delete {source.display_name}?")
        self.label.set_text(f"Are you sure you wish to delete the source '{source.display_name}'?")
        self.dialog.show()
