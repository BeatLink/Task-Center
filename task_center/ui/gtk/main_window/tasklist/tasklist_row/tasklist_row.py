# Imports ##############################################################################################################
import pathlib
import arrow
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


# TasklistRow ##########################################################################################################
class TasklistRow:
    def __init__(self, task_id, task):
        self.id = task_id
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'tasklist_row.glade').resolve()))
        self.gtk_builder.connect_signals(self)
        self.box = self.gtk_builder.get_object("box")
        self.listbox = self.gtk_builder.get_object('listbox')
        self.listbox_row = self.gtk_builder.get_object('listbox_row')
        self.dnd_eventbox = self.gtk_builder.get_object("dnd_eventbox")
        self.dnd_eventbox.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.MOVE)
        self.dnd_eventbox.drag_source_add_text_targets()
        self.dnd_eventbox.drag_source_set_icon_name('document')
        self.dnd_eventbox.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.MOVE)
        self.dnd_eventbox.drag_dest_add_text_targets()
        self.title_label = self.gtk_builder.get_object("title_label")
        self.title_label.set_text(task.summary)
        self.start_date_label = self.gtk_builder.get_object("start_date_label")
        self.start_date_label.set_text(f"Starts {arrow.get(task.start_date).humanize()}" if task.start_date else "")
        self.due_date_label = self.gtk_builder.get_object("due_date_label")
        self.due_date_label.set_text(f"Due {arrow.get(task.due_date).humanize()}" if task.due_date else "")
        self.tags_label = self.gtk_builder.get_object("tags_label")
        self.tags_label.set_text(",".join(task.tags))
        self.subtasks_box = self.gtk_builder.get_object("subtasks_box")
        self.subtasks_reveal_image = self.gtk_builder.get_object("subtask_reveal_image")
        self.subtasks_reveal_image_eventbox = self.gtk_builder.get_object("subtask_reveal_eventbox")
        self.subtasks_box_revealer = self.gtk_builder.get_object("subtasks_revealer")
        self.subtasks_box_revealer.connect("notify::reveal-child", self._on_subtasks_box_revealer_changed)
        self._on_subtasks_box_revealer_changed()

    def _on_subtasks_box_changed(self, *_):
        if len(self.subtasks_box.get_children()) > 0:
            self.subtasks_reveal_image.set_opacity(1)
            self.subtasks_reveal_image.set_sensitive(True)
        else:
            self.subtasks_reveal_image.set_opacity(0)
            self.subtasks_reveal_image.set_sensitive(False)

    def _on_subtask_reveal_image_eventbox_button_press_event(self, _eventbox, _buttonpress):
        opposite_reveal = not self.subtasks_box_revealer.get_reveal_child()
        self.subtasks_box_revealer.set_reveal_child(opposite_reveal)

    def _on_subtasks_box_revealer_changed(self, *_):
        reveal = self.subtasks_box_revealer.get_reveal_child()
        self.subtasks_reveal_image.set_from_icon_name(
            "pan-down-symbolic" if reveal else "pan-end-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
