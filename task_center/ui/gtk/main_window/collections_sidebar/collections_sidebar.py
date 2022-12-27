# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from .collection_list import CollectionList
from .edit_dialog import CollectionEditDialog
from .delete_dialog import CollectionDeleteDialog


# Collections Sidebar ##################################################################################################
class CollectionsSidebar:
    def __init__(self, core, parent_box, main_window, update_function):
        # Internal Variables
        self.core = core
        self.update_function = update_function
        # Setup GTK Builder
        self._gtk_builder = Gtk.Builder()
        self._gtk_builder.add_from_file(str(pathlib.Path(__file__).parent.resolve() / 'collections_sidebar.glade'))
        self._gtk_builder.connect_signals(self)
        self.box = self._gtk_builder.get_object("collections_box")
        self.delete_dialog = CollectionDeleteDialog(self.core)
        self.edit_dialog = CollectionEditDialog(self.core)
        parent_box.add(self.box)
        parent_box.set_child_packing(self.box, True, True, 0, Gtk.PackType.START)
        self.collection_sidebars = {}
        for source_id in self.core.tasks_manager.get_all_sources():
            sidebar = CollectionList(self.core, source_id, self.edit_dialog, self.delete_dialog)
            sidebar.refresh_list(source_id)
            sidebar.listbox.connect("row-activated", self._on_sidebar_listbox_row_activated, source_id)
            sidebar.update_menubutton.connect("activate", self._on_update_menubutton_activate, source_id)
            sidebar.edit_dialog.dialog.set_transient_for(main_window)
            sidebar.delete_dialog.dialog.set_transient_for(main_window)
            self.box.add(sidebar.box)
            self.box.set_child_packing(sidebar.box, False, False, 0, Gtk.PackType.START)
            self.collection_sidebars[source_id] = sidebar

    def _on_sidebar_listbox_row_activated(self, _listbox, _listbox_row, source_id):
        sidebar = self.collection_sidebars[source_id]
        collection_id = sidebar.selected_collection_id
        self.update_function(source_id, collection_id)

    def _on_update_menubutton_activate(self, _menubutton, source_id):
        sidebar = self.collection_sidebars[source_id]
        collection_id = sidebar.selected_collection_id
        self.update_function(source_id, collection_id)
