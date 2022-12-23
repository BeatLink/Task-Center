# Imports ##############################################################################################################
import pathlib
import gi

from task_center.core.settings import SettingsManager

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class WindowSettings:
    def __init__(self, settings: SettingsManager):
        # Settings Setup
        self.settings = settings

        # GtkBuilder Setup
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'window_settings.glade').resolve()))
        self.gtk_builder.connect_signals(self)

        # List Setup
        self.box = self.gtk_builder.get_object("box")
        self.sidebar_pane_size_spinbutton = self.gtk_builder.get_object("sidebar_pane_size_spinbutton")
        self.task_pane_size_spinbutton = self.gtk_builder.get_object("task_pane_size_spinbutton")

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_sidebar_pane_size_spinbutton_value_changed(self, _spinbutton):
        sidebar_pane_position = self.sidebar_pane_size_spinbutton.get_value()
        self.settings.set_setting("sidebar_pane_position", sidebar_pane_position)

    def _on_task_pane_size_spinbutton_value_changed(self, _spinbutton):
        task_pane_position = self.task_pane_size_spinbutton.get_value()
        self.settings.set_setting("task_pane_position", task_pane_position)

    # Functions --------------------------------------------------------------------------------------------------------
    def load(self, *_):
        self.sidebar_pane_size_spinbutton.set_value(self.settings.get_setting("sidebar_pane_position"))
        self.task_pane_size_spinbutton.set_value(self.settings.get_setting("task_pane_position"))
