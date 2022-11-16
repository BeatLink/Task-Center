#!/usr/bin/env python3.7

# Imports ##############################################################################################################
import pathlib
import gi

from task_center.ui.gtk.main_window.sidebars.tasklist_sidebar.task_list_sidebar import TaskListSidebar

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # if not found in pycharm, hit alt enter to generate stubs for this
from task_center.ui.gtk.about_dialog import AboutDialog
from task_center.ui.gtk.settings_dialog.settings_dialog import SettingsDialog
from task_center.ui.gtk.main_window.task_view.task_view import TaskView


# Main Window ##########################################################################################################
class MainWindow:
    def __init__(self, core):
        # Core Setup
        self.core = core

        # Main Window Setup
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'main_window.glade').resolve()))
        self.gtk_builder.connect_signals(self)
        self.window = self.gtk_builder.get_object('main_window')
        self.headerbar_popover = self.gtk_builder.get_object("headerbar_popover")
        self.main_box = self.gtk_builder.get_object('main_box')
        self.sidebar_box = self.gtk_builder.get_object('sidebar_box')

        # Setup Tasks View
        self.tasks_treeview = TaskView(self.core.datastores)
        self.main_box.add(self.tasks_treeview.box)
        self.main_box.set_child_packing(self.tasks_treeview.box, True, True, 0, Gtk.PackType.START)

        # Setup task lists
        self.task_lists = {}
        for id, datastore in self.core.datastores.list.items():
            self.task_lists[id] = TaskListSidebar(datastore, self.tasks_treeview)
            self.sidebar_box.add(self.task_lists[id].box)
            self.sidebar_box.set_child_packing(self.task_lists[id].box, False, False, 0, Gtk.PackType.START)

        # self.tags = = GtkTagSidebar
        # self.filters = GtkFilterSidebar

        # GUI Dialogs Setup
        self.about_dialog = AboutDialog(self.core.appinfo)
        self.about_dialog.dialog.set_transient_for(self.window)
        self.settings_dialog = SettingsDialog(self.core)
        self.settings_dialog.dialog.set_transient_for(self.window)

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_about_dialog_button_clicked(self, _button):
        self.about_dialog.open()
        self.headerbar_popover.popdown()

    def _on_settings_dialog_button_clicked(self, _button):
        self.settings_dialog.open()
        self.headerbar_popover.popdown()

    def _on_quit_button_clicked(self, _):
        self.headerbar_popover.popdown()
        self.window.destroy()

    # Functions --------------------------------------------------------------------------------------------------------
    def open(self):
        self.window.show()
        self.window.maximize()

    def close(self):
        self.window.destroy()