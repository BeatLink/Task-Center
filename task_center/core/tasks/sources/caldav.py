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
import warnings
import caldav
import icalendar
import keyring
import urllib3
from caldav.elements import dav
from caldav.elements.ical import CalendarColor
from task_center.core.tasks.sources.generic import Source
from task_center.core.tasks.models.collection import Collection
from task_center.core.tasks.models.task import Task


class CaldavSource(Source):
    type = "caldav"

    def __init__(self):
        super().__init__()
        self.url = ""                   # The URL for the CalDAV server
        self.username = ""              # The username for the CalDAV server
        self.self_signed_cert = False
        self.client = None
        self.all_tasks = {}

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
        settings_dict['self_signed_cert'] = self.self_signed_cert
        return settings_dict

    def load_settings_dict(self, settings_dict):
        super().load_settings_dict(settings_dict)
        self.url = settings_dict['url']
        self.username = settings_dict['username']
        self.self_signed_cert = settings_dict['self_signed_cert']
        self.client = caldav.DAVClient(
            url=self.url,
            username=self.username,
            password=self.password,
            ssl_verify_cert=(not self.self_signed_cert)
        )
        if self.self_signed_cert:
            urllib3.disable_warnings(urllib3.connectionpool.InsecureRequestWarning)

    def get_principal(self):
        try:
            return self.client.principal()
        except:
            pass

    # Lists ------------------------------------------------------------------------------------------------------------
    def create_collection(self, collection):
        calendar = self.get_principal().make_calendar(name=collection.name, supported_calendar_component_set=['VTODO'])
        calendar.set_properties([dav.DisplayName(collection.name)])
        calendar.set_properties([caldav.elements.ical.CalendarColor(collection.color)])
        calendar.save()
        return calendar.url

    def get_all_collections(self):
        collections = {}
        principal = self.get_principal()
        if principal:
            calendars = principal.calendars()
            if calendars:
                for calendar in calendars:
                    name = calendar.name
                    color = calendar.get_properties([CalendarColor()])[CalendarColor.tag]
                    collections[str(calendar.url)] = Collection(name, color)
                return collections

    def get_collection(self, collection_id):
        return self.get_all_collections()[collection_id]

    def update_collection(self, collection_id, collection: Collection):
        for calendar in self.get_principal().calendars():
            if calendar.url == collection_id:
                calendar.name = collection.name
                calendar.set_properties([dav.DisplayName(collection.name)])
                calendar.set_properties([caldav.elements.ical.CalendarColor(collection.color)])
                calendar.save()

    def delete_collection(self, collection_id):
        for calendar in self.get_principal().calendars():
            if calendar.url == collection_id:
                calendar.delete()

    # Tasks ------------------------------------------------------------------------------------------------------------

    def create_task(self, collection_id, task: Task):
        for calendar in self.get_principal().calendars():
            if calendar.url == collection_id:
                calendar.save_todo(
                    summary=task.summary,
                    dtstart=task.start_date,
                    due=task.due_date,
                    ics="RRULE:FREQ=YEARLY",
                    categories=['family', 'finance'],
                    status='NEEDS-ACTION')

    def get_all_tasks(self, collection_id):
        tasks = {}
        for calendar in self.get_principal().calendars():
            if calendar.url == collection_id:
                for caldav_todo in calendar.todos():
                    print(caldav_todo.url)
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
                            task.tags = ical_todo['CATEGORIES'].cats if "CATEGORIES" in ical_todo else []
                            #task.recurrence.caldav = ical_todo['RRULE'] if "RRULE" in "todo" else ""
                            tasks[ical_todo["UID"]] = task
        return tasks

    def get_task(self, collection_id, task_id):
        for calendar in self.get_principal().calendars():
            if calendar.url == collection_id:
                for caldav_todo in calendar.todos():
                    for ical_todo in caldav_todo.icalendar_instance.subcomponents:
                        if type(ical_todo) == icalendar.Todo and ical_todo["UID"] == task_id:
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
                            task.tags = ical_todo['CATEGORIES'].cats if "CATEGORIES" in ical_todo else []
                            return task

    def update_task(self, collection_id, task_id, task):
        for calendar in self.get_principal().calendars():
            if calendar.url == collection_id:
                for caldav_todo in calendar.todos():
                    for ical_todo in caldav_todo.icalendar_instance.subcomponents:
                        if type(ical_todo) == icalendar.Todo and ical_todo["UID"] == task_id:
                            ical_todo["RELATED-TO"] = task.parent if task.parent else ""
                            ical_todo["SUMMARY"] = task.summary
                            ical_todo["DESCRIPTION"] = task.description
                            if "CATEGORIES" not in ical_todo:
                                ical_todo['CATEGORIES'] = icalendar.prop.vCategory([])
                            ical_todo['CATEGORIES'].cats = [icalendar.prop.vText(tag) for tag in task.tags]
                            caldav_todo.save()


    def delete_task(self, collection_id, task_id):
        for calendar in self.get_principal().calendars():
            if calendar.url == collection_id:
                for caldav_todo in calendar.todos():
                    for ical_todo in caldav_todo.icalendar_instance.subcomponents:
                        if type(ical_todo) == icalendar.Todo and ical_todo["UID"] == task_id:
                            caldav_todo.delete()
