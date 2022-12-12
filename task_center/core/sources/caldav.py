import caldav
from caldav.elements.ical import CalendarColor
from caldav.elements import dav
import icalendar
import keyring
from pprint import pprint
from task_center.core.models.source import Source
from task_center.core.models.tasklists import TaskList
from task_center.core.models.tasks import Task


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
    def create_list(self, tasklist):
        calendar = self.client.principal().make_calendar(name=tasklist.name, supported_calendar_component_set=['VTODO'])
        calendar.set_properties([dav.DisplayName(tasklist.name)])
        calendar.set_properties([caldav.elements.ical.CalendarColor(tasklist.color)])
        calendar.save()
        return calendar.url

    def get_all_lists(self):
        calendars = {}
        for calendar in self.client.principal().calendars():
            name = calendar.name
            color = calendar.get_properties([CalendarColor()])[CalendarColor.tag]
            calendars[str(calendar.url)] = TaskList(name, color)
        return calendars

    def get_list(self, url):
        calendar = next(calendar for calendar in self.client.principal().calendars() if calendar.url == url)
        name = calendar.name
        color = calendar.get_properties([CalendarColor()])[CalendarColor.tag]
        return TaskList(name, color)

    def update_list(self, url, tasklist: TaskList):
        calendar = next(calendar for calendar in self.client.principal().calendars() if calendar.url == url)
        calendar.name = tasklist.name
        calendar.set_properties([dav.DisplayName(tasklist.name)])
        calendar.set_properties([caldav.elements.ical.CalendarColor(tasklist.color)])
        calendar.save()

    def delete_list(self, url):
        calendar = next(calendar for calendar in self.client.principal().calendars() if calendar.url == url)
        calendar.delete()

    # Tasks ------------------------------------------------------------------------------------------------------------
    def create_task(self, list_id, task: Task):
        calendar = next(calendar for calendar in self.client.principal().calendars() if calendar.url == list_id)
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
        calendar = next(calendar for calendar in self.client.principal().calendars() if calendar.url == list_id)
        tasks = {}
        for caldav_todo in calendar.todos():
            ical = caldav_todo.icalendar_instance
            caldav_todo = next(item for item in ical.subcomponents if type(item) == icalendar.Todo)
            #print(icalendar.Todo.keys())
            #pprint(caldav_todo.items(), indent=4)
            #icalendar.Todo().subcomponents.

            task = Task()
            task.summary = caldav_todo["SUMMARY"] if "SUMMARY" in caldav_todo else ""
            task.description = caldav_todo["DESCRIPTION"] if "DESCRIPTION" in caldav_todo else ""
            task.start_date = caldav_todo['DTSTART'].dt if "DTSTART" in caldav_todo else None
            task.due_date = caldav_todo["DUE"].dt if "DUE" in caldav_todo else None
            task.parent = caldav_todo["RELATED-TO"] if "RELATED-TO" in caldav_todo else ""
            task.created_date = caldav_todo["CREATED"].dt if "CREATED" in caldav_todo else ""
            task.last_modified_date = caldav_todo['LAST-MODIFIED'].dt if "LAST-MODIFIED" in caldav_todo else ""
            task.percent_complete = caldav_todo['PERCENT-COMPLETE'] if 'PERCENT-COMPLETE' in caldav_todo else 0
            task.priority = caldav_todo["PRIORITY"] if "PRIORITY" in caldav_todo else 0
            task.status = caldav_todo["STATUS"] if "STATUS" in caldav_todo else ""
            task.categories = caldav_todo['CATEGORIES'] if "CATEGORIES" in caldav_todo else []
            task.recurrence.caldav = caldav_todo['RRULE'] if "RRULE" in "todo" else ""
            tasks[caldav_todo["UID"]] = task
            #print(todos[todo["UID"]]["SEQUENCE"])
        return tasks

    def get_task(self, list_id, task_id):
        todos = self.get_all_tasks(list_id)
        return todos[task_id]


    def edit_task(self, list_id, task_id, task):
        #task =
        "event.vobject_instance.vevent.summary.value = ‘Norwegian national day celebrations’ event.save()"

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