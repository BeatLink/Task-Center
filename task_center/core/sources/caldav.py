"""
- client
    - principal
        - calendars
            - todos
                - icalendar_instance
                    - subcomponents
                        - timezone
                        - todo
"""

import caldav
from caldav.elements.ical import CalendarColor
from caldav.elements import dav
import icalendar
import keyring
from task_center.core.sources.source import Source
from task_center.core.collections.collections import Collection
from task_center.core.tasks.tasks import Task


class CaldavSource(Source):
    type = "caldav"

    def __init__(self):
        super().__init__()
        self.url = ""                   # The URL for the CalDAV server
        self.username = ""              # The username for the CalDAV server
        self.client = None

    @property
    def password(self):
        """The password for the CalDAV server"""
        return keyring.get_password(str(self.url), self.username)

    @password.setter
    def password(self, password):
        keyring.set_password(str(self.url), self.username, password)

    # Settings ---------------------------------------------------------------------------------------------------------
    def get_settings_dict(self):
        settings_dict = super().get_settings_dict()
        settings_dict['url'] = self.url
        settings_dict['username'] = self.username
        return settings_dict

    def load_settings_dict(self, settings_dict):
        super().load_settings_dict(settings_dict)
        self.url = settings_dict['url']
        self.username = settings_dict['username']
        self.client = caldav.DAVClient(
            url=self.url,
            username=self.username,
            password=self.password
        )

    # Lists ------------------------------------------------------------------------------------------------------------
    def create_collection(self, tasklist):
        calendar = self.client.principal().make_calendar(name=tasklist.name, supported_calendar_component_set=['VTODO'])
        calendar.set_properties([dav.DisplayName(tasklist.name)])
        calendar.set_properties([caldav.elements.ical.CalendarColor(tasklist.color)])
        calendar.save()
        return calendar.url

    def get_all_collections(self):
        calendars = {}
        for calendar in self.client.principal().calendars():
            name = calendar.name
            color = calendar.get_properties([CalendarColor()])[CalendarColor.tag]
            calendars[str(calendar.url)] = Collection(name, color)
        return calendars

    def get_collection(self, url):
        for calendar in self.client.principal().calendars():
            if calendar.url == url:
                name = calendar.name
                color = calendar.get_properties([CalendarColor()])[CalendarColor.tag]
                return Collection(name, color)

    def update_collection(self, url, tasklist: Collection):
        for calendar in self.client.principal().calendars():
            if calendar.url == url:
                calendar.name = tasklist.name
                calendar.set_properties([dav.DisplayName(tasklist.name)])
                calendar.set_properties([caldav.elements.ical.CalendarColor(tasklist.color)])
                calendar.save()

    def delete_collection(self, url):
        for calendar in self.client.principal().calendars():
            if calendar.url == url:
                calendar.delete()

    # Tasks ------------------------------------------------------------------------------------------------------------
    def create_task(self, list_id, task: Task):
        for calendar in self.client.principal().calendars():
            if calendar.url == list_id:
                calendar.save_todo(
                    summary=task.summary,
                    dtstart=task.start_date,
                    due=task.due_date,
                    ics="RRULE:FREQ=YEARLY",
                    categories=['family', 'finance'],
                    status='NEEDS-ACTION')

        #id = str(uuid.uuid4())
            #task = task if task else Task()
            #if self.get_task(task.id):
            #    raise TaskExistsException
            #self.task_database_manager.create_task(task)

    def get_all_tasks(self, list_id):
        tasks = {}
        for calendar in self.client.principal().calendars():
            if calendar.url == list_id:
                for caldav_todo in calendar.todos():
                    for ical_todo in caldav_todo.icalendar_instance.subcomponents:
                        if type(ical_todo) == icalendar.Todo:
                            task = Task()
                            task.summary = ical_todo["SUMMARY"] if "SUMMARY" in ical_todo else ""
                            task.description = ical_todo["DESCRIPTION"] if "DESCRIPTION" in ical_todo else ""
                            task.start_date = ical_todo['DTSTART'].dt if "DTSTART" in ical_todo else None
                            task.due_date = ical_todo["DUE"].dt if "DUE" in ical_todo else None
                            task.parent = ical_todo["RELATED-TO"] if "RELATED-TO" in ical_todo else ""
                            task.created_date = ical_todo["CREATED"].dt if "CREATED" in ical_todo else ""
                            task.last_modified_date = ical_todo['LAST-MODIFIED'].dt if "LAST-MODIFIED" in ical_todo else ""
                            task.percent_complete = ical_todo['PERCENT-COMPLETE'] if 'PERCENT-COMPLETE' in ical_todo else 0
                            task.priority = ical_todo["PRIORITY"] if "PRIORITY" in ical_todo else 0
                            task.status = ical_todo["STATUS"] if "STATUS" in ical_todo else ""
                            task.categories = ical_todo['CATEGORIES'] if "CATEGORIES" in ical_todo else []
                            task.recurrence.caldav = ical_todo['RRULE'] if "RRULE" in "todo" else ""
                            tasks[ical_todo["UID"]] = task
                return tasks

    def get_task(self, list_id, task_id):
        return self.get_all_tasks(list_id)[task_id]

    def get_task_parents(self, list_id, task_id):
        all_tasks = self.get_all_tasks(list_id)
        def get_parent_loop(task_id):
            parents = []
            if task_id:
                parent = all_tasks[task_id].parent
                if parent:
                    parents += get_parent_loop(parent)
                parents += [parent]
            return parents
        parents = get_parent_loop(task_id)
        print(parents)
        for parent in parents:
            if parent:
                print(all_tasks[parent].summary)
        return parents


    def edit_task(self, list_id, task_id, task):
        for calendar in self.client.principal().calendars():
            if calendar.url == list_id:
                for caldav_todo in calendar.todos():
                    for ical_todo in caldav_todo.icalendar_instance.subcomponents:
                        if type(ical_todo) == icalendar.Todo and ical_todo["UID"] == task_id:
                            ical_todo["RELATED-TO"] = task.parent if task.parent else ""
                            caldav_todo.save()


        #task =
        #"event.vobject_instance.vevent.summary.value = ‘Norwegian national day celebrations’ event.save()"

    def delete_task(self, list_id, task_id, delete_subtasks=False):
        for subtask in self.get_subtasks(task_id):
            if delete_subtasks:
                self.delete_task(subtask, delete_subtasks=True)
            else:
                subtask.parent=None
                self.update_task(subtask)
        self.all_tasks.remove(self)

        """Deletes a task and all its children"""
        if task_id in self.task_master_dict:
            del self.task_master_dict[task_id]
            for child in self.task_relationship_manager.get_task_children(task_id):
                self.delete_task(child)
            self.task_relationship_manager.delete_task(task_id)