class TestWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Formatted TextView Test Window")
        self.textview = FormatTextView()
        self.add(self.textview.box_widget)

win = TestWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
