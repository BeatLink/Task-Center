import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from xtasks.app.ui.gtk.datetime_popover import DateTimeButton

button = DateTimeButton()
button._button.show()

box = Gtk.Box()
box.pack_end(button._button, False, False, 0)
box.show()

window = Gtk.Window()
window.add(box)
window.show()

Gtk.main()
