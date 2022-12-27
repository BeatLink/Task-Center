# Imports ##############################################################################################################
import pathlib
import datetime
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from task_center.core.app import TaskCenterCore
from task_center.core.tasks.models.task import Task
from .recurrence_button import RecurrenceButton
from .datetime_button import DateTimeButton


# TaskView #############################################################################################################
class TaskEditBox:
    """
    This class contains the logic for the task editor dialog, which edits individual tasks.
    """
    def __init__(self, core: TaskCenterCore, main_window_gtk_builder):

        """
        This class contains the logic for the task editor dialog, which edits individual tasks.
        """

        # if "task_pane_position" not in self.core.settings.settings_dict:
        #    self._on_task_pane_position_notify(None, 800)

        self.main_window_gtk_builder = main_window_gtk_builder
        self.core = core
        self.source_id = ""
        self.collection_id = ""
        self.task_id = ""
        self.done_date = None

        # GtkBuilder Setup
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'edit_box.glade').resolve()))
        self.gtk_builder.connect_signals(self)

        # Widget Setup
        self.box = self.gtk_builder.get_object("box")
        self.cancel_button = self.gtk_builder.get_object("cancel_button")
        self.save_button = self.gtk_builder.get_object("save_button")
        self.grid = self.gtk_builder.get_object('grid')
        self.title_entry = self.gtk_builder.get_object('title_entry')
        self.description_buffer = self.gtk_builder.get_object('description_textbuffer')
        self.start_date_button = DateTimeButton('%B %d, %Y', "%B %d, %Y at %H:%M", 'No Start Date')
        self.grid.attach(self.start_date_button._button, 1, 7, 1, 1)
        self.due_date_button = DateTimeButton('%B %d, %Y', "%B %d, %Y at %H:%M", 'No Due Date')
        self.grid.attach(self.due_date_button._button, 1, 8, 1, 1)
        self.recurrence_button = RecurrenceButton()
        self.grid.attach(self.recurrence_button.button, 1, 9, 1, 1)
        self.tags_entry = self.gtk_builder.get_object("tags_entry")
        self.mark_done_button = self.gtk_builder.get_object('mark_done_button')
        self.mark_undone_button = self.gtk_builder.get_object('mark_undone_button')
        self.delete_button = self.gtk_builder.get_object('delete_button')
        self.new_subtask_button = self.gtk_builder.get_object('new_subtask_button')


        #self._load_task_data()
        #self.connect_task_changed(self._save_task_data)
        #self.connect_new_subtask_button_signal(self._create_subtask)
        #self.connect_delete_button_signal(self._delete_task)
        #self.connect_task_changed(self._save_task_data)
        #self.connect_new_subtask_button_signal(self._create_subtask)
        #self.connect_delete_button_signal(self._delete_task)

        # if "task_pane_position" not in self.core.settings.settings_dict:
        #    self._on_task_pane_position_notify(None, 800)

        #self.subtasks_box = self.gtk_builder.get_object("subtasks_box")
        #self.subtasks_reveal_image = self.gtk_builder.get_object("subtask_reveal_image")
        #self.subtasks_reveal_image_eventbox = self.gtk_builder.get_object("subtask_reveal_image_eventbox")
        #self.subtasks_box_revealer = self.gtk_builder.get_object("subtasks_box_revealer")
        #self.subtasks_box_revealer.connect("notify::reveal-child", self._on_subtasks_box_revealer_changed)
       # self._on_subtasks_box_revealer_changed()

    # Handlers ---------------------------------------------------------------------------------------------------------
    def _on_save_button_clicked(self, _button):
        self.save_data()

    def _on_mark_done_button_clicked(self, *_):
        self.__done_date = datetime.now()
        self._update_mark_done_buttons()

    def _on_mark_undone_button_clicked(self, *_):
        self.__done_date = None
        self._update_mark_done_buttons()

    def _on_start_date_button_clicked(self, *_):
        self.start_date_popover.popup()

    def _on_due_date_button_clicked(self, *_):
        self.due_date_popover.popup()

    def _on_start_date_button_clicked(self, *_):
        self.start_date_popover.popup()

    def _on_due_date_button_clicked(self, *_):
        self.due_date_popover.popup()

    def _on_start_date_popover_closed(self, *_):
        if self.start_date_popover.get_datetime():
            hour = self.start_date_popover._minute_spinbox.get_value_as_int()
            minute = self.start_date_popover._minute_spinbox.get_value_as_int()
            format_string = '%Y-%m-%d at %H:%M' if (hour or minute) else '%Y-%m-%d'
            final_date_string = self.start_date_popover.get_datetime().strftime(format_string)
            self.start_date_button.set_label(final_date_string)
        else:
            self.start_date_button.set_label('No Start Date')

    def _on_start_date_popover_closed(self, *_):
        if self.start_date_popover.get_datetime():
            hour = self.start_date_popover._minute_spinbox.get_value_as_int()
            minute = self.start_date_popover._minute_spinbox.get_value_as_int()
            format_string = '%Y-%m-%d at %H:%M' if (hour or minute) else '%Y-%m-%d'
            final_date_string = self.start_date_popover.get_datetime().strftime(format_string)
            self.start_date_button.set_label(final_date_string)
        else:
            self.start_date_button.set_label('No Start Date')


    def _on_subtasks_box_add(self, *_):
        self.subtasks_reveal_image.set_opacity(1.0)
        self.subtasks_reveal_image.set_sensitive(True)

    def _on_subtask_reveal_image_eventbox_button_press_event(self, _eventbox, _buttonpress):
        opposite_reveal = not self.subtasks_box_revealer.get_reveal_child()
        self.subtasks_box_revealer.set_reveal_child(opposite_reveal)

    def _on_subtasks_box_revealer_changed(self, *_):
        reveal = self.subtasks_box_revealer.get_reveal_child()
        self.subtasks_reveal_image.set_from_icon_name(
            "pan-down-symbolic" if reveal else "pan-end-symbolic", Gtk.IconSize.SMALL_TOOLBAR)

    # Functions --------------------------------------------------------------------------------------------------------


    # Updating Methods -------------------------------------------------------------------------------------------------
    def _update_mark_done_buttons(self):
        self.mark_done_button.set_visible(not bool(self.done_date))
        self.mark_undone_button.set_visible(bool(self.done_date))

    # Changed signal connector -----------------------------------------------------------------------------------------
    def connect_task_changed(self, function):
        self.title_entry.connect('changed', function)
        self.note_buffer.connect('changed', function)
        self.start_date_picker.picker.connect_datetime_changed_signal(function)
        self.due_date_picker.picker.connect_datetime_changed_signal(function)
        self.mark_done_button.connect('clicked', function)
        self.mark_undone_button.connect('clicked', function)
        #self._recurrence_picker.popover.connect_recurrence_changed_signal(function)

    def connect_delete_button_signal(self, function):
        self.delete_button.connect('clicked', function)
    # Changed signal connector -----------------------------------------------------------------------------------------
    def connect_task_changed(self, function):
        self.title_entry.connect('changed', function)
        self.note_buffer.connect('changed', function)
        self.start_date_picker.picker.connect_datetime_changed_signal(function)
        self.due_date_picker.picker.connect_datetime_changed_signal(function)
        self.mark_done_button.connect('clicked', function)
        self.mark_undone_button.connect('clicked', function)
        #self._recurrence_picker.popover.connect_recurrence_changed_signal(function)

    def connect_delete_button_signal(self, function):
        self.delete_button.connect('clicked', function)

    def connect_new_subtask_button_signal(self, function):
        self.new_subtask_button.connect('clicked', function)
    # Saving methods ---------------------------------------------------------------------------------------------------
    def initialize(self):
        pass

    def _create_subtask(self, *_):
        subtask = self.task.create_subtask()
        self.task_treestore_manager.update_task(subtask)


    def load_data(self, source_id, collection_id, task_id=None):
        self.source_id = source_id
        self.collection_id = collection_id
        self.task_id = task_id
        if self.task_id:
            task = self.core.tasks_manager.get_task(self.source_id, self.collection_id, self.task_id)
            self.title_entry.set_text(task.summary)
            self.description_buffer.set_text(task.description)
            self.start_date_button.set_datetime(task.start_date)
            self.due_date_button.set_datetime(task.due_date)
            self.done_date = task.done_date
            self.tags_entry.set_text(",".join(task.tags))
            #self._update_mark_done_buttons()
            #self.recurrence_button.set_data(task.recurrence)

    def save_data(self, *_):
        task = Task()
        task.summary = self.title_entry.get_text()
        task.notes = self.description_buffer.get_text(
            self.description_buffer.get_start_iter(), self.description_buffer.get_end_iter(), True)
        task.start_date = self.start_date_button.get_datetime()
        task.due_date = self.due_date_button.get_datetime()
        task.done_date = self.done_date
        task.tags = self.tags_entry.get_text().split(",")
        #task.recurrence = self.recurrence_button.get_data()
        self.core.tasks_manager.update_task(self.source_id, self.collection_id, self.task_id, task)
        #self.task_treestore_manager.update_task(self.task)

    def save_data2(self, *_):
        task = Task()
        task.title = self.title_entry.get_text()
        task.notes = self.description_buffer.get_text(
            self.description_buffer.get_start_iter(), self.description_buffer.get_end_iter(), True)
        task.start_date = self.start_date_button.get_datetime()
        task.due_date = self.due_date_button.get_datetime()
        task.done_date = self.done_date
        task.recurrence = self.recurrence_button.get_data()
        #self.task_treestore_manager.update_task(self.task)
