#!/usr/bin/env python3.7

# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # if not found in pycharm, hit alt enter to generate stubs for this
from .tasklist.tasklist import Tasklist
from .sidebars.sources_sidebar.sources_sidebar import SourcesSidebar
from .taskview.taskview import TaskView
from .about_dialog import AboutDialog
from .settings_dialog import SettingsDialog

# Main Window ##########################################################################################################
class MainWindow:
    def __init__(self, core):
        # Core Setup
        self.core = core

        # Main Window Setup
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'main_window.glade').resolve()))
        self.gtk_builder.connect_signals(self)

        # Widgets
        self.window = self.gtk_builder.get_object('window')
        self.popover = self.gtk_builder.get_object("popover")
        self.sidebar_pane = self.gtk_builder.get_object('sidebar_pane')
        self.task_pane = self.gtk_builder.get_object("task_pane")
        self.sidebar_box = self.gtk_builder.get_object('sidebar_box')
        self.tasklist_box = self.gtk_builder.get_object('tasklist_box')
        self.task_box = self.gtk_builder.get_object('task_box')

        # Setup Task Pane
        self.taskview = TaskView(self.core.sources, self.task_pane)
        self.task_box.add(self.taskview.box)
        self.task_box.set_child_packing(self.taskview.box, True, True, 0, Gtk.PackType.START)

        # Setup Tasklist Pane
        self.tasklist = Tasklist(self.core.sources, self.taskview)
        self.tasklist_box.add(self.tasklist.box)
        self.task_box.set_child_packing(self.tasklist.box, True, True, 0, Gtk.PackType.START)

        # Setup Sources Sidebars
        self.sources_sidebar = SourcesSidebar(self.core.sources, self.tasklist)
        self.sidebar_box.add(self.sources_sidebar.box)
        self.sidebar_box.set_child_packing(self.sources_sidebar.box, True, True, 0, Gtk.PackType.START)
        self.sources_sidebar.edit_dialog.dialog.set_transient_for(self.window)
        self.sources_sidebar.delete_dialog.dialog.set_transient_for(self.window)

        # self.tags = = GtkTagSidebar
        # self.filters = GtkFilterSidebar

        # About Dialog Setup
        self.about_dialog = AboutDialog(self.core.app_info)
        self.about_dialog.dialog.set_transient_for(self.window)

        # Settings Dialog Setup
        self.settings_dialog = SettingsDialog(self.core, self.gtk_builder)
        self.settings_dialog.dialog.set_transient_for(self.window)


    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_about_dialog_button_clicked(self, _button):
        self.about_dialog.open()
        self.popover.popdown()

    def _on_settings_dialog_button_clicked(self, _button):
        self.settings_dialog.open()
        self.popover.popdown()

    def _on_quit_button_clicked(self, _):
        self.popover.popdown()
        self.window.destroy()

    def _on_window_size_allocate(self, _window, _rectangle):
        self.sidebar_pane.set_position(self.core.settings.settings_dict["sidebar_pane_position"])
        self.core.settings.settings_dict["window_is_maximized"] = self.window.is_maximized()
        self.core.settings.settings_dict["window_size"] = self.window.get_size()
        self.core.settings.save()

    def _on_sidebar_pane_position_notify(self, _pane, _position):
        self.sidebar_pane.set_position(self.core.settings.settings_dict["sidebar_pane_position"])

    # Functions --------------------------------------------------------------------------------------------------------
    def open(self):
        self.core.settings.load()
        if "window_is_maximized" in self.core.settings.settings_dict:
            if self.core.settings.settings_dict['window_is_maximized']:
                self.window.maximize()
            else:
                self.window.unmaximize()
                if "window_size" in self.core.settings.settings_dict:
                    window_size = self.core.settings.settings_dict["window_size"]
                    self.window.resize(*window_size)
                else:
                    self._on_window_size_allocate(None, None)
        self.window.show()

    def close(self):
        self.window.destroy()