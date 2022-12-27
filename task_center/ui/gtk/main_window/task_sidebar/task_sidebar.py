#!/usr/bin/env python3
"""
# TODO: Setup task retrieval with async
"""
# Imports ##############################################################################################################
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from task_center.core.app import TaskCenterCore
from .view_box import TaskViewBox
from .edit_box import TaskEditBox


# Task Pane ############################################################################################################
class TaskSidebar:
    def __init__(self, core: TaskCenterCore, parent_box):
        # Setup internal variables
        self.core = core
        self.parent_box = parent_box
        self.source_id = None
        self.collection_id = None
        self.task_id = None

        # Setup GTK Builder
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str(pathlib.Path(__file__).parent.resolve() / 'task_sidebar.glade'))
        self.gtk_builder.connect_signals(self)
        self.stack = self.gtk_builder.get_object("stack")
        self.view_box = self.gtk_builder.get_object("view_box")
        self.edit_box = self.gtk_builder.get_object("edit_box")
        self.parent_box.add(self.stack)
        self.parent_box.set_child_packing(self.stack, True, True, 0, Gtk.PackType.START)

        # Setup Task View Pane
        self.task_view_box = TaskViewBox(self.core, self)
        self.task_view_box.edit_button.connect("clicked", self._on_task_view_box_edit_task_button_clicked)
        self.view_box.add(self.task_view_box.box)
        self.view_box.set_child_packing(self.task_view_box.box, True, True, 0, Gtk.PackType.START)

        # Setup Task Edit Pane
        self.task_edit_box = TaskEditBox(self.core, self)
        self.task_edit_box.cancel_button.connect("clicked", self._on_task_edit_box_cancel_button_clicked)
        self.edit_box.add(self.task_edit_box.box)
        self.task_edit_box.save_button.connect("clicked", self._on_task_edit_box_save_button_clicked)
        self.edit_box.set_child_packing(self.task_edit_box.box, True, True, 0, Gtk.PackType.START)

    def _on_task_view_box_edit_task_button_clicked(self, _button):
        self.open(self.source_id, self.collection_id, self.task_id, True)

    def _on_task_edit_box_cancel_button_clicked(self, _button):
        self.open(self.source_id, self.collection_id, self.task_id, False)

    def _on_task_edit_box_save_button_clicked(self, _button):
        self.open(self.source_id, self.collection_id, self.task_id, False)

    def open(self, source_id, collection_id, task_id, edit_mode=False):
        self.source_id = source_id
        self.collection_id = collection_id
        self.task_id = task_id
        self.parent_box.set_visible(True)
        if edit_mode:
            self.stack.set_visible_child_name("edit")
            self.task_edit_box.load_data(self.source_id, self.collection_id, self.task_id)
        else:
            self.stack.set_visible_child_name("view")
            self.task_view_box.load_data(self.source_id, self.collection_id, self.task_id)

    def close(self):
        self.parent_box.set_visible(False)