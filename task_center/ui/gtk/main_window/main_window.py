#!/usr/bin/env python3.7

# Imports ##############################################################################################################
import pathlib
import gi


from .tasks.task_pane.task_pane import TaskPane

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # if not found in pycharm, hit alt enter to generate stubs for this
from task_center.core.app import TaskCenterCore
from task_center.ui.gtk.main_window.tasks.collections.sidebar.collection_sidebar import CollectionSidebar
from task_center.ui.gtk.main_window.tasks.tasklist.tasklist import Tasklist
from .about import AboutDialog
from .settings import SettingsDialog

# Main Window ##########################################################################################################
class MainWindow:
    def __init__(self, core: TaskCenterCore):
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
        self.sidebar_box = self.gtk_builder.get_object('sidebar_box')
        self.collections_box = self.gtk_builder.get_object("collections_box")
        self.main_box = self.gtk_builder.get_object("main_box")

        # Setup Task Pane
        self.task_pane = TaskPane(self.core, self.gtk_builder)
        self.pane = self.gtk_builder.get_object("task_pane")
        self.tasks_box = self.gtk_builder.get_object("task_box")
        self.tasks_box.add(self.task_pane.stack)
        self.tasks_box.set_child_packing(self.task_pane.stack, True, True, 0, Gtk.PackType.START)

        # Setup Tasklist
        self.tasklist = Tasklist(self.core, self.task_pane)
        self.tasklist_box = self.gtk_builder.get_object("tasklist_box")
        self.tasklist_box.add(self.tasklist.box)
        self.tasklist_box.set_child_packing(self.tasklist.box, True, True, 0, Gtk.PackType.START)

        # Setup Collection Sidebars
        self.collection_sidebars = {}
        for source_id in self.core.tasks_manager.get_all_sources():
            sidebar = CollectionSidebar(self.core, source_id)
            sidebar.refresh_list(source_id)
            sidebar.listbox.connect("row-activated", self._on_sidebar_listbox_row_activated, source_id)
            sidebar.update_menubutton.connect("activate", self._on_update_menubutton_activate, source_id)
            sidebar.edit_dialog.dialog.set_transient_for(self.window)
            sidebar.delete_dialog.dialog.set_transient_for(self.window)
            self.collections_box.add(sidebar.box)
            self.collections_box.set_child_packing(sidebar.box, False, False, 0, Gtk.PackType.START)
            self.collection_sidebars[source_id] = sidebar

        # Setup task lists

        # self.tags = = GtkTagSidebar
        # self.filters = GtkFilterSidebar

        # About Dialog Setup
        self.about_dialog = AboutDialog(self.core.app_info_manager)
        self.about_dialog.dialog.set_transient_for(self.window)

        # Settings Dialog Setup
        self.settings_dialog = SettingsDialog(self.core)
        self.settings_dialog.dialog.set_transient_for(self.window)
        self.settings_dialog.window_settings.sidebar_pane_size_spinbutton.connect(
            "value-changed", self._on_settings_dialog_sidebar_pane_spinbutton_changed)
        self.settings_dialog.window_settings.task_pane_size_spinbutton.connect(
            "value-changed", self._on_settings_dialog_task_pane_spinbutton_changed)

        # Todo, connect sources edit/delete dialog apply button signals to collection update method


    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_about_dialog_button_clicked(self, _button):
        self.about_dialog.open()
        self.popover.popdown()

    def _on_settings_dialog_button_clicked(self, _button):
        self.settings_dialog.open()
        self.popover.popdown()

    def _on_settings_dialog_sidebar_pane_spinbutton_changed(self, _spinbutton):
        spinbutton = self.settings_dialog.window_settings.sidebar_pane_size_spinbutton
        self.sidebar_pane.set_position(spinbutton.get_value())

    def _on_settings_dialog_task_pane_spinbutton_changed(self, _spinbutton):
        spinbutton = self.settings_dialog.window_settings.task_pane_size_spinbutton
        self.task_pane.pane.set_position(spinbutton.get_value())

    def _on_quit_button_clicked(self, _):
        self.popover.popdown()
        self.window.destroy()

    def _on_window_size_allocate(self, _window, _rectangle):
        self.sidebar_pane.set_position(self.core.settings_manager.get_setting("sidebar_pane_position"))
        if self.pane.get_child2().get_visible():
            self.pane.set_position(self.core.settings_manager.get_setting("task_pane_position"))
        else:
            self.pane.set_position(self.pane.props.max_position)
        self.core.settings_manager.set_setting("window_is_maximized", self.window.is_maximized())
        self.core.settings_manager.set_setting("window_size", self.window.get_size())
        self.core.settings_manager.save()

    def _on_sidebar_pane_position_notify(self, _pane, _position):
        self.sidebar_pane.set_position(self.core.settings_manager.get_setting("sidebar_pane_position"))

    def _on_task_pane_position_notify(self, _pane, _position):
        if _pane.get_child2().get_visible():
            self.pane.set_position(self.core.settings_manager.get_setting("task_pane_position"))
        else:
            self.pane.set_position(self.pane.props.max_position)


    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_sidebar_listbox_row_activated(self, _listbox, _listbox_row, source_id):
        print("here")
        print(_listbox)
        print(_listbox_row)
        print(source_id)
        sidebar = self.collection_sidebars[source_id]
        collection_id = sidebar.selected_collection_id
        self.refresh_taskview(source_id, collection_id)

    def _on_update_menubutton_activate(self, _menubutton, source_id):
        sidebar = self.collection_sidebars[source_id]
        collection_id = sidebar.selected_collection_id
        self.refresh_taskview(source_id, collection_id)

    def refresh_taskview(self, source_id, collection_id):
        all_tasks = self.core.tasks_manager.get_all_tasks(source_id, collection_id)
        task_list = {(source_id, collection_id, task_id): task for task_id, task in all_tasks.items()}
        self.tasklist.refresh_list(task_list)


    # Functions --------------------------------------------------------------------------------------------------------
    def open(self):
        self.core.settings_manager.load()
        if not self.core.settings_manager.get_setting("sidebar_pane_position"):
            self.core.settings_manager.set_setting("sidebar_pane_position", 250)
        if not self.core.settings_manager.get_setting("task_pane_position"):
            self.core.settings_manager.set_setting("task_pane_position", 800)
        if self.core.settings_manager.get_setting("window_is_maximized"):
            self.window.maximize()
        else:
            self.window.unmaximize()
            window_size = self.core.settings_manager.get_setting("window_size")
            if window_size:
                window_size = self.core.settings_manager.get_setting("window_size")
                self.window.resize(*window_size)
            else:
                self._on_window_size_allocate(None, None)
        self.window.show()

    def close(self):
        self.window.destroy()