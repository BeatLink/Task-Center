import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from task_center.ui.gtk.main_window.settings_dialog.sources_list.sources_list import SourcesList


class SettingsDialog:
    def __init__(self, core):
        # Settings Setup
        self.core = core

        # GtkBuilder Setup
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'settings_dialog.glade').resolve()))
        self.gtk_builder.connect_signals(self)

        # Dialog Setup
        self.dialog = self.gtk_builder.get_object('dialog')
        self.stack = self.gtk_builder.get_object("stack")

        # Sources List Setup
        self.sources_list = SourcesList(self.core.sources)
        self.sources_list.edit_dialog.dialog.set_transient_for(self.dialog)
        self.sources_list.delete_dialog.dialog.set_transient_for(self.dialog)
        self.stack.add_titled(self.sources_list.box, "sources", "Data Sources")
        self.stack.connect("notify::visible-child", self._on_stack_selection_changed)

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_dialog_delete_event(self, _window, _event):
        self.dialog.hide()
        return True

    def _on_stack_selection_changed(self, _stack, _changed_property):
        if self.stack.get_visible_child_name() == "sources":
            self.sources_list.refresh_list()

    # Functions --------------------------------------------------------------------------------------------------------
    def open(self):
        self.sources_list.refresh_list()
        self.dialog.show()
