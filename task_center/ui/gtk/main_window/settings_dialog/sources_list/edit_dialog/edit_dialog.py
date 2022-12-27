# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from task_center.core.app import TaskCenterCore
from task_center.core.tasks.sources import SOURCES


# Edit Dialog ##########################################################################################################
class SourceEditDialog:
    def __init__(self, core: TaskCenterCore):
        # Settings Setup
        self.core = core
        self.source_id = ""

        # GtkBuilder Setup
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'edit_dialog.glade').resolve()))
        self.gtk_builder.connect_signals(self)

        # Widgets Setup
        self.dialog = self.gtk_builder.get_object('dialog')
        self.save_button = self.gtk_builder.get_object("save_button")
        self.headerbar = self.gtk_builder.get_object("headerbar")
        self.grid = self.gtk_builder.get_object("grid")
        self.enabled_switch = self.gtk_builder.get_object("enabled_switch")
        self.name_entry = self.gtk_builder.get_object("name_entry")
        self.type_combobox = self.gtk_builder.get_object("type_combobox")
        self.type_label = self.gtk_builder.get_object("type_label")
        self.type_stack = self.gtk_builder.get_object("type_stack")
        self.decsync_filechooser_box = self.gtk_builder.get_object("decsync_filechooser_box")
        self.decsync_filechooser_button = self.gtk_builder.get_object("decsync_filechooser_button")
        self.decsync_filechooser_clear_button = self.gtk_builder.get_object("decsync_filechooser_clear_button")
        self.caldav_url_entry = self.gtk_builder.get_object("caldav_url_entry")
        self.caldav_username_entry = self.gtk_builder.get_object("caldav_username_entry")
        self.caldav_password_entry = self.gtk_builder.get_object("caldav_password_entry")
        self.caldav_self_signed_cert_switch = self.gtk_builder.get_object("caldav_self_signed_cert_switch")

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_cancel_button_clicked(self, *_):
        self.dialog.hide()

    def _on_save_button_clicked(self, _button):
        self._save_settings()
        self.dialog.hide()

    def _on_type_combobox_changed(self, _combobox):
        id = self.type_combobox.get_active_id()
        self.type_stack.set_visible_child_name(id)

    def _on_decsync_filechooser_button_file_set(self, *_):
        if self.decsync_filechooser_button.get_uri():
            self.decsync_filechooser_clear_button.set_visible(True)

    def _on_decsync_filechooser_clear_button_clicked(self, *_):
        self.decsync_filechooser_button.unselect_all()
        self.decsync_filechooser_clear_button.set_visible(False)

    # Internal functions -----------------------------------------------------------------------------------------------
    def _save_settings(self):
        source_type = self.type_combobox.get_active_id()
        if not self.source_id:
            source = SOURCES[source_type]()
            self.source_id = self.core.tasks_manager.create_source(source)
        else:
            source = self.core.tasks_manager.get_source(self.source_id)
        source.enabled = self.enabled_switch.get_active()
        source.display_name = self.name_entry.get_text()
        if source_type == "caldav":
            source.url = self.caldav_url_entry.get_text()
            source.username = self.caldav_username_entry.get_text()
            source.password = self.caldav_password_entry.get_text()
            source.self_signed_cert = self.caldav_self_signed_cert_switch.get_active()
        elif source_type == "decsync":
            path = self.decsync_filechooser_button.get_uri() if self.decsync_filechooser_button.get_uri() else ""
            path = path.replace("file://", "")
            source.decsync_dir = path
        self.core.tasks_manager.update_source(self.source_id, source)

    def _initialize(self):
        self.enabled_switch.set_active(False)
        self.name_entry.set_text("")
        self.type_combobox.set_active_id("caldav")
        self.caldav_url_entry.set_text("")
        self.caldav_username_entry.set_text("")
        self.caldav_password_entry.set_text("")
        self.decsync_filechooser_button.unselect_all()
        self.decsync_filechooser_clear_button.set_visible(False)
        self.headerbar.set_title("Adding Backends")

    def _load_settings(self):
        source = self.core.tasks_manager.get_source(self.source_id)
        self.enabled_switch.set_active(source.enabled)
        self.name_entry.set_text(source.display_name)
        self.headerbar.set_title(f"Editing {source.display_name}")
        self.type_combobox.set_active_id(source.type)
        if source.type == "caldav":
            self.caldav_url_entry.set_text(source.url)
            self.caldav_username_entry.set_text(source.username)
            self.caldav_password_entry.set_text(source.password)
            self.caldav_self_signed_cert_switch.set_active(source.self_signed_cert)
        elif source.type == "decsync":
            path = source.decsync_dir
            if path:
                self.decsync_filechooser_button.set_uri(f"file://{path}")
                self.decsync_filechooser_clear_button.set_visible(True)
            else:
                self.decsync_filechooser_button.unselect_all()
                self.decsync_filechooser_clear_button.set_visible(False)

    # Functions --------------------------------------------------------------------------------------------------------
    def open(self, source_id=None):
        self.source_id = source_id
        if self.source_id:
            self._load_settings()
        else:
            self._initialize()
        self.dialog.show_now()
