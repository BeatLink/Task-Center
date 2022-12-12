# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from task_center.ui.gtk.main_window.settings_dialog.sources_list.edit_dialog.edit_dialog import SourceEditDialog
from task_center.ui.gtk.main_window.settings_dialog.sources_list.delete_dialog.delete_dialog import SourceDeleteDialog


# List Row #############################################################################################################
class SourceListRow:
    def __init__(self):
        gtk_builder = Gtk.Builder()
        gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'sources_list.glade').resolve()))
        self.event_box = gtk_builder.get_object('row_box')
        self.label = gtk_builder.get_object("row_label")
        self.row = Gtk.ListBoxRow()
        self.row.add(self.event_box)
        self.row.show_all()


class SourcesList:
    def __init__(self, core):
        # Settings Setup
        self.core = core

        # GtkBuilder Setup
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'sources_list.glade').resolve()))
        self.gtk_builder.connect_signals(self)

        # List Setup
        self.box = self.gtk_builder.get_object("box")
        self.listbox = self.gtk_builder.get_object("listbox")
        self.menu = self.gtk_builder.get_object("menu")
        self.edit_dialog = SourceEditDialog(self.core.sources)
        self.edit_dialog.save_button.connect("clicked", self.refresh_list)
        self.delete_dialog = SourceDeleteDialog(self.core.sources)
        self.delete_dialog.delete_button.connect("clicked", self.refresh_list)

        # Variables
        self.rows = {}
        self.selected_row = None

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_add_source_button_clicked(self, _button):
        self.edit_dialog.open(None)

    def _on_listbox_button_press_event(self, _box, button, id):
        if button.button == 3:
            self.selected_row = id
            self.menu.popup_at_pointer(None)

    def _on_edit_source_button_activate(self, _button):
        self.edit_dialog.open(self.selected_row)
        self.menu.popdown()

    def _on_delete_source_button_activate(self, _button):
        self.delete_dialog.open(self.selected_row)
        self.menu.popdown()

    # Functions --------------------------------------------------------------------------------------------------------
    def refresh_list(self, *_):
        for row_id in self.rows:
            self.listbox.remove(self.rows[row_id].row)
        self.rows = {}
        for id, source in self.core.sources.list.items():
            self.rows[id] = SourceListRow()
            self.rows[id].event_box.connect("button-press-event", self._on_listbox_button_press_event, id)
            self.rows[id].row.id = id
            self.listbox.insert(self.rows[id].row, -1)
            self.rows[id].label.set_text(source.display_name)
