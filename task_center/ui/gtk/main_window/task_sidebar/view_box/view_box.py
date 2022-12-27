# Imports ##############################################################################################################
import pathlib
import datetime
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from task_center.core.app import TaskCenterCore


# TaskView #############################################################################################################
class TaskViewBox:
    """
    This class contains the logic for the task editor dialog, which edits individual tasks.
    """
    def __init__(self, core: TaskCenterCore, task_sidebar):
        self.core = core
        self.task_sidebar = task_sidebar
        self.source_id = ""
        self.collection_id = ""
        self.task_id = ""
        self.done_date = None

        # GtkBuilder Setup
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str((pathlib.Path(__file__).parent / 'view_box.glade').resolve()))
        self.gtk_builder.connect_signals(self)
        self.box = self.gtk_builder.get_object("box")
        self.grid = self.gtk_builder.get_object('grid')
        self.title_data_label = self.gtk_builder.get_object("title_data_label")
        self.description_data_label = self.gtk_builder.get_object("description_data_label")
        self.collection_data_label = self.gtk_builder.get_object("collection_data_label")
        self.super_task_data_label = self.gtk_builder.get_object("super_task_data_label")
        self.start_date_data_label = self.gtk_builder.get_object("start_date_data_label")
        self.due_date_data_label = self.gtk_builder.get_object("due_date_data_label")
        self.recurrence_data_label = self.gtk_builder.get_object("recurrence_data_label")
        self.tags_data_label = self.gtk_builder.get_object("tags_data_label")
        self.edit_button = self.gtk_builder.get_object("edit_button")
        self.new_subtask_button = self.gtk_builder.get_object("new_subtask_button")
        self.mark_done_button = self.gtk_builder.get_object('mark_done_button')
        self.new_subtask_button = self.gtk_builder.get_object('new_subtask_button')

    # Handlers -------------------------------------------------------------------------------------------------


    def _on_mark_done_button_clicked(self, *_):
        self.__done_date = datetime.datetime.now()
        self._update_mark_done_buttons()

    def _on_mark_undone_button_clicked(self, *_):
        self.__done_date = None
        self._update_mark_done_buttons()

    def _on_super_task_data_label_activate_link(self, *_):
        if self.super_task_data_label.get_uri():
            self.task_sidebar.open(self.source_id, self.collection_id, self.super_task_data_label.get_uri())

    def _update_mark_done_buttons(self):
        self.mark_done_button.set_visible(not bool(self.done_date))
        self.mark_undone_button.set_visible(bool(self.done_date))

    # Saving methods ---------------------------------------------------------------------------------------------------
    def _create_subtask(self, *_):
        subtask = self.task.create_subtask()
        self.task_treestore_manager.update_task(subtask)

    # Functions --------------------------------------------------------------------------------------------------------
    def load_data(self, source_id, collection_id, task_id):
        self.source_id = source_id
        self.collection_id = collection_id
        self.task_id = task_id
        if self.task_id:
            task = self.core.tasks_manager.get_task(source_id, collection_id, task_id)
            collection = self.core.tasks_manager.get_collection(source_id, collection_id)
            self.title_data_label.set_text(task.summary)
            self.description_data_label.set_text(task.description)
            self.collection_data_label.set_markup(
                f'<span foreground="{collection.color}"> ⬤  </span><span>{collection.name}</span>')
            if task.parent:
                parent = self.core.tasks_manager.get_task(source_id, collection_id, task.parent)
                self.super_task_data_label.set_label(parent.summary)
                self.super_task_data_label.set_uri(task.parent)
            else:
                self.super_task_data_label.set_label("None")
                self.super_task_data_label.set_uri("")

            self.start_date_data_label.set_text(task.start_date.isoformat() if task.start_date else "No Start Date")
            self.due_date_data_label.set_text(task.due_date.isoformat() if task.due_date else "No Due Date")
            self.done_date = task.done_date
            self.tags_data_label.set_text(",".join(task.tags))
            # self.recurrence_data_label.set_text(task.recurrence)
            # self._update_mark_done_buttons()


