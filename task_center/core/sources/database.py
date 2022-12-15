import pathlib
import peewee
import playhouse.signals

from task_center.core.sources.source import Source

"""This class is Task Center's logic manager/API. This manages the tasks, tags and file handling."""


# Exceptions -------------------------------------------------------------------------------------------------------
class InvalidFileError(Exception):
    pass


class NoFilePathError(Exception):
    pass

    # Create, Get, GetAll, Update, Delete


class Recurrence(playhouse.signals.Model):
    id = peewee.CharField(primary_key=True)
    enabled = peewee.BooleanField(default=False)
    interval = peewee.CharField(default='minute')
    increment = peewee.IntegerField(default=1)
    week_sunday = peewee.BooleanField(default=False)
    week_monday = peewee.BooleanField(default=False)
    week_tuesday = peewee.BooleanField(default=False)
    week_wednesday = peewee.BooleanField(default=False)
    week_thursday = peewee.BooleanField(default=False)
    week_friday = peewee.BooleanField(default=False)
    week_saturday = peewee.BooleanField(default=False)
    month_ordinal = peewee.IntegerField(null=True)
    month_weekday = peewee.IntegerField(null=True)
    stop_type = peewee.CharField(default='never')
    stop_date = peewee.DateTimeField(default=None, null=True)
    stop_number = peewee.IntegerField(default=0)


class Task(playhouse.signals.Model):
    id = peewee.CharField(primary_key=True)
    parent = peewee.ForeignKeyField('self', null=True, backref='children')
    sort_oder = peewee.IntegerField()
    title = peewee.CharField(default='')
    notes = peewee.TextField(default='')
    start_date = peewee.DateTimeField(null=True)
    due_date = peewee.DateTimeField(null=True)
    done_date = peewee.DateTimeField(null=True)
    recurrence = peewee.ForeignKeyField(Recurrence, backref="task")



class TaskDatabaseManager:
    def __init__(self):
        pass

    @staticmethod
    def get_task(task_id):
        database_task = DatabaseTask.get(task_id)
        task = Task()
        task.title = database_task.title
        task.notes = database_task.notes
        task.start_date = database_task.start_date
        task.due_date = database_task.due_date
        task.done_date = database_task.done_date
        task.parent = None  # use query to get storage task with similar id
        task.recurrence.enabled = database_task.recurrence_enabled
        task.recurrence.increment = database_task.recurrence_increment
        task.recurrence.interval = database_task.recurrence_interval
        task.recurrence.weekdays.sunday = database_task.recurrence_weekdays_sunday
        task.recurrence.weekdays.monday = database_task.recurrence_weekdays_monday
        task.recurrence.weekdays.tuesday = database_task.recurrence_weekdays_tuesday
        task.recurrence.weekdays.wednesday = database_task.recurrence_weekdays_wednesday
        task.recurrence.weekdays.thursday = database_task.recurrence_weekdays_thursday
        task.recurrence.weekdays.friday = database_task.recurrence_weekdays_friday
        task.recurrence.weekdays.saturday = database_task.recurrence_weekdays_saturday
        task.recurrence.weekday_of_month.ordinal = database_task.recurrence_weekday_of_month_ordinal
        task.recurrence.weekday_of_month.weekday = database_task.recurrence_weekday_of_month_weekday
        task.recurrence.stop_info.type = database_task.recurrence_stop_type
        task.recurrence.stop_info.date = database_task.recurrence_stop_date
        task.recurrence.stop_info.number = database_task.recurrence_stop_number
        return task

    @staticmethod
    def update_task(task: Task):
        database_task = DatabaseTask(
            title=task.title,
            notes=task.notes,
            start_date=task.start_date,
            due_date=task.due_date,
            done_date=task.done_date,
            parent=task.parent,
        )
        recurrence = task.recurrence
        database_recurrence = DatabaseRecurrence(
            task_id = database_task,
            enabled=recurrence.enabled,
            increment=recurrence.increment,
            interval=recurrence.interval,
        )
        weekdays = recurrence.weekdays
        database_weekdays = DatabaseWeekdays(
            recurrence_id=database_recurrence,
            sunday=weekdays.sunday,
            monday=weekdays.monday,
            tuesday=weekdays.tuesday,
            wednesday=weekdays.wednesday,
            thursday=weekdays.thursday,
            friday=weekdays.friday,
            saturday=weekdays.saturday,
        )
        weekday_of_month = recurrence.weekday_of_month
        database_weekday_of_month = DatabaseWeekdayOfMonth(
            recurrence_id=database_recurrence,
            ordinal=weekday_of_month.ordinal,
            weekday=weekday_of_month.weekday
        )

        stop_data = recurrence.stop_info
        database_stop_data = DatabaseStopData(
            recurrence_id=database_recurrence,
            type=stop_data.type,
            date=stop_data.date,
            number=stop_data.number
        )

        database_task.save()
        database_recurrence.save()
        database_weekdays.save()
        database_weekday_of_month.save()
        database_stop_data.save()

    @staticmethod
    def delete_task(task_id):
        database_task = DatabaseTask.get_by_id(task_id)
        database_task.delete_instance()

    @staticmethod
    def load_all():
        for task in DatabaseTask.select():
            pass


