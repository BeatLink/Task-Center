# Imports ##############################################################################################################
import pathlib
import gi

from task_center.core.app import TaskCenterCore

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from task_center.ui.gtk.main_window.collections.edit_dialog.collection_edit_dialog import CollectionEditDialog
from task_center.ui.gtk.main_window.collections.delete_dialog.collection_delete_dialog import CollectionDeleteDialog
from task_center.ui.gtk.main_window.collections.sidebar_row.collection_sidebar_row import CollectionSidebarRow


class CollectionSidebar:
    def __init__(
            self,
            core: TaskCenterCore,
            source_id,
            edit_dialog: CollectionEditDialog,
            delete_dialog: CollectionDeleteDialog,
            tasklist):
        # Core Variables
        self.core = core
        self.source_id = source_id

        # Setup GTK Builder
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str(pathlib.Path(__file__).parent.resolve() / 'collection_sidebar.glade'))
        self.gtk_builder.connect_signals(self)

        # Widgets setup
        self.scrolled_window = self.gtk_builder.get_object("scrolled_window")
        self.box = self.gtk_builder.get_object('box')
        self.label = self.gtk_builder.get_object('label')
        self.label.set_text(self.core.tasks_manager.get_source(self.source_id).display_name)
        self.add_button = self.gtk_builder.get_object("add_button")
        self.listbox = self.gtk_builder.get_object("listbox")
        self.menu = self.gtk_builder.get_object("menu")
        self.rows = {}

        # External UI Elements
        self.edit_dialog = edit_dialog
        self.delete_dialog = delete_dialog
        self.tasklist = tasklist

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_heading_clicked(self, _, event_button):
        if event_button._button == 1:
            content_revealer = self.gtk_builder.get_object('revealer')
            add_button_revealer = self.gtk_builder.get_object('add_button_revealer')
            for revealer in content_revealer, add_button_revealer:
                revealer.set_reveal_child(not revealer.get_reveal_child())

    def _on_add_button_clicked(self, _):
        self.edit_dialog.open(self.source_id, None)

    def _on_listbox_row_activated(self, _listbox, listbox_row):
        self.refresh_taskview(listbox_row.id)

    def _on_listbox_button_press_event(self, _box, button, list_id):
        if button.button == 3:
            self.list_id = list_id
            self.menu.popup_at_pointer(None)

    def _on_update_menubutton_activate(self, _button):
        self.refresh_taskview(self.list_id)
        self.menu.popdown()

    def _on_edit_menubutton_activate(self, _button):
        self.edit_dialog.open(self.source_id, self.list_id)
        self.menu.popdown()

    def _on_delete_menubutton_activate(self, _button):
        self.delete_dialog.open(self.source_id, self.list_id)
        self.menu.popdown()

    def refresh_taskview(self, collection_id):
        all_tasks = self.core.tasks_manager.get_all_tasks(self.source_id, collection_id)
        task_list = {(self.source_id, collection_id, task_id): task for task_id, task in all_tasks.items()}
        self.tasklist.refresh_list(task_list)


    # Functions --------------------------------------------------------------------------------------------------------
    def add_collection_row(self, collection_id, collection):
        self.rows[collection_id] = CollectionSidebarRow()
        self.rows[collection_id].event_box.connect("button-press-event", self._on_listbox_button_press_event, collection_id)
        self.rows[collection_id].row.id = collection_id
        self.listbox.insert(self.rows[collection_id].row, -1)
        self.edit_collection_row(collection_id, collection)

    def edit_collection_row(self, collection_id, collection):
        if not collection.color:
            collection.color = "#000000"
        self.rows[collection_id].icon_label.set_markup(f'<span foreground="{collection.color}">⬤</span>')
        self.rows[collection_id].title_label.set_text(collection.name)

    def delete_collection_row(self, collection_id):
        self.listbox.remove(self.rows[collection_id].row)
        del self.rows[collection_id]

    # Functions --------------------------------------------------------------------------------------------------------
    def refresh_list(self, *_):
        for row_id in self.rows:
            self.listbox.remove(self.rows[row_id].row)
        self.rows = {}
        if self.core.tasks_manager.get_source(self.source_id).enabled:
            for id, collection in self.core.tasks_manager.get_all_collections(self.source_id):
                self.add_collection_row(id, collection)

    def start_refresh_timer(self):
        pass

class CollectionSidebarManager:
    def __init__(self, core: TaskCenterCore, task_list_view):
        self.core = core
        self.task_list_view = task_list_view

        # Setup task lists
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box.set_name("collections_box")
        self.box.show_all()
        self.edit_dialog = CollectionEditDialog(self.core, self)
        self.delete_dialog = CollectionDeleteDialog(self.core, self)

        self.sidebars = {}
        for source_id in self.core.tasks_manager.get_all_sources():
            self.sidebars[source_id] = CollectionSidebar(self.core, source_id, self.edit_dialog, self.delete_dialog, self.task_list_view)
            self.box.add(self.sidebars[source_id].box)
            self.box.set_child_packing(self.sidebars[source_id].box, False, False, 0, Gtk.PackType.START)
            self.sidebars[source_id].refresh_list()
