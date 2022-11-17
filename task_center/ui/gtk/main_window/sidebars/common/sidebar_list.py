#!/usr/bin/env python3


# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


# List Row #############################################################################################################
class SidebarListRow:
    def __init__(self):
        gtk_builder = Gtk.Builder()
        gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'sidebar_list.glade').resolve()))
        self.event_box = gtk_builder.get_object('row_event_box')
        self.box = gtk_builder.get_object("row_box")
        self.icon_label = gtk_builder.get_object("row_icon_label")
        self.title_label = gtk_builder.get_object("row_title_label")
        self.row = Gtk.ListBoxRow()
        self.row.add(self.event_box)
        self.row.show_all()


# List Container #######################################################################################################
class SidebarList:
    def __init__(self, editor, context_menu, list_name):
        # Setup GTK Builder
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str(pathlib.Path(__file__).parent.resolve() / 'sidebar_list.glade'))

        # Widgets
        self.box = self.gtk_builder.get_object('box')
        self.label = self.gtk_builder.get_object('label')
        self.label.set_text(list_name)
        self.add_button = self.gtk_builder.get_object("add_button")
        self.listbox = self.gtk_builder.get_object("listbox")

        # Other Widgets
        self.editor = editor
        self.context_menu = context_menu

        # Variables
        self.rows = {}

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_heading_clicked(self, _, event_button):
        if event_button.button == 1:
            content_revealer = self.gtk_builder.get_object('revealer')
            add_button_revealer = self.gtk_builder.get_object('add_button_revealer')
            for revealer in content_revealer, add_button_revealer:
                revealer.set_reveal_child(not revealer.get_reveal_child())

    def _on_add_button_clicked(self, _):
        pass

    def _on_listbox_row_activated(self, *_):
        pass

    def _on_listbox_button_press_event(self, box, button, id):
        pass

    # Functions --------------------------------------------------------------------------------------------------------
    def add_row(self, id, text, color, icon_character):
        self.rows[id] = SidebarListRow()
        self.rows[id].event_box.connect("button-press-event", self._on_listbox_button_press_event, id)
        self.rows[id].row.id = id
        self.listbox.insert(self.rows[id].row, -1)
        self.edit_row(id, text, color, icon_character)

    def edit_row(self, id, text, color, icon_character):
        self.rows[id].icon_label.set_markup(f'<span foreground="{color}">{icon_character}</span>')
        self.rows[id].title_label.set_text(text)

    def delete_row(self, id):
        self.listbox.remove(self.rows[id].row)
        del self.rows[id]

    def clear_rows(self):
        for row_id in self.rows:
            self.listbox.remove(self.rows[row_id].row)
        self.rows = {}
