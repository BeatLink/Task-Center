# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# List Row #############################################################################################################
class CollectionSidebarRow:
    def __init__(self):
        gtk_builder = Gtk.Builder()
        gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'collection_sidebar_row.glade').resolve()))
        self.event_box = gtk_builder.get_object('event_box')
        self.box = gtk_builder.get_object("box")
        self.icon_label = gtk_builder.get_object("icon_label")
        self.title_label = gtk_builder.get_object("title_label")
        self.row = Gtk.ListBoxRow()
        self.row.add(self.event_box)
        self.row.show_all()