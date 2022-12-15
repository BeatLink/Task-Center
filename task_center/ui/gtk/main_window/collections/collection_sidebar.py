# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from task_center.ui.gtk.main_window.collections.edit_dialog.collection_edit_dialog import CollectionEditDialog
from task_center.ui.gtk.main_window.collections.delete_dialog.collection_delete_dialog import CollectionDeleteDialog
from task_center.ui.gtk.main_window.collections.sidebar_row.collection_sidebar_row import CollectionSidebarRow


class CollectionSidebar:
    def __init__(self, core, source_id, edit_dialog, delete_dialog, tasklistview):
        # Core Variables
        self.core = core
        self.source_id = source_id
        self.tasklistview = tasklistview

        # Setup GTK Builder
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str(pathlib.Path(__file__).parent.resolve() / 'collection_sidebar.glade'))
        self.gtk_builder.connect_signals(self)

        # Widgets setup
        self.scrolled_window = self.gtk_builder.get_object("scrolled_window")
        self.box = self.gtk_builder.get_object('box')
        self.label = self.gtk_builder.get_object('label')
        self.label.set_text(self.core.sources.list[self.source_id].display_name)
        self.add_button = self.gtk_builder.get_object("add_button")
        self.listbox = self.gtk_builder.get_object("listbox")
        self.menu = self.gtk_builder.get_object("menu")
        self.rows = {}

        # External UI Elements
        self.edit_dialog = edit_dialog
        self.delete_dialog = delete_dialog

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_heading_clicked(self, _, event_button):
        if event_button.button == 1:
            content_revealer = self.gtk_builder.get_object('revealer')
            add_button_revealer = self.gtk_builder.get_object('add_button_revealer')
            for revealer in content_revealer, add_button_revealer:
                revealer.set_reveal_child(not revealer.get_reveal_child())

    def _on_add_button_clicked(self, _):
        self.edit_dialog.open(self.source_id, None)

    def _on_listbox_row_activated(self, _listbox, listbox_row):
        self.tasklistview.refresh_list(self.source_id, listbox_row.id)

    def _on_listbox_button_press_event(self, box, button, list_id):
        if button.button == 3:
            self.list_id = list_id
            self.menu.popup_at_pointer(None)

    def _on_update_menubutton_activate(self, _button):
        self.tasklistview.refresh_list(self.source_id, self.list_id)
        self.menu.popdown()

    def _on_edit_menubutton_activate(self, _button):
        self.edit_dialog.open(self.source_id, self.list_id)
        self.menu.popdown()

    def _on_delete_menubutton_activate(self, _button):
        self.delete_dialog.open(self.source_id, self.list_id)
        self.menu.popdown()

    # Functions --------------------------------------------------------------------------------------------------------
    def refresh_list(self, *_):
        for row_id in self.rows:
            self.listbox.remove(self.rows[row_id].row)
        self.rows = {}
        source = self.core.sources.list[self.source_id]
        if source.enabled:
            collections = source.get_all_collections()
            if collections:
                for id, collection in sorted(collections.items(), key=lambda collection: collection[1].name):
                    self.add_collection(id, collection)

    # Functions --------------------------------------------------------------------------------------------------------
    def add_collection(self, id, tasklist):
        self.rows[id] = CollectionSidebarRow()
        self.rows[id].event_box.connect("button-press-event", self._on_listbox_button_press_event, id)
        self.rows[id].row.id = id
        self.listbox.insert(self.rows[id].row, -1)
        self.edit_collection(id, tasklist)

    def edit_collection(self, id, tasklist):
        if not tasklist.color:
            tasklist.color = "#000000"
        self.rows[id].icon_label.set_markup(f'<span foreground="{tasklist.color}">⬤</span>')
        self.rows[id].title_label.set_text(tasklist.name)

    def delete_collection(self, id):
        self.listbox.remove(self.rows[id].row)
        del self.rows[id]

    def start_refresh_timer(self):
        pass

class CollectionSidebarManager:
    def __init__(self, core, task_list_view):
        self.core = core
        self.task_list_view = task_list_view

        # Setup task lists
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box.set_name("collections_box")
        self.box.show_all()
        self.edit_dialog = CollectionEditDialog(self.core, self)
        self.delete_dialog = CollectionDeleteDialog(self.core, self)

        self.sidebars = {}
        for source_id in self.core.sources.list:
            self.sidebars[source_id] = CollectionSidebar(self.core, source_id, self.edit_dialog, self.delete_dialog, self.task_list_view)
            self.box.add(self.sidebars[source_id].box)
            self.box.set_child_packing(self.sidebars[source_id].box, True, True, 0, Gtk.PackType.START)
            self.sidebars[source_id].refresh_list()
