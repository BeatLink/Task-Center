# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class WindowSettings:
    def __init__(self, settings, main_window_gtk_builder):
        # Settings Setup
        self.settings = settings
        self.main_window_gtk_builder = main_window_gtk_builder

        # GtkBuilder Setup
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'window_settings.glade').resolve()))
        self.gtk_builder.connect_signals(self)

        # List Setup
        self.box = self.gtk_builder.get_object("box")
        self.sidebar_pane_size_spinbutton = self.gtk_builder.get_object("sidebar_pane_size_spinbutton")
        self.task_pane_size_spinbutton = self.gtk_builder.get_object("task_pane_size_spinbutton")
        self.sidebar_pane = self.main_window_gtk_builder.get_object('sidebar_pane')
        self.task_pane = self.main_window_gtk_builder.get_object("task_pane")

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_sidebar_pane_size_spinbutton_value_changed(self, _spinbutton):
        sidebar_pane_position = self.sidebar_pane_size_spinbutton.get_value()
        self.settings.settings_dict["sidebar_pane_position"] = sidebar_pane_position
        self.settings.save()
        self.sidebar_pane.set_position(sidebar_pane_position)

    def _on_task_pane_size_spinbutton_value_changed(self, _spinbutton):
        task_pane_position = self.task_pane_size_spinbutton.get_value()
        self.settings.settings_dict["task_pane_position"] = task_pane_position
        self.settings.save()
        self.task_pane.set_position(task_pane_position)

    # Functions --------------------------------------------------------------------------------------------------------
    def load(self, *_):
        self.sidebar_pane_size_spinbutton.set_value(self.settings.settings_dict["sidebar_pane_position"])
        self.task_pane_size_spinbutton.set_value(self.settings.settings_dict["task_pane_position"])
