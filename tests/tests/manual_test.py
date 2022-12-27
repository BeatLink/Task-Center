import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from recurrence_popover.recurrence_popover import RecurrenceButton

button = RecurrenceButton()
box = Gtk.Grid()
box.add(button._button)
box.show()
window = Gtk.Window()
window.add(box)
window.show()
Gtk.main()