#!/usr/bin/env python3
"""
# TODO: Setup task retrieval with async
"""
# Imports ##############################################################################################################
import pathlib
import arrow
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from task_center.core.app import TaskCenterCore
from task_center.ui.gtk.main_window.tasklist.tasklist_row.tasklist_row import TasklistRow
from task_center.ui.gtk.main_window.task_sidebar.task_sidebar import TaskSidebar


# Task Treeview ########################################################################################################
class Tasklist:
    def __init__(self, core: TaskCenterCore, parent_box, task_sidebar: TaskSidebar):
        # Setup internal variables
        self.core = core
        self.all_tasks = {}
        self.selected_task = ""
        self.selected_collection = None
        self.sort_mode = "title"
        self.sort_order = "ascending"

        # Setup GTK Builder
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(str(pathlib.Path(__file__).parent.resolve() / 'tasklist.glade'))
        self.gtk_builder.connect_signals(self)
        self.box = self.gtk_builder.get_object('box')
        parent_box.add(self.box)
        parent_box.set_child_packing(self.box, True, True, 0, Gtk.PackType.START)
        self.stack = self.gtk_builder.get_object("stack")
        self.tasks_box = self.gtk_builder.get_object("tasks_box")
        self.eventbox = self.gtk_builder.get_object("eventbox")
        self.eventbox.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.MOVE)
        self.eventbox.drag_dest_add_text_targets()
        self.eventbox.connect("drag-data-received", self._on_drag_data_received, None)
        self.context_menu = self.gtk_builder.get_object("menu")
        self.rows = {}
        self.task_sidebar = task_sidebar
        self.subtasks_revealed_state = self.core.settings_manager.get_setting("subtask_reveal_state")
        if not self.subtasks_revealed_state:
            self.subtasks_revealed_state = {}

        # Setup CSS
        css = b""".task-view-background { background: white; }"""
        # noinspection PyArgumentList
        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        provider.load_from_data(css)

    # Event Handlers ---------------------------------------------------------------------------------------------------
    def _on_new_task_button_clicked(self, _button):
        self.task_sidebar.open(self.source_id, self.collection_id, None, True)

    def _on_listbox_row_activated(self, _listbox, _row, task_uid):
        if self.selected_task and self.selected_task != task_uid:
            self.rows[self.selected_task].listbox.unselect_all()
        self.selected_task = task_uid
        self.task_sidebar.open(*task_uid, False)

    def _on_listbox_button_press_event(self, box, button, task_uid):
        if button.button == 3:
            self.context_menu.task_uid = task_uid
            self.context_menu.popup_at_pointer(None)

    def _on_menu_view_task_button_activate(self, _menu):

        self.task_sidebar.open(*self.context_menu.task_uid, False)

    def _on_menu_new_subtask_button_activate(self, *_):
        pass

    def _on_menu_edit_button_activate(self, task_uid):
        self.task_sidebar.open(*task_uid, True)

    def _on_menu_delete_button_activate(self, *_):
        pass
        #for subtask_id in self.get_subtasks(source_id, collection_id, task_id):
        #    self.delete_task_and_subtasks(source_id, collection_id, subtask_id)
        #pass
        #self.task_editor.close_dialog()
        #self.task.delete()
        #self.task_treestore_manager.update_task(self.task)

    @staticmethod
    def _on_drag_data_get(_widget, _drag_context, data, _info, _time, drag_uid):
        data.set_text("###".join(drag_uid), -1)

    def _on_drag_data_received(self, _widget, _drag_context, _x, _y, data, _info, _time, drop_id):
        def get_task_parents(source_id, collection_id, task_id):
            parents = []
            task = self.all_tasks[(source_id, collection_id, task_id)]
            if task.parent:
                parents += task.parent
                parents += get_task_parents(source_id, collection_id, task.parent)
            return parents
        drag_id = tuple(data.get_text().split("###"))
        if drag_id == drop_id:
            return
        if drop_id:
            if drag_id in get_task_parents(drop_id[0], drop_id[1], drop_id[2]):
                return
        child = self.core.tasks_manager.get_task(drag_id[0], drag_id[1], drag_id[2])
        child.parent = drop_id[2] if drop_id else None
        self.core.tasks_manager.update_task(*drag_id, child)
        self.all_tasks[drag_id].parent = drop_id[2] if drop_id else ""
        self.delete_row(drag_id)
        self.create_row(drag_id)

    def _on_subtasks_box_revealer_changed(self, _revealer, reveal_child, task_uid):
        self.subtasks_revealed_state[task_uid[0]][task_uid[1]][task_uid[2]] = _revealer.get_reveal_child()
        self.core.settings_manager.set_setting("subtask_reveal_state", self.subtasks_revealed_state)

    # Internal functions -----------------------------------------------------------------------------------------------
    def create_row(self, task_uid):
        task = self.all_tasks[task_uid]
        row = TasklistRow(task_uid, task)
        row.subtasks_box_revealer.connect("notify::reveal-child", self._on_subtasks_box_revealer_changed, task_uid)
        row.dnd_eventbox.connect("drag-data-get", self._on_drag_data_get, task_uid)
        row.dnd_eventbox.connect("drag-data-received", self._on_drag_data_received, task_uid)
        row.listbox.connect("row-activated", self._on_listbox_row_activated, task_uid)
        row.listbox.connect("button-press-event", self._on_listbox_button_press_event, task_uid)
        self.load_subtask_revealed_state(task_uid)
        row.subtasks_box_revealer.set_reveal_child(self.subtasks_revealed_state[task_uid[0]][task_uid[1]][task_uid[2]])
        self.rows[task_uid] = row
        parent_row = (task_uid[0], task_uid[1], task.parent)
        if parent_row in self.rows:
            self.rows[parent_row].subtasks_box.add(row.box)
        else:
            self.tasks_box.add(row.box)
        subtasks = {id: task for id, task in self.all_tasks.items() if task.parent == task_uid[2]}
        for subtask_id in subtasks:
            self.create_row(subtask_id)

    def delete_row(self, task_uid):
        self.rows[task_uid].box.props.parent.remove(self.rows[task_uid].box)
        del self.rows[task_uid]

    def clear_rows(self):
        for widget in self.tasks_box.get_children():
            self.tasks_box.remove(widget)
        self.rows = {}
        self.selected_task = ""

    # Functions --------------------------------------------------------------------------------------------------------
    def load_collection(self, source_id, collection_id):
        self.stack.set_visible_child_name("loading_page")
        self.task_sidebar.close()
        self.clear_rows()
        all_tasks = {
            (source_id, collection_id, task_id): task
            for task_id, task in self.core.tasks_manager.get_collection_tasks(source_id, collection_id).items()
        }
        self.all_tasks = {id: task for id, task in sorted(all_tasks.items(), key=self.sort_tasks)}
        root_tasks = {
            task_uid: task
            for task_uid, task in self.all_tasks.items()
            if (not task.parent) or (task_uid not in self.all_tasks)
        }
        for task_uid in root_tasks:
            self.create_row(task_uid)
        self.stack.set_visible_child_name("tasks_page")

    def load_subtask_revealed_state(self, task_uid):
        if task_uid[0] not in self.subtasks_revealed_state:
            self.subtasks_revealed_state[task_uid[0]] = {}
        if task_uid[1] not in self.subtasks_revealed_state[task_uid[0]]:
            self.subtasks_revealed_state[task_uid[0]][task_uid[1]] = {}
        if task_uid[2] not in self.subtasks_revealed_state[task_uid[0]][task_uid[1]]:
            self.subtasks_revealed_state[task_uid[0]][task_uid[1]][task_uid[2]] = False

        # self.task_pane.box.set_visible(False)
        # self.pane.set_position(self.core.settings.settings_dict["task_pane_position"])

    # Starting/Stopping ------------------------------------------------------------------------------------------------
    def start(self):
        self._run_threads_flag = True
        #self.update_all_tasks()
        #GLib.timeout_add_seconds(1, self.update_all_tasks, priority=GLib.PRIORITY_DEFAULT_IDLE)

    def stop(self):
        self._run_threads_flag = False

    # todo add way for treestore manager to be updated when a task changes
    # TODO.txt Implement tag filtering
    def sort_tasks(self, task):
        return task[1].summary


    def open(self, source_id, collection_id, task_id, edit_mode=False):
        self.source_id = source_id
        self.collection_id = collection_id
        self.task_id = task_id
        self.task_box.set_visible(True)
        if edit_mode:
            self.stack.set_visible_child_name("edit")
            self.task_edit_pane.load_data(self.source_id, self.collection_id, self.task_id)
        else:
            self.stack.set_visible_child_name("view")
            self.view_pane.load_data(self.source_id, self.collection_id, self.task_id)
        #self.pane.set_position()
        #self.task_pane.load_data(*task_uid)
        #self.task_pane.box.set_visible(True)


    def close(self):
        self.task_box.set_visible(False)


    def _on_task_pane_position_notify(self, *_):
        pass























