# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from .collection_list_row import CollectionListRow


# Collection Sidebar ###################################################################################################
class CollectionList:
    def __init__(self, core, source_id, edit_dialog, delete_dialog):
        # Internal Variables
        self.core = core
        self.source_id = source_id
        self.selected_collection_id = None

        # Setup GTK Builder
        self._gtk_builder = Gtk.Builder()
        self._gtk_builder.add_from_file(str(pathlib.Path(__file__).parent.resolve() / 'collection_list.glade'))
        self._gtk_builder.connect_signals(self)

        # Widgets setup
        self.scrolled_window = self._gtk_builder.get_object("scrolled_window")
        self.box = self._gtk_builder.get_object('box')
        self.label = self._gtk_builder.get_object('label')
        self.add_button = self._gtk_builder.get_object("add_button")
        self.listbox = self._gtk_builder.get_object("listbox")
        self.menu = self._gtk_builder.get_object("menu")
        self.update_menubutton = self._gtk_builder.get_object("update_menubutton")
        self.edit_menubutton = self._gtk_builder.get_object("edit_menubutton")
        self.delete_menubutton = self._gtk_builder.get_object("delete_menubutton")
        self.rows = {}
        self.edit_dialog = edit_dialog
        self.edit_dialog.save_button.connect('clicked', self._on_edit_dialog_save_button_clicked)
        self.delete_dialog = delete_dialog
        self.delete_dialog.delete_button.connect("clicked", self._on_delete_dialog_delete_button_clicked)

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_heading_clicked(self, _, event_button):
        if event_button.button == 1:
            content_revealer = self._gtk_builder.get_object('revealer')
            add_button_revealer = self._gtk_builder.get_object('add_button_revealer')
            for revealer in content_revealer, add_button_revealer:
                revealer.set_reveal_child(not revealer.get_reveal_child())

    def _on_add_button_clicked(self, _button):
        self.edit_dialog.open(self.source_id, None)

    def _on_collection_right_clicked(self, _box, button, collection_id):
        if button.button == 3:
            self.selected_collection_id = collection_id
            self.menu.popup_at_pointer(None)

    def _on_listbox_row_activated(self, _listbox, listbox_row):
        self.selected_collection_id = listbox_row.id

    def _on_update_menubutton_activate(self, _button):
        self.menu.popdown()

    def _on_edit_menubutton_activate(self, _button):
        self.edit_dialog.open(self.source_id, self.selected_collection_id)
        self.menu.popdown()

    def _on_delete_menubutton_activate(self, _button):
        self.delete_dialog.open(self.source_id, self.selected_collection_id)
        self.menu.popdown()

    def _on_edit_dialog_save_button_clicked(self, _button):
        self.refresh_list(self.source_id)

    def _on_delete_dialog_delete_button_clicked(self, _button):
        self.refresh_list(self.source_id)

    # Functions --------------------------------------------------------------------------------------------------------
    def refresh_list(self, source_id):
        for collection_id in self.rows:
            self.listbox.remove(self.rows[collection_id].row)
        self.rows = {}
        self.source_id = source_id
        self.selected_collection_id = None
        source = self.core.tasks_manager.get_source(source_id)
        if source.enabled:
            self.label.set_text(source.display_name)
            collections = self.core.tasks_manager.get_all_collections(source_id)
            if collections:
                for collection_id, collection in collections:
                    self.rows[collection_id] = CollectionListRow()
                    self.rows[collection_id].event_box.connect(
                        "button-press-event", self._on_collection_right_clicked, collection_id)
                    self.rows[collection_id].row.id = collection_id
                    self.listbox.insert(self.rows[collection_id].row, -1)
                    collection.color = "#000000" if not collection.color else collection.color
                    self.rows[collection_id].icon_label.set_markup(f'<span foreground="{collection.color}">⬤</span>')
                    self.rows[collection_id].title_label.set_text(collection.name)
