# !/bin/env python3
import arrow

# MonthWeekday #########################################################################################################
class WeekdayOfMonth:
    """
    Class that represents the specific weekday of the month the task will repeat on (eg, first sunday, last friday)

    ordinal: An integer representing the ordinal of the day. None=unset, 0=First, 1=Second, 2=Third, 3=Fourth, -1=Last
    weekday: An integer representing the day of the week. , None=unset, 0=monday, 1=tuesday, 2=wednesday, 3=thursday,
            4=friday, 5=saturday, 6=sunday
    """
    def __init__(self, ordinal=None, weekday=None):
        self._ordinal = None
        self._weekday = None
        self.ordinal = ordinal
        self.weekday = weekday

    # Ordinal property -------------------------------------------------------------------------------------------------
    @property
    def ordinal(self):
        return self._ordinal

    @ordinal.setter
    def ordinal(self, ordinal):
        if ordinal in (-1, 0, 1, 2, 3, None):
            self._ordinal = ordinal
        else:
            raise ValueError("Ordinal must be an integer between -1 and 3, or None to unset")

    # Weekday property -------------------------------------------------------------------------------------------------
    @property
    def weekday(self):
        return self._weekday

    @weekday.setter
    def weekday(self, weekday):
        valid_weekdays = (0, 1, 2, 3, 4, 5, 6, None)
        if weekday in valid_weekdays:
            self._weekday = weekday
        else:
            raise ValueError("Weekday must be an integer between 0-6, or None to unset")

    @property
    def dict(self):
        return {
                'ordinal': self.ordinal,
                'weekday': self.weekday
            }

    # String property --------------------------------------------------------------------------------------------------

    def get_next_date(self, initial_date, increment):
        """
        This method gets the next valid weekday of the month. It does it by doing the following
        * Find the 2 valid months: the initial month and the incremented month.
        * Find all matching weekdays within the month and save to lists
        * Use the ordinal as the index to the matching weekday lists to get the correct weekdays for both months
        * Add the 2 correct weekdays to a final lists
        * sorts the lists and then chooses the soonest date that comes after the initial date
        """
        def generate_valid_weekdays():
            for month in initial_date, initial_date.shift(months=increment):
                month_start = month.floor('month')
                month_end = month.ceil('month')
                weekdays_in_this_month = [
                    day for day in month.range('day', month_start, month_end) if day.weekday() == self.weekday]
                specific_weekday = weekdays_in_this_month[self.ordinal]
                yield specific_weekday
        for weekday in sorted(list(generate_valid_weekdays())):
            if weekday > initial_date:
                return weekday.replace(hour=initial_date.hour, minute=initial_date.minute, second=initial_date.second)


# Recurrence ###########################################################################################################
class Recurrence:
    """
    enabled: Boolean to indicate whether the task recurs or not
    interval: String representing the time interval. Valid values are 'minute', 'hour', 'day', 'week', 'month', 'year'
    increment: Integer representing the number of time intervals. Valid values are positive integers
    weekdays: Returns a set of integers ranging from 0-6 representing the enabled days. 0=Mon, 1=Tue...5=Sat, 6=Sun
    weekday_of_month: See WeekdayOfMonth for more info
    type: String indicating the stop criteria. Valid Values are 'date', 'number' and 'never'
    date: Arrow object representing the date the task should stop repeating.
    number: Integer representing the number of times before task stops repeating.
    """

    def __init__(self, enabled=False, interval='minute', increment=1, weekdays=None, weekday_of_month=None,
                 stop_type='never', stop_date=None, stop_number=0):
        self.enabled = enabled
        self.interval = interval
        self.increment = increment
        self.weekdays = weekdays if weekdays else []
        self.weekday_of_month = WeekdayOfMonth(**weekday_of_month) if weekday_of_month else WeekdayOfMonth()
        self.stop_type = stop_type
        self.stop_date = stop_date
        self.stop_number = stop_number

    def get_next_date(self, initial_date):
        """Gets the next date and time after the initial date that the task would repeat"""
        new_date = initial_date
        if self.enabled and initial_date <= arrow.now():
            if self.interval == 'week' and self.weekdays:
                new_date = self.weekdays.get_next_date(initial_date, self.increment)
                def generate_valid_weekdays():
                    for week in [initial_date, initial_date.shift(weeks=self.increment)]:
                        week_start = week.floor('week').shift(days=-1)
                        for weekday_number in self.weekdays:
                            valid_weekday = week_start.shift(weekday=weekday_number)
                            yield valid_weekday
                for weekday in sorted(list(generate_valid_weekdays())):
                    if weekday > initial_date:
                        return weekday.replace(hour=initial_date.hour, minute=initial_date.minute,
                                               second=initial_date.second)
            elif (
                    self.interval == 'month') and (
                    self.weekday_of_month.weekday is not None) and (
                    self.weekday_of_month.ordinal is not None):
                new_date = self.weekday_of_month.get_next_date(initial_date, self.increment)
            else:
                new_date = initial_date.shift(**{self.interval + 's': self.increment})
        if self.stop_type == 'date' and self.stop_date and self.stop_date <= arrow.now():
            self.enabled = False
            self.stop_type = 'never'
        elif self.stop_type == 'number':
            if self.stop_number <= 1:
                self.enabled = False
                self.stop_type = 'never'
            elif self.stop_number > 1:
                self.stop_number -= 1
        return new_date

    @property
    def string(self):
        """Returns the recurrence in a human-readable format. Eg Every week on thursdays"""
        if self.enabled:
            string = f'every {str(self.increment)} {self.interval}s' if self.increment > 1 else f'every {self.interval}'
            if self.interval == 'week' and self.weekdays.weekdays_list:
                weekday_string = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
                weekdays = [weekday_string[index].capitalize() for index in self.weekdays.weekdays_list]
                if 'Sunday' in weekdays:
                    weekdays.insert(0, weekdays.pop())
                weekdays = [day[:3] for day in weekdays]
                if len(weekdays) > 1:
                    weekdays_string = f"{', '.join(weekdays)} and {weekdays.pop()}"
                elif len(weekdays) == 1:
                    weekdays_string = weekdays[0]
                else:
                    weekdays_string = ''
                string += f' on {weekdays_string}'
            elif self.interval == 'month':
                if self.weekday_of_month.weekday is not None and self.weekday_of_month.ordinal is not None:
                    ordinal = ('first', 'second', 'third', 'fourth', 'last')
                    weekday = ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')
                    return f'on the {ordinal[self.weekday_of_month.ordinal]} {weekday[self.weekday_of_month.weekday].capitalize()}'
                else:
                    return ''
            return string
        else:
            return ''

# Task ################################################################################################################
class Task:
    def __init__(
            self,
            summary="",
            description="",
            start_date=None,
            due_date=None,
            done_date=None,
            recurrence=None,
            created_date=None,
            last_modified_date=None,
            percent_complete="",
            priority="",
            status="",
            tags="",
            parent=None):
        self.summary = summary
        self.description = description
        self.start_date = start_date
        self.due_date = due_date
        self.done_date = done_date
        self.recurrence = recurrence #if recurrence else Recurrence()
        self.created_date = created_date
        self.last_modified_date = last_modified_date
        self.percent_complete = percent_complete
        self.priority = priority
        self.status = status
        self.tags=tags
        self.parent = parent