# Drag and Drop ########################################################################################################
class DragAndDropHandler:
    """
    Allows tasks to be dragged and dropped onto each other to change task hierarchy. Also prevents tasks from being
    dropped in between rows
    """

    @staticmethod
    def _drag_motion(widget, context, x, y, etime):
        """This handler prevents tasks from being dragged in between rows. Barely know how it works. Avoid touching"""
        drag_info = widget.get_dest_row_at_pos(x, y)
        if not drag_info:
            return False
        path, pos = drag_info
        Gdk.drag_status(context, context.get_suggested_action(), etime)
        if pos == Gtk.TreeViewDropPosition.BEFORE or pos == Gtk.TreeViewDropPosition.AFTER:
            return True
        else:
            return False

# List Mode Manager ####################################################################################################

def filter_function(self, model, iterator, __):
    pass
    #task_id = model.get_value(iterator, 0)
    #return False if self.enabled and self._task_center_core.get_children(task_id) else True
    # todo determine if task should be shown if children are done






# Sort Manager #########################################################################################################
class SortManager:
    """
    Allows tasks to be sorted using the treeview headings. Specifically, this customizes the sorting for all 3 dates
    and the recurrences
    """
    def __init__(self, gtk_builder):
        # treestore setup
        self._treestore = gtk_builder.get_object('task_treestore')
        self._treestore.connect('sort-column-changed', self._on_sort_column_changed)
        self._treestore.set_sort_func(5, self._repeat_sort_function, None)
        for date_column in (2, 3, 4):
            self._treestore.set_sort_func(date_column, self._date_sort_function, None)

        # parameter parsing
        self.sort_column = None
        self.sort_type = None

