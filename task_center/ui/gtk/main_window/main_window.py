# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # if not found in pycharm, hit alt enter to generate stubs for this
from task_center.core.app import TaskCenterCore
from task_center.ui.gtk.main_window.about_dialog import AboutDialog
from task_center.ui.gtk.main_window.settings_dialog import SettingsDialog
from task_center.ui.gtk.main_window.collections_sidebar import CollectionsSidebar
from task_center.ui.gtk.main_window.tasklist import Tasklist
from .task_sidebar.task_sidebar import TaskSidebar
# Todo, connect sources edit/delete dialog apply button signals to collection update method


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
        self.tasklist_box = self.gtk_builder.get_object("tasklist_box")
        self.task_pane = self.gtk_builder.get_object("task_pane")
        self.task_box = self.gtk_builder.get_object("task_box")

        # Setup Task Sidebar
        self.task_sidebar = TaskSidebar(self.core, self.task_box)

        # Setup TaskList
        self.tasklist = Tasklist(self.core, self.tasklist_box, self.task_sidebar)
        self.task_box = self.gtk_builder.get_object("task_box")

        # Setup Collections Sidebar
        self.collections_sidebar = CollectionsSidebar(
            self.core, self.sidebar_box, self.window, self.tasklist.load_collection)

        # self.tags = GtkTagSidebar

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
        self.task_pane.set_position(spinbutton.get_value())

    def _on_quit_button_clicked(self, _):
        self.popover.popdown()
        self.window.destroy()

    def _on_window_size_allocate(self, _window, _rectangle):
        self.sidebar_pane.set_position(self.core.settings_manager.get_setting("sidebar_pane_position"))
        if self.task_pane.get_child2().get_visible():
            self.task_pane.set_position(self.core.settings_manager.get_setting("task_pane_position"))
        else:
            self.task_pane.set_position(self.task_pane.props.max_position)
        self.core.settings_manager.set_setting("window_is_maximized", self.window.is_maximized())
        self.core.settings_manager.set_setting("window_size", self.window.get_size())
        self.core.settings_manager.save()

    def _on_sidebar_pane_position_notify(self, _pane, _position):
        self.sidebar_pane.set_position(self.core.settings_manager.get_setting("sidebar_pane_position"))

    def _on_task_pane_position_notify(self, _pane, _position):
        if _pane.get_child2().get_visible():
            self.task_pane.set_position(self.core.settings_manager.get_setting("task_pane_position"))
        else:
            self.task_pane.set_position(self.task_pane.props.max_position)

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