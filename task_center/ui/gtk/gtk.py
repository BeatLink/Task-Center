#!/usr/bin/env python3

# Imports ##############################################################################################################
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
from task_center.core.app import TaskCenterCore
from task_center.ui.gtk.main_window.main_window import MainWindow

# GtkApp ###############################################################################################################
class GtkApp(Gtk.Application):
    def __init__(self):
        # Core Setup
        self.core = TaskCenterCore()

        # GTK App Setup
        super().__init__(application_id="io.gitlab.task-center", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.on_activate)

        # Main Window Setup
        self.main_window = MainWindow(self.core)
        self.main_window.window.connect("destroy", Gtk.main_quit)

    def on_activate(self, _=None):
        self.add_window(self.main_window.window)
        self.main_window.open()
        Gtk.main()

    def on_shutdown(self):
        self.main_window.close()
        Gtk.main_quit()

    def launch(self):
        self.run()


def run_app():
    app = GtkApp()
    app.launch()