#        self.load_sort_settings()

    def _date_sort_function(self, model, row1, row2, _):
        """
        Sorts the date columns in the _treeview

        it returns the following
           -1 if row1 should appear before row2
            0 if both are equal in sorting
            1 if row2 should appear before row1
        """
        now = arrow.now()

        def get_date(row):
            column, _ = self._treestore.get_sort_column_id()
            task_id = model.get_value(row, 0)
            task_data = self.task_center_core.get(task_id)
            if not task_data:
                return now
            date_manager = task_data.date_manager
            if column == 2 and date_manager.start_date:
                return date_manager.start_date
            elif column == 3 and date_manager.due_date:
                return date_manager.due_date
            elif column == 4 and date_manager.done_date:
                return date_manager.completion_date
            else:
                return now
        date1 = get_date(row1)
        date2 = get_date(row2)
        if date1 < date2:
            return -1
        elif date1 > date2:
            return 1
        else:
            return 0

    def _repeat_sort_function(self, model, row1, row2, _):
        """
        This method is the sort function handler for the repeat column in a gui _treeview

        it returns the following
            -1 if row1 should appear before row2
            0 if both are equal in sorting 2
            1 if row2 should appear before row1

        The overarching guide is to sort from more frequent intervals to less.
        Task recurrences are sorted in the following priority.

            Tasks with recurrence comes before tasks without. If neither has recurrences, they're equal.
            If both have recurrences, further sorting is done

            Tasks follow the following order with the first in the list appearing first
            'minute', 'hour', 'day', 'week', 'month', 'year'.
            If both have the same interval, further sorting is done

            Tasks with lower increments (ie, more frequent repeat intervals) appear first.
            if both have the same increment, further sorting is done

            For week tasks, tasks with more weekdays come before those with less
       """
        def fetch_repeat_data(row):
            task_id = model.get_value(row, 0)

            task_data = self.task_center_core.get(task_id)
            return task_data.date_manager.recurrence if task_data else None

        recurrence1 = fetch_repeat_data(row1)
        recurrence2 = fetch_repeat_data(row2)

        # repeat enabled vs not
        recurrence1_enabled = recurrence1.enabled if recurrence1 else False
        recurrence2_enabled = recurrence2.enabled if recurrence2 else False
        if not recurrence1_enabled and not recurrence2_enabled:
            return 0
        elif recurrence1_enabled and not recurrence2_enabled:
            return -1
        elif not recurrence1_enabled and recurrence2_enabled:
            return 1

        # interval sorting
        interval_order = ['minute', 'hour', 'day', 'week', 'month', 'year']
        interval1 = interval_order.index(recurrence1.interval)
        interval2 = interval_order.index(recurrence2.interval)
        if interval1 < interval2:
            return -1
        elif interval1 > interval2:
            return 1

        # Increment sorting
        if recurrence1.increment < recurrence2.increment:
            return -1
        elif recurrence1.increment > recurrence2.increment:
            return 1

        # weekday sorting
        weekdays1 = recurrence1.weekdays.sources
        weekdays2 = recurrence2.weekdays.sources
        if not weekdays1 and not weekdays2:
            return 0
        elif not weekdays1 and weekdays2:
            return 1
        elif weekdays1 and not weekdays2:
            return -1
        elif weekdays1 > weekdays2:
            return -1
        elif weekdays1 < weekdays2:
            return 1
        else:
            return 0

    # sort settings ----------------------------------------------------------------------------------------------------
    def _on_sort_column_changed(self, *_):
        self.save_sort_settings()

    def save_sort_settings(self):
        pass

    def load_sort_settings(self):
        pass