class List(playhouse.signals.Model):
    id = peewee.CharField(primary_key=True)
    backend = ""
    parent = peewee.ForeignKeyField('self', null=True, backref='children')
    sort_order = peewee.IntegerField()
    name = peewee.CharField()
    description = peewee.TextField()
    color = peewee.CharField()
    icon = peewee.CharField()


class Task(playhouse.signals.Model):
    id = peewee.CharField(primary_key=True)
    parent = peewee.ForeignKeyField('self', null=True, backref='children')
    sort_oder = peewee.IntegerField()
    title = peewee.CharField(default='')
    notes = peewee.TextField(default='')
    start_date = peewee.DateTimeField(null=True)
    due_date = peewee.DateTimeField(null=True)
    done_date = peewee.DateTimeField(null=True)
    recurrence = peewee.ForeignKeyField(Recurrence, backref="task")


class DatabaseSource(Source):
    type = "database"

    def __init__(self):
        super().__init__()
        self.database_path = ""                             # The path to the local database
        self._VERSION = 846711849                           # TCv1 converted to ASCII with spaces removed
        self._engine = None                                 # The peewee storage engine
        self._database = None                               # The peewee storage
        self._MODELS = (Task, Recurrence)                   # The storage database

        """This code creates the database file and initializes all the tables."""
        database = peewee.SqliteDatabase('TaskCenter.db')
        models = [List]
        with database:
            for model in models:
                model.bind(database)
            database.create_tables(models)

    # Settings ---------------------------------------------------------------------------------------------------------
    def get_settings_dict(self):
        settings_dict = super().get_settings_dict()
        settings_dict['database_path'] = self.database_path
        return settings_dict

    def load_settings_dict(self, settings_dict):
        super().load_settings_dict(settings_dict)
        self.database_path = settings_dict["database_path"]

    # Get Database File Path -------------------------------------------------------------------------------------------
    def open_file(self, file_path: str, existing=False):
        self._database.close()                              # Close engine if open
        self._file_path = pathlib.Path(file_path) if file_path else None  # Set file path
        self._validate_file_path(existing)                  # Validate file path
        self._database = peewee.SqliteDatabase(             # Setup storage
            database=self._file_path,
            pragmas={
                'foreign_keys': 1,
                'user_version': self._VERSION,
                'journal_mode': 'wal',
                'synchronous': 1,
            }
        )
        for database_model in self._MODELS:                 # Bind database to storage
            database_model.bind(self._database)
        self._database.create_tables(self._MODELS)          # Create tables

    # Validate file path --------------------------------------------------------------------------
    def _validate_file_path(self, existing):
        if not self._file_path:                            # Check if path is empty
            raise self.NoFilePathError("No File Selected")
        if existing and not self._file_path.exists():      # Check if file not found
            raise FileNotFoundError("File not found")
        if not existing and self._file_path.exists():      # Check if file exists
            raise FileExistsError("File already exists")
        if self._file_path.is_dir():                       # Check if file is folder
            raise IsADirectoryError("File path is a folder")
        if existing and self._file_path.exists():          # Check if storage is valid file
            db = peewee.SqliteDatabase(self._file_path)
            if db.pragma('user_version') != self._VERSION:
                raise self.InvalidFileError("Invalid File")

    @staticmethod
    def connect_changed_signal(callback):
        playhouse.signals.post_save.connect(callback)
        playhouse.signals.post_delete.connect(callback)

    @staticmethod
    def create_collection(self, id=None, parent=None, sort_order=0, name="", description="", color=""):
        List.create(
            id=id,
            parent=parent,
            sort_order=sort_order,
            name=name,
            description=description,
            color=color
        )

    def get_all_collections(self):
        return List.select()

    def update_collection(self, id, name="", color=""):
        pass


    def create_task(self, id, title, notes, start, due, done, recurrence, parent):
        pass
