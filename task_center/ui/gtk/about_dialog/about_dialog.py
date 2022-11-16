# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf


# GtkAboutDialog #######################################################################################################
class AboutDialog:
    def __init__(self, app_info):
        # AppInfo
        self.app_info = app_info

        # GtkBuilder Setup
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'about_dialog.glade').resolve()))
        self.gtk_builder.connect_signals(self)

        # Dialog Setup
        self.dialog = self.gtk_builder.get_object('dialog')
        self.dialog.set_program_name(self.app_info.name)
        self.dialog.set_version(self.app_info.version)
        self.dialog.set_comments(self.app_info.description)
        self.dialog.set_copyright(self.app_info.copyright)
        self.dialog.set_website(self.app_info.homepage)
        self.dialog.set_authors([self.app_info.author_name])
        self.dialog.set_logo(GdkPixbuf.Pixbuf().new_from_file_at_size(self.app_info.icon_file_path, 128, 128))
        self.dialog.set_license_type(Gtk.License.GPL_3_0)

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_dialog_response(self, _dialog, response):
        if response == Gtk.ResponseType.DELETE_EVENT:
            self.dialog.hide()

    # Functions --------------------------------------------------------------------------------------------------------
    def open(self):
        self.dialog.show_now()