class SortManager:

    def __init__(self, treestore, task_manager):
        self.treestore = treestore
        self.task_manager = task_manager
        self.sort_column = 1
        self.sort_type = 'ascending'


        self.treestore.set_sort_column_id(1, Gtk.SortType.ASCENDING)

        for date_column in (2, 3, 4):
            self.treestore.set_sort_func(date_column, self._date_sort_function)
        self.treestore.set_sort_func(5, self._repeat_sort_function)

    def load_sort_settings(self, column, sort_type):
        if sort_type == 'ascending':
            self.treestore.set_sort_column_id(column, Gtk.SortType.ASCENDING)
        elif sort_type == 'descending':
            self.treestore.set_sort_column_id(column, Gtk.SortType.DESCENDING)
        else:
            self.treestore.set_sort_column_id(column, Gtk.SortType.ASCENDING)

    def get_sort_settings(self):
        column, sort_type = self.treestore.get_sort_column_id()

        if type(sort_type) == Gtk.SortType.ASCENDING:
            sort_type = 'ascending'
        elif type(sort_type) == Gtk.SortType.DESCENDING:
            sort_type = 'descending'
        else:
            sort_type = 'ascending'
        return column, sort_type



    def _date_sort_function(self, model, row1, row2, _):
        """
        Sorts the date columns in the treeview

        it returns the following
           -1 if row1 should appear before row2
            0 if both are equal in sorting
            1 if row2 should appear before row1

        """
        now = arrow.now()

        def get_date(row):
            column, _ = self.treestore.get_sort_column_id()
            task_id = model.get_value(row, 0)
            task_data = self.task_manager.get_task(task_id=task_id)
            if not task_data:
                return now
            date_manager = task_data.date_manager
            if column == 2 and date_manager.start_date:
                return date_manager.start_date
            elif column == 3 and date_manager.due_date:
                return date_manager.due_date
            elif column == 4 and date_manager.done_date:
                return date_manager.completion_date
            else:
                return now
        date1 = get_date(row1)
        date2 = get_date(row2)
        if date1 < date2:
            return -1
        elif date1 > date2:
            return 1
        else:
            return 0

    def _repeat_sort_function(self, model, row1, row2, _):
        """
        This method is the sort function handler for the repeat column in a gui treeview

        it returns the following
            -1 if row1 should appear before row2
            0 if both are equal in sorting 2
            1 if row2 should appear before row1

        The overarching guide is to sort from more frequent intervals to less.
        Task recurrences are sorted in the following priority.

            Tasks with recurrence comes before tasks without. If neither has recurrences, they're equal.
            If both have recurrences, further sorting is done

            Tasks follow the following order with the first in the list appearing first
            'minute', 'hour', 'day', 'week', 'month', 'year'.
            If both have the same interval, further sorting is done

            Tasks with lower increments (ie, more frequent repeat intervals) appear first.
            if both have the same increment, further sorting is done

            For week tasks, tasks with more weekdays come before those with less
       """

        def fetch_repeat_data(row):
            task_id = model.get_value(row, 0)
            if not self.task_manager.get_task(task_id):
                return None
            return self.task_manager.get_task(task_id).date_manager.recurrence
        recurrence1 = fetch_repeat_data(row1)
        recurrence2 = fetch_repeat_data(row2)

        recurrence1_enabled = recurrence1.enabled if recurrence1 else False
        recurrence2_enabled = recurrence2.enabled if recurrence2 else False

        # repeat enabled vs not
        if not recurrence1_enabled and not recurrence2_enabled:
            return 0
        elif recurrence1_enabled and not recurrence2_enabled:
            return -1
        elif not recurrence1_enabled and recurrence2_enabled:
            return 1

        # interval sorting
        interval_order = ['minute', 'hour', 'day', 'week', 'month', 'year']
        interval1 = interval_order.index(recurrence1.interval) + 1
        interval2 = interval_order.index(recurrence2.interval) + 1
        if not interval1 and not interval2:
            return 0
        elif not interval1 and interval2:
            return 1
        elif interval1 and not interval2:
            return -1
        elif interval1 < interval2:
            return -1
        elif interval1 > interval2:
            return 1

        # Increment sorting
        if not recurrence1.increment and not recurrence2.increment:
            return 0
        elif not recurrence1.increment and recurrence2.increment:
            return -1
        elif recurrence1.increment and not recurrence2.increment:
            return 1
        if recurrence1.increment < recurrence2.increment:
            return -1
        elif recurrence1.increment > recurrence2.increment:
            return 1

        # weekday sorting
        weekdays1 = recurrence1.weekdays.sources
        weekdays2 = recurrence2.weekdays.sources
        if not weekdays1 and not weekdays2:
            return 0
        elif not weekdays1 and weekdays2:
            return 1
        elif weekdays1 and not weekdays2:
            return -1
        elif weekdays1 > weekdays2:
            return -1
        elif weekdays1 < weekdays2:
            return 1
        else:
            return 0




