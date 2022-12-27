from uuid import uuid4

from task_center.core.settings import SettingsManager
from task_center.core.tasks.sources import SOURCES

# TaskManager ##########################################################################################################
class TasksManager:
    def __init__(self, settings: SettingsManager):
        self._settings = settings
        self._sources = {}
        self.load_settings()

    # Sources ----------------------------------------------------------------------------------------------------------
    def create_source(self, source):
        source_id = str(uuid4())
        self._sources[source_id] = source
        self.save_settings()
        return source_id
    def get_all_sources(self):
        return self._sources.keys()

    def get_source(self, source_id):
        return self._sources[source_id]

    def update_source(self, source_id, source):
        self._sources[source_id] = source
        self.save_settings()

    def delete_source(self, source_id):
        del self._sources[source_id]
        self.save_settings()

    # Collections ------------------------------------------------------------------------------------------------------
    def sync_collections(self, source_id):
        self._sources[source_id].sync_collections()


    def create_collection(self, source_id, collection):
        return self._sources[source_id].create_collection(collection)

    def get_all_collections(self, source_id):
        collections = self._sources[source_id].get_all_collections()
        if collections:
            sorted_collections = sorted(collections.items(), key=lambda collection: collection[1].name)
            return sorted_collections

    def get_collection(self, source_id, collection_id):
        return self._sources[source_id].get_collection(collection_id)

    def update_collection(self, source_id, collection_id, collection):
        self._sources[source_id].update_collection(collection_id, collection)

    def delete_collection(self, source_id, collection_id):
        self._sources[source_id].delete_collection(collection_id)

    # Tasks ------------------------------------------------------------------------------------------------------------
    def create_task(self, source_id, collection_id, task):
        return self._sources[source_id].create_task(collection_id, task)

    def get_all_tasks(self):
        tasks = {}
        for source in self._sources:
            pass

    def get_collection_tasks(self, source_id, collection_id):
        return self._sources[source_id].get_all_tasks(collection_id)

    def get_task(self, source_id, collection_id, task_id):
        return self._sources[source_id].get_task(collection_id, task_id)

    def update_task(self, source_id, collection_id, task_id, task):
        return self._sources[source_id].update_task(collection_id, task_id, task)

    def delete_task(self, source_id, collection_id, task_id):
        self._sources[source_id].delete_task(collection_id, task_id)

    # Settings ---------------------------------------------------------------------------------------------------------
    def load_settings(self):
        self._settings.load()
        if not self._settings.get_setting("sources"):
            self._settings.set_setting('sources', {})
            self._settings.save()
        for id, source_setting in self._settings.get_setting('sources').items():
            self._sources[id] = SOURCES[source_setting['type']]()
            self._sources[id].load_settings_dict(source_setting)

    def save_settings(self):
        self._settings.set_setting('sources', {source_id: source.get_settings_dict() for (source_id, source) in self._sources.items()} )
        self._settings.save()









class Archive:


    @staticmethod

    def _schedule_next_repeat(self):
        """
        Determines the next date that the task should repeat, depending on the start/due  date
        If a task has both start and due dates set, then the due date will be updated according to the recurrence. The
        start date will be updated to have the same distance from the due date as it had previously
        """
        if self.recurrence.enabled:
            if self.due_date and self.start_date:
                difference = self.due_date - self.start_date
                self.due_date = self.recurrence.get_next_date(self.due_date)
                self.start_date = self.due_date - difference
            elif self.due_date:
                self.due_date = self.recurrence.get_next_date(self.due_date)
            elif self.start_date:
                self.start_date = self.recurrence.get_next_date(self.start_date)

    """

    def mark_undone(self, task_id):
        self.task_manager.mark_undone(task_id)
        self.treestore_manager.update_task(task_id)
        for child in self.task_manager.task_relationship_manager.get_task_children(task_id):
            self.treestore_manager.update_task(child)

    def mark_done(self, task_id):
        self.task_manager.mark_done(task_id)
        self.treestore_manager.update_task(task_id)
        for child in self.task_manager.task_relationship_manager.get_task_children(task_id):
            self.treestore_manager.update_task(child)
"""

    def done_date(self, done_date_arrow):
        self._done_date = done_date_arrow
        if done_date_arrow:  # marking  done
            if self.recurrence.enabled:
                # schedule new start and due dates and clear the done date
                self._schedule_next_repeat()
                self._done_date = None
                for child in self.children:
                    child.done_date = None
            else:
                for child in self.children:
                    if not child.done_date:
                        child.done_date = done_date_arrow
        else:
            if self.parent:
                Task.get(self.parent).done_date = None

    # ancestors
    # children
    # parent
    # child


    def mark_done(self, task_id):
        """Marks a task and all its children as done"""
        self.get_task(task_id).mark_done()
        for child in self.task_relationship_manager.get_task_children(task_id):
            self.get_task(child).mark_done()

    def mark_undone(self, task_id):
        """Marks a task, all its children and its ancestral tasks as undone"""
        self.get_task(task_id).mark_undone()
        for child in self.task_relationship_manager.get_task_children(task_id):
            self.get_task(child).mark_undone()
        for parent in self.task_relationship_manager.get_task_ancestry(task_id):
            self.mark_undone(parent)


    # Task Status ######################################################################################################
    def get_task_active(self, task_id):
        return True if not self.task_master_dict[task_id].date_manager.done_date else False

    def get_task_done(self, task_id):
        return True if self.get_task(task_id).date_manager.done_date else False

    def get_task_doable(self, task_id):
        """
        Determines whether a task is doable

        For a task to be doable:
        If a task has children and all children are done, the task is doable
        If a task has children and at least one child can be done, the task is doable.
        If a task has no children, its doability depends on its own status (no done date, start date and start date has passed)
        """
        # logging.debug(f"Determining doability for task {task_id}")
        children = self.task_relationship_manager.get_task_children(task_id)
        if self.get_task(task_id).is_doable and children:
            # all children done, task can now be worked on
            if all(self.get_task_done(child) for child in children):
                return True
            # a child is doable, so this task can be worked on too
            elif any(self.get_task(child).is_doable() for child in children):
                return True
        else:
            return self.get_task(task_id).is_doable()


    def get_task_in_current_list(self, task_id):
        return True if self.get_task_doable(task_id) and not self.task_relationship_manager.get_task_children(
            task_id) else False


    def get_task_in_current_tree(self, task_id):
        return True if self.get_task_doable(task_id) else False


    # All task methoods ################################################################################################

    def get_active_tasks(self):
        """This method gets all active tasks, which are tasks that arent done yet (has no done date)"""
        return [task_id for task_id in self.task_master_dict if self.get_task_active(task_id)]

    def get_current_tree(self):
        """Returns lists of all doable tasks. See the "get_task_doable()" method for criteria on task doability."""
        return [task_id for task_id in self.task_master_dict if self.get_task_doable(task_id)]

    def get_current_list(self):
        """returns a lists of doable leaves of the task tree (tasks with subtasks arent included)"""
        return [task_id for task_id in self.task_master_dict if self.get_task_in_current_list(task_id)]

    def get_done_tasks(self):
        """Gets a lists of all done tasks (tasks with a done date)"""
        return [task for task in self.task_master_dict if self.get_task_done(task)]