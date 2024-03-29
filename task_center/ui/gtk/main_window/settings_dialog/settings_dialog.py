import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from task_center.core.app import TaskCenterCore
from task_center.ui.gtk.main_window.settings_dialog.sources_list.sources_list import SourcesList
from task_center.ui.gtk.main_window.settings_dialog.window_settings.window_settings import WindowSettings


class SettingsDialog:
    def __init__(self, core: TaskCenterCore):
        # Settings Setup
        self.core = core

        # GtkBuilder Setup
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'settings_dialog.glade').resolve()))
        self.gtk_builder.connect_signals(self)

        # Dialog Setup
        self.dialog = self.gtk_builder.get_object('dialog')
        self.stack = self.gtk_builder.get_object("stack")

        # BackendManager List Setup
        self.sources_list = SourcesList(self.core)
        self.sources_list.edit_dialog.dialog.set_transient_for(self.dialog)
        self.sources_list.delete_dialog.dialog.set_transient_for(self.dialog)
        self.stack.add_titled(self.sources_list.box, "core", "Data Sources")

        # Window Settings Setup
        self.window_settings = WindowSettings(self.core.settings_manager)
        self.stack.add_titled(self.window_settings.box, "window_settings", "Window Settings")

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_dialog_delete_event(self, _window, _event):
        self.dialog.hide()
        return True

    def _on_stack_selection_changed(self, _stack, _changed_property):
        if self.stack.get_visible_child_name() == "core":
            self.sources_list.refresh_list()
        elif self.stack.get_visible_child_name() == "window_settings":
            self.window_settings.load()

    # Functions --------------------------------------------------------------------------------------------------------
    def open(self):
        self.sources_list.refresh_list()
        self.dialog.show()