# Sort Manager #########################################################################################################
class SortManager:
    """
    Allows tasks to be sorted using the treeview headings. Specifically, this customizes the sorting for all 3 dates
    and the recurrences
    """
    def __init__(self, gtk_builder, task_center_core):
        # treestore setup
        self._treestore = gtk_builder.get_object('task_treestore')
        self._treestore.connect('sort-column-changed', self._on_sort_column_changed)
        self._treestore.set_sort_func(5, self._repeat_sort_function, None)
        for date_column in (2, 3, 4):
            self._treestore.set_sort_func(date_column, self._date_sort_function, None)

        # parameter parsing
        self.task_center_core = task_center_core
#        self.settings_dict = task_center_core.settings_dict
        self.sort_column = None
        self.sort_type = None

#        self.load_sort_settings()


    def _date_sort_function(self, model, row1, row2, _):
        """
        Sorts the date columns in the _treeview

        it returns the following
           -1 if row1 should appear before row2
            0 if both are equal in sorting
            1 if row2 should appear before row1
        """
        now = arrow.now()

        def get_date(row):
            column, _ = self._treestore.get_sort_column_id()
            task_id = model.get_value(row, 0)
            task_data = self.task_center_core.get_task(task_id)
            if not task_data:
                return now
            date_manager = task_data.date_manager
            if column == 2 and date_manager.start_date:
                return date_manager.start_date
            elif column == 3 and date_manager.due_date:
                return date_manager.due_date
            elif column == 4 and date_manager.done_date:
                return date_manager.completion_date
            else:
                return now
        date1 = get_date(row1)
        date2 = get_date(row2)
        if date1 < date2:
            return -1
        elif date1 > date2:
            return 1
        else:
            return 0

    def _repeat_sort_function(self, model, row1, row2, _):
        """
        This method is the sort function handler for the repeat column in a gui _treeview

        it returns the following
            -1 if row1 should appear before row2
            0 if both are equal in sorting 2
            1 if row2 should appear before row1

        The overarching guide is to sort from more frequent intervals to less.
        Task recurrences are sorted in the following priority.

            Tasks with recurrence comes before tasks without. If neither has recurrences, they're equal.
            If both have recurrences, further sorting is done

            Tasks follow the following order with the first in the list appearing first
            'minute', 'hour', 'day', 'week', 'month', 'year'.
            If both have the same interval, further sorting is done

            Tasks with lower increments (ie, more frequent repeat intervals) appear first.
            if both have the same increment, further sorting is done

            For week tasks, tasks with more weekdays come before those with less
       """
        def fetch_repeat_data(row):
            task_id = model.get_value(row, 0)

            task_data = self.task_center_core.get_task(task_id)
            return task_data.date_manager.recurrence if task_data else None

        recurrence1 = fetch_repeat_data(row1)
        recurrence2 = fetch_repeat_data(row2)

        # repeat enabled vs not
        recurrence1_enabled = recurrence1.enabled if recurrence1 else False
        recurrence2_enabled = recurrence2.enabled if recurrence2 else False
        if not recurrence1_enabled and not recurrence2_enabled:
            return 0
        elif recurrence1_enabled and not recurrence2_enabled:
            return -1
        elif not recurrence1_enabled and recurrence2_enabled:
            return 1

        # interval sorting
        interval_order = ['minute', 'hour', 'day', 'week', 'month', 'year']
        interval1 = interval_order.index(recurrence1.interval)
        interval2 = interval_order.index(recurrence2.interval)
        if interval1 < interval2:
            return -1
        elif interval1 > interval2:
            return 1

        # Increment sorting
        if recurrence1.increment < recurrence2.increment:
            return -1
        elif recurrence1.increment > recurrence2.increment:
            return 1

        # weekday sorting
        weekdays1 = recurrence1.weekdays.sources
        weekdays2 = recurrence2.weekdays.sources
        if not weekdays1 and not weekdays2:
            return 0
        elif not weekdays1 and weekdays2:
            return 1
        elif weekdays1 and not weekdays2:
            return -1
        elif weekdays1 > weekdays2:
            return -1
        elif weekdays1 < weekdays2:
            return 1
        else:
            return 0

    # sort settings ----------------------------------------------------------------------------------------------------
    def _on_sort_column_changed(self, *_):
        self.save_sort_settings()

    def save_sort_settings(self):
        self.task_center_core.settings._dict['gui']['sort_settings'] = self._treestore.get_sort_column_id()

    #def load_sort_settings(self):
        #gtk_present = 'gui' in self.task_center_core.settings_dict._dict
        #sort_settings_present = gtk_present and 'sort_settings' in self.task_center_core.settings_dict._dict['gui']
        #if sort_settings_present:
        #    resources = self.task_center_core.settings_dict['sort_settings']
        #    self._treestore.set_sort_column_id(resources[0], resources[1])
        #else:
         #   self._treestore.set_sort_column_id(1, Gtk.SortType.ASCENDING)









# Commands ################################################################################################
class Commands:
    def __init__(self, gtk_builder, task_treestore_manager):
        self.main_window = gtk_builder.get_object('window')
        self.task_treestore_manager = task_treestore_manager

    def create_task(self, *_):
        #task = Task()
        #TaskEditorInterface(task, self.task_treestore_manager, dialog_parent=self.main_window)
        self.task_treestore_manager.update_task(task)

    def create_subtask(self, *_):
        parent_id = self.get_selected_rows()[0]
        #task = Task.get(parent_id).create_subtask()
        #TaskEditorInterface(task, self.task_treestore_manager, dialog_parent=self.main_window)
        self.task_treestore_manager.update_task(task)

    def edit_task(self, *_):
        task_id = self.get_selected_rows()[0]
        #task = Task.get(task_id)
        #TaskEditorInterface(task, self.task_treestore_manager, dialog_parent=self.main_window)
        self.task_treestore_manager.update_task(task)

    def mark_done(self, *_):
        #for task_id in self.get_selected_rows():
            #task = Task.get(task_id)
            #task.done_date = datetime.now()
            #self.task_treestore_manager.update_task(task)
        pass

    def mark_undone(self, *_):
        for task_id in self.get_selected_rows():
            pass
            #task = Task.get(task_id)
            #task.done_date = None
         #   self.task_treestore_manager.update_task(task)
        pass

    def delete_task(self, *_):
        for task_id in self.get_selected_rows():
            pass
            #task = Task.get(task_id)
            #task.delete()
            #self.task_treestore_manager.update_task(task)

    def get_selected_rows(self):
        return self.task_treestore_manager.get_selected_rows()



# User Controls ########################################################################################################
class UserControls:
    def __init__(self, gtk_builder, task_commands):
        self.gtk_builder = gtk_builder
        self.task_commands = task_commands

        # Handlers
        self.setup_new_task_headerbar_button_handler()
        self.setup_treeview_row_activated_handler()
        self.setup_right_click_handler()
        self.setup_actionbar_handler()
        self.setup_keyboard_shortcut_handler()

    # Nea Task Headerbar Button ----------------------------------------------------------------------------------------
    def setup_new_task_headerbar_button_handler(self):
        self.gtk_builder.get_object('new_task_button').connect('clicked', self.task_commands.create_task)

    # Double click task row to edit  -----------------------------------------------------------------------------------
    def setup_treeview_row_activated_handler(self):
        self.gtk_builder.get_object('task_treeview').connect('row-activated', self.task_commands.edit_task)

    # Right click task row context menu --------------------------------------------------------------------------------
    def setup_right_click_handler(self):
        def on_task_treeview_button_release_event(widget, event):
            row_info = widget.get_path_at_pos(event.x, event.y)
            if event._button == 3 and row_info:
                widget.grab_focus()
                widget.set_cursor(row_info[0], row_info[1], 0)
                self.gtk_builder.get_object('right_click_menu').popup_at_pointer()
        widget_handlers_dict = {
            'right_click_menu_new_subtask_button': ('activate', self.task_commands.create_subtask),
            'right_click_menu_edit_button': ('activate', self.task_commands.edit_task),
            'right_click_menu_mark_done_button': ('activate', self.task_commands.mark_done),
            'right_click_menu_mark_undone_button': ('activate', self.task_commands.mark_undone),
            'right_click_menu_delete_button': ('activate', self.task_commands.delete_task),
            'task_treeview': ('button-release-event', on_task_treeview_button_release_event)}
        for widget_to_connect in widget_handlers_dict:
            signal = widget_handlers_dict[widget_to_connect][0]
            callback = widget_handlers_dict[widget_to_connect][1]
            self.gtk_builder.get_object(widget_to_connect).connect(signal, callback)

    # Actionbar at bottom of window ------------------------------------------------------------------------------------
    def setup_actionbar_handler(self):
        def update_toolbar_visibility(*_):
            no_task_visibility = False if len(self.task_commands.get_selected_rows()) == 0 else True
            self.gtk_builder.get_object('task_actionbar_revealer').set_reveal_child(no_task_visibility)
            for button in ['task_actionbar_new_subtask_button', 'task_actionbar_edit_task_button']:
                single_task_visibility = False if len(self.task_commands.get_selected_rows()) > 1 else True
                self.gtk_builder.get_object(button).set_sensitive(single_task_visibility)
        widget_handlers_dict = {
            'task_treeview_selection': ('changed', update_toolbar_visibility),
            'task_actionbar_new_subtask_button': ('clicked', self.task_commands.create_subtask),
            'task_actionbar_edit_task_button': ('clicked', self.task_commands.edit_task),
            'task_actionbar_mark_done_button': ('clicked', self.task_commands.mark_done),
            'task_actionbar_mark_undone_button': ('clicked', self.task_commands.mark_undone),
            'task_actionbar_delete_button': ('clicked', self.task_commands.delete_task)}
        for widget in widget_handlers_dict:
            signal = widget_handlers_dict[widget][0]
            callback = widget_handlers_dict[widget][1]
            self.gtk_builder.get_object(widget).connect(signal, callback)

    # Keyboard shortcuts -----------------------------------------------------------------------------------------------
    def setup_keyboard_shortcut_handler(self):
        pass

def get_date_string(date):
    datetime_string = ""
    if date:
        datetime_string = date.strftime("%B %d, %Y")
        if date.hour != 0 and date.minute != 0:
            datetime_string += date.strftime(" at %H:%M")
    return datetime_string

# TODO: Implement Drag and Drop
# Todo Implement Sorting
# Todo Implement Filtering
