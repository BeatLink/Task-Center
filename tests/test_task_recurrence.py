#!/usr/bin/env python3.7

import arrow
from unittest import TestCase
from xtasks.app.logic.task_recurrence import WeekDays, WeekdayOfMonth, StopInfo, Recurrence


class TestWeekDays(TestCase):

    def test_dict(self):
        def test_some_enabled():
            self.weekdays = WeekDays()
            self.weekdays.sunday = True
            self.weekdays.monday = True
            self.weekdays.wednesday = True
            self.weekdays.thursday = True
            self.weekdays.saturday = True
            self.assertEqual(
                {
                    'sunday': True,
                    'monday': True,
                    'tuesday': False,
                    'wednesday': True,
                    'thursday': True,
                    'friday': False,
                    'saturday': True
                },
                self.weekdays.dict)

        def test_one_enabled():
            self.weekdays = WeekDays()
            self.weekdays.monday = True
            self.assertEqual(
                {
                    'sunday': False,
                    'monday': True,
                    'tuesday': False,
                    'wednesday': False,
                    'thursday': False,
                    'friday': False,
                    'saturday': False
                },
                self.weekdays.dict)

        def test_none_enabled():
            self.weekdays = WeekDays()
            self.assertEqual(
                {
                    'sunday': False,
                    'monday': False,
                    'tuesday': False,
                    'wednesday': False,
                    'thursday': False,
                    'friday': False,
                    'saturday': False
                },
                self.weekdays.dict)

        test_some_enabled()
        test_one_enabled()
        test_none_enabled()

    def test_arrow_set(self):
        def test_some_enabled():
            self.weekdays = WeekDays()
            self.weekdays.sunday = True
            self.weekdays.monday = True
            self.weekdays.wednesday = True
            self.weekdays.thursday = True
            self.weekdays.saturday = True
            self.assertEqual({0, 2, 3, 5, 6}, self.weekdays.arrow_set)

        def test_one_enabled():
            self.weekdays = WeekDays()
            self.weekdays.monday = True
            self.assertEqual({0}, self.weekdays.arrow_set)

        def test_none_enabled():
            self.weekdays = WeekDays()
            self.assertEqual(set(), self.weekdays.arrow_set)

        test_some_enabled()
        test_one_enabled()
        test_none_enabled()

    def test_string_list(self):
        def test_some_enabled():
            self.weekdays = WeekDays()
            self.weekdays.sunday = True
            self.weekdays.monday = True
            self.weekdays.wednesday = True
            self.weekdays.thursday = True
            self.weekdays.saturday = True
            self.assertEqual(
                ['Sunday', 'Monday', 'Wednesday', 'Thursday', 'Saturday'], self.weekdays.string_list)

        def test_one_enabled():
            self.weekdays = WeekDays()
            self.weekdays.monday = True
            self.assertEqual(['Monday'], self.weekdays.string_list)

        def test_none_enabled():
            self.weekdays = WeekDays()
            self.assertEqual([], self.weekdays.string_list)

        test_some_enabled()
        test_one_enabled()
        test_none_enabled()

    def test_string(self):
        def test_some_enabled():
            self.weekdays = WeekDays()
            self.weekdays.sunday = True
            self.weekdays.monday = True
            self.weekdays.wednesday = True
            self.weekdays.thursday = True
            self.weekdays.saturday = True
            self.assertEqual("Sun, Mon, Wed, Thu and Sat", self.weekdays.string)

        def test_one_enabled():
            self.weekdays = WeekDays()
            self.weekdays.monday = True
            self.assertEqual("Mon", self.weekdays.string)

        def test_none_enabled():
            self.weekdays = WeekDays()
            self.assertEqual('', self.weekdays.string)

        test_some_enabled()
        test_one_enabled()
        test_none_enabled()

    def test_get_next_date(self):
        weekday = WeekDays(sunday=True, monday=True, thursday=True)

        initial_date = arrow.Arrow(year=2019, month=7, day=1, hour=10, minute=3, second=30)
        new_date = arrow.Arrow(year=2019, month=7, day=4, hour=10, minute=3, second=30)
        self.assertEqual(new_date, weekday.get_next_date(initial_date=initial_date, increment=2))

        initial_date = arrow.Arrow(year=2019, month=7, day=5, hour=10, minute=3, second=30)
        new_date = arrow.Arrow(year=2019, month=7, day=14, hour=10, minute=3, second=30)
        self.assertEqual(new_date, weekday.get_next_date(initial_date=initial_date, increment=2))

        initial_date = arrow.Arrow(year=2018, month=10, day=9, hour=10, minute=3, second=30)
        new_date = arrow.Arrow(year=2018, month=10, day=11, hour=10, minute=3, second=30)
        self.assertEqual(new_date, weekday.get_next_date(initial_date=initial_date, increment=2))


class TestWeekdayOfMonth(TestCase):

    def test_ordinal(self):
        wom = WeekdayOfMonth()

        with self.assertRaises(ValueError):
            wom.ordinal = -2

        wom.ordinal = -1
        self.assertEqual(-1, wom.ordinal)

        wom.ordinal = None
        self.assertEqual(None, wom.ordinal)

        wom.ordinal = 0
        self.assertEqual(0, wom.ordinal)

        wom.ordinal = 1
        self.assertEqual(1, wom.ordinal)

        wom.ordinal = 2
        self.assertEqual(2, wom.ordinal)

        wom.ordinal = 3
        self.assertEqual(3, wom.ordinal)

        with self.assertRaises(ValueError):
            wom.ordinal = 4

        with self.assertRaises(ValueError):
            wom.ordinal = 'hello'

    def test_weekday(self):
        with self.assertRaises(ValueError):
            wom = WeekdayOfMonth()
            wom.weekday = 'hello'

        with self.assertRaises(ValueError):
            wom = WeekdayOfMonth()
            wom.weekday = 7

        with self.assertRaises(ValueError):
            wom = WeekdayOfMonth()
            wom.weekday = -1

        wom = WeekdayOfMonth()
        wom.weekday = 6
        self.assertEqual(6, wom.weekday)

        wom = WeekdayOfMonth()
        wom.weekday = 0
        self.assertEqual(0, wom.weekday)

        wom = WeekdayOfMonth()
        wom.weekday = 1
        self.assertEqual(1, wom.weekday)

        wom = WeekdayOfMonth()
        wom.weekday = 2
        self.assertEqual(2, wom.weekday)

        wom = WeekdayOfMonth()
        wom.weekday = 3
        self.assertEqual(3, wom.weekday)

        wom = WeekdayOfMonth()
        wom.weekday = 4
        self.assertEqual(4, wom.weekday)

        wom = WeekdayOfMonth()
        wom.weekday = 5
        self.assertEqual(5, wom.weekday)

        wom = WeekdayOfMonth()
        wom.weekday = 6
        self.assertEqual(6, wom.weekday)

        wom = WeekdayOfMonth()
        wom.weekday = None
        self.assertEqual(None, wom.weekday)

    def test_string(self):
        wom = WeekdayOfMonth()
        self.assertEqual('', wom.string)

        wom = WeekdayOfMonth()
        wom.ordinal = None
        wom.weekday = None
        self.assertEqual('', wom.string)

        wom = WeekdayOfMonth()
        wom.ordinal = 0
        wom.weekday = 6
        self.assertEqual('the first Sunday', wom.string)

        wom = WeekdayOfMonth()
        wom.ordinal = 1
        wom.weekday = 6
        self.assertEqual('the second Sunday', wom.string)

        wom = WeekdayOfMonth()
        wom.ordinal = 2
        wom.weekday = 6
        self.assertEqual('the third Sunday', wom.string)

        wom = WeekdayOfMonth()
        wom.ordinal = 3
        wom.weekday = 6
        self.assertEqual('the fourth Sunday', wom.string)

        wom = WeekdayOfMonth()
        wom.ordinal = -1
        wom.weekday = 6
        self.assertEqual('the last Sunday', wom.string)

    def test_get_next_date(self):
        # find the first sunday in the month, every 2 months
        wom = WeekdayOfMonth()
        wom.ordinal = 0
        wom.weekday = 6
        initial_date = arrow.Arrow(year=2019, month=7, day=1, hour=10, minute=3, second=30)
        new_date = arrow.Arrow(year=2019, month=7, day=7, hour=10, minute=3, second=30)
        self.assertEqual(new_date, wom.get_next_date(initial_date, increment=2))

        # find the first sunday in the month, every 2 months
        wom = WeekdayOfMonth()
        wom.ordinal = 0
        wom.weekday = 6
        initial_date = arrow.Arrow(year=2019, month=7, day=8, hour=10, minute=3, second=30)
        new_date = arrow.Arrow(year=2019, month=9, day=1, hour=10, minute=3, second=30)
        self.assertEqual(new_date, wom.get_next_date(initial_date, increment=2))

        # find the third saturday in the month, every 2 months
        wom = WeekdayOfMonth()
        wom.ordinal = 2
        wom.weekday = 5
        initial_date = arrow.Arrow(year=2019, month=7, day=1, hour=10, minute=3, second=30)
        new_date = arrow.Arrow(year=2019, month=7, day=20, hour=10, minute=3, second=30)
        self.assertEqual(new_date, wom.get_next_date(initial_date, increment=2))

        # find the third saturday in the month, every 2 months
        wom = WeekdayOfMonth()
        wom.ordinal = 2
        wom.weekday = 5
        initial_date = arrow.Arrow(year=2019, month=8, day=20, hour=10, minute=3, second=30)
        new_date = arrow.Arrow(year=2019, month=10, day=19, hour=10, minute=3, second=30)
        self.assertEqual(new_date, wom.get_next_date(initial_date, increment=2))

        # find the last wednesday in the month, every 3 months
        wom = WeekdayOfMonth()
        wom.ordinal = -1
        wom.weekday = 2
        initial_date = arrow.Arrow(year=2019, month=8, day=20, hour=10, minute=3, second=30)
        new_date = arrow.Arrow(year=2019, month=8, day=28, hour=10, minute=3, second=30)
        self.assertEqual(new_date, wom.get_next_date(initial_date, increment=3))

        # find the last wednesday in the month, every 3 months
        wom = WeekdayOfMonth()
        wom.ordinal = -1
        wom.weekday = 2
        initial_date = arrow.Arrow(year=2019, month=8, day=30, hour=10, minute=3, second=30)
        new_date = arrow.Arrow(year=2019, month=11, day=27, hour=10, minute=3, second=30)
        self.assertEqual(new_date, wom.get_next_date(initial_date, increment=3))


class TestStopInfo(TestCase):

    def test_should_stop(self):
        stop = StopInfo()
        stop.type = 'never'
        self.assertEqual(False, stop.should_stop())

        stop = StopInfo()
        stop.type = 'date'
        stop.date = arrow.now().shift(days=-1)  # current time yesterday
        self.assertEqual(True, stop.should_stop())

        stop = StopInfo()
        stop.type = 'date'
        stop.date = arrow.now()
        self.assertEqual(True, stop.should_stop())

        stop = StopInfo()
        stop.type = 'date'
        stop.date = arrow.now().shift(days=1)  # current time tomorrow
        self.assertEqual(False, stop.should_stop())

        stop = StopInfo()
        stop.type = 'date'
        stop.date = None
        self.assertEqual(False, stop.should_stop())

        stop = StopInfo()
        stop.type = 'number'
        stop.number = -1
        self.assertEqual(True, stop.should_stop())

        stop = StopInfo()
        stop.type = 'number'
        stop.number = 0
        self.assertEqual(True, stop.should_stop())

        stop = StopInfo()
        stop.type = 'number'
        stop.number = 1
        self.assertEqual(True, stop.should_stop())

        stop = StopInfo()
        stop.type = 'number'
        stop.number = 2
        self.assertEqual(False, stop.should_stop())

        stop = StopInfo()
        stop.type = 'number'
        stop.number = None
        self.assertEqual(False, stop.should_stop())

    def test_update_number(self):
        stop = StopInfo()
        stop.type = 'number'
        stop.number = -1
        stop.update_number()
        self.assertEqual(-1, stop.number)

        stop = StopInfo()
        stop.type = 'number'
        stop.number = 0
        stop.update_number()
        self.assertEqual(0, stop.number)

        stop = StopInfo()
        stop.type = 'number'
        stop.number = 1
        stop.update_number()
        self.assertEqual(1, stop.number)

        stop = StopInfo()
        stop.type = 'number'
        stop.number = 2
        stop.update_number()
        self.assertEqual(1, stop.number)

        stop = StopInfo()
        stop.type = 'number'
        stop.number = 3
        stop.update_number()
        self.assertEqual(2, stop.number)


class TestRecurrence(TestCase):

    def test_get_next_date(self):
        def test_disabled():
            initial_date = arrow.Arrow(year=2018, month=5, day=1, hour=10, minute=3, second=30)
            recurrence_object = Recurrence(enabled=False)
            self.assertEqual(recurrence_object.get_next_date(initial_date), initial_date)

        def test_minutes():
            # test minutes
            initial_date = arrow.Arrow(year=2018, month=5, day=1, hour=10, minute=3, second=30)
            new_date = arrow.Arrow(year=2018, month=5, day=1, hour=10, minute=4, second=30)
            recurrence_object = Recurrence(enabled=True, increment=1, interval='minute')
            self.assertEqual(recurrence_object.get_next_date(initial_date), new_date)
            initial_date = arrow.Arrow(year=2018, month=5, day=1, hour=10, minute=3, second=30)
            new_date = arrow.Arrow(year=2018, month=5, day=1, hour=10, minute=5, second=30)
            recurrence_object = Recurrence(enabled=True, increment=2, interval='minute')
            self.assertEqual(recurrence_object.get_next_date(initial_date), new_date)

        def test_hours():
            # test hours
            initial_date = arrow.Arrow(year=2018, month=5, day=1, hour=10, minute=3, second=30)
            new_date = arrow.Arrow(year=2018, month=5, day=1, hour=11, minute=3, second=30)
            recurrence_object = Recurrence(enabled=True, increment=1, interval='hour')
            self.assertEqual(recurrence_object.get_next_date(initial_date), new_date)
            initial_date = arrow.Arrow(year=2018, month=5, day=1, hour=10, minute=3, second=30)
            new_date = arrow.Arrow(year=2018, month=5, day=1, hour=12, minute=3, second=30)
            recurrence_object = Recurrence(enabled=True, increment=2, interval='hour')
            self.assertEqual(recurrence_object.get_next_date(initial_date), new_date)

        def test_days():
            # test days
            initial_date = arrow.Arrow(year=2018, month=5, day=1, hour=10, minute=3, second=30)
            new_date = arrow.Arrow(year=2018, month=5, day=2, hour=10, minute=3, second=30)
            recurrence_object = Recurrence(enabled=True, increment=1, interval='day')
            self.assertEqual(recurrence_object.get_next_date(initial_date), new_date)
            initial_date = arrow.Arrow(year=2018, month=5, day=1, hour=10, minute=3, second=30)
            new_date = arrow.Arrow(year=2018, month=5, day=3, hour=10, minute=3, second=30)
            recurrence_object = Recurrence(enabled=True, increment=2, interval='day')
            self.assertEqual(recurrence_object.get_next_date(initial_date), new_date)

        def test_weeks():
            initial_date = arrow.Arrow(year=2018, month=5, day=1, hour=10, minute=3, second=30)
            new_date = arrow.Arrow(year=2018, month=5, day=8, hour=10, minute=3, second=30)
            recurrence_object = Recurrence()
            recurrence_object.enabled = True
            recurrence_object.increment = 1
            recurrence_object.interval = 'week'
            self.assertEqual(recurrence_object.get_next_date(initial_date), new_date)

            initial_date = arrow.Arrow(year=2018, month=10, day=1, hour=10, minute=3, second=30)
            new_date = arrow.Arrow(year=2018, month=10, day=15, hour=10, minute=3, second=30)
            recurrence_object = Recurrence()
            recurrence_object.enabled = True
            recurrence_object.increment = 2
            recurrence_object.interval = 'week'
            self.assertEqual(recurrence_object.get_next_date(initial_date), new_date)

            initial_date = arrow.Arrow(year=2018, month=10, day=9, hour=10, minute=3, second=30)
            new_date = arrow.Arrow(year=2018, month=10, day=11, hour=10, minute=3, second=30)
            recurrence_object = Recurrence(enabled=True, increment=2, interval='week')
            recurrence_object.weekdays.monday = True
            recurrence_object.weekdays.thursday = True
            self.assertEqual(recurrence_object.get_next_date(initial_date), new_date)

            initial_date = arrow.Arrow(year=2018, month=10, day=9, hour=10, minute=3, second=30)
            new_date = arrow.Arrow(year=2018, month=10, day=21, hour=10, minute=3, second=30)
            recurrence_object = Recurrence(enabled=True, increment=2, interval='week')
            recurrence_object.weekdays.monday = True
            recurrence_object.weekdays.sunday = True
            self.assertEqual(recurrence_object.get_next_date(initial_date), new_date)

        def test_months():
            # test months
            initial_date = arrow.Arrow(year=2018, month=5, day=1, hour=10, minute=3, second=30)
            new_date = arrow.Arrow(year=2018, month=6, day=1, hour=10, minute=3, second=30)
            recurrence_object = Recurrence(enabled=True, increment=1, interval='month')
            self.assertEqual(new_date, recurrence_object.get_next_date(initial_date))

            initial_date = arrow.Arrow(year=2018, month=5, day=1, hour=10, minute=3, second=30)
            new_date = arrow.Arrow(year=2018, month=7, day=1, hour=10, minute=3, second=30)
            recurrence_object = Recurrence(enabled=True, increment=2, interval='month')
            self.assertEqual(new_date, recurrence_object.get_next_date(initial_date))

            initial_date = arrow.Arrow(year=2018, month=5, day=1, hour=10, minute=3, second=30)
            new_date = arrow.Arrow(year=2018, month=5, day=2, hour=10, minute=3, second=30)
            recurrence_object = Recurrence(enabled=True, increment=2, interval='month')
            recurrence_object.weekday_of_month.ordinal = 0
            recurrence_object.weekday_of_month.weekday = 2
            self.assertEqual(new_date, recurrence_object.get_next_date(initial_date))

            initial_date = arrow.Arrow(year=2018, month=5, day=1, hour=10, minute=3, second=30)
            new_date = arrow.Arrow(year=2018, month=5, day=10, hour=10, minute=3, second=30)
            recurrence_object = Recurrence(enabled=True, increment=2, interval='month')
            recurrence_object.weekday_of_month.ordinal = 1
            recurrence_object.weekday_of_month.weekday = 3
            self.assertEqual(new_date, recurrence_object.get_next_date(initial_date))

            initial_date = arrow.Arrow(year=2019, month=8, day=20, hour=10, minute=3, second=30)
            new_date = arrow.Arrow(year=2019, month=10, day=18, hour=10, minute=3, second=30)
            recurrence_object = Recurrence(enabled=True, increment=2, interval='month')
            recurrence_object.weekday_of_month.ordinal = 2
            recurrence_object.weekday_of_month.weekday = 4
            self.assertEqual(new_date, recurrence_object.get_next_date(initial_date))

            initial_date = arrow.Arrow(year=2019, month=8, day=21, hour=2, minute=45, second=30)
            new_date = arrow.Arrow(year=2019, month=8, day=29, hour=2, minute=45, second=30)
            recurrence_object = Recurrence(enabled=True, increment=1, interval='month')
            recurrence_object.weekday_of_month.ordinal = -1
            recurrence_object.weekday_of_month.weekday = 3
            self.assertEqual(new_date, recurrence_object.get_next_date(initial_date))

        def test_years():
            initial_date = arrow.Arrow(year=2018, month=5, day=1, hour=10, minute=3, second=30)
            new_date = arrow.Arrow(year=2019, month=5, day=1, hour=10, minute=3, second=30)
            recurrence_object = Recurrence(enabled=True, increment=1, interval='year')
            self.assertEqual(recurrence_object.get_next_date(initial_date), new_date)
            initial_date = arrow.Arrow(year=2018, month=5, day=1, hour=10, minute=3, second=30)
            new_date = arrow.Arrow(year=2020, month=5, day=1, hour=10, minute=3, second=30)
            recurrence_object = Recurrence(enabled=True, increment=2, interval='year')
            self.assertEqual(recurrence_object.get_next_date(initial_date), new_date)

        test_disabled()
        test_minutes()
        test_hours()
        test_days()
        test_weeks()
        test_months()
        test_years()

    def test_string(self):
        def test_disabled():
            recurrence_object = Recurrence(enabled=False)
            self.assertEqual(recurrence_object.string, '')

        def test_minutes():
            recurrence_object = Recurrence(enabled=True, interval='minute', increment=1)
            self.assertEqual('every minute', recurrence_object.string)
            recurrence_object = Recurrence(enabled=True, interval='minute', increment=2)
            self.assertEqual('every 2 minutes', recurrence_object.string)

        def test_hours():
            recurrence_object = Recurrence(enabled=True, interval='hour', increment=1)
            self.assertEqual('every hour', recurrence_object.string)
            recurrence_object = Recurrence(enabled=True, interval='hour', increment=2)
            self.assertEqual('every 2 hours', recurrence_object.string)

        def test_days():
            recurrence_object = Recurrence(enabled=True, interval='day', increment=1)
            self.assertEqual('every day', recurrence_object.string)
            recurrence_object = Recurrence(enabled=True, interval='day', increment=2)
            self.assertEqual('every 2 days', recurrence_object.string)

        def test_weeks():
            recurrence_object = Recurrence(enabled=True, interval='week', increment=1)
            self.assertEqual('every week', recurrence_object.string)

            recurrence_object = Recurrence(enabled=True, interval='week', increment=2)
            self.assertEqual('every 2 weeks', recurrence_object.string)

            recurrence_object = Recurrence(enabled=True, interval='week', increment=1)
            recurrence_object.weekdays.monday = True
            recurrence_object.weekdays.thursday = True
            recurrence_object.weekdays.saturday = True
            recurrence_object.weekdays.sunday = True
            self.assertEqual('every week on Sun, Mon, Thu and Sat', recurrence_object.string)

            recurrence_object = Recurrence(enabled=True, interval='week', increment=2)
            recurrence_object.weekdays.monday = True
            recurrence_object.weekdays.thursday = True
            recurrence_object.weekdays.saturday = True
            recurrence_object.weekdays.sunday = True
            self.assertEqual('every 2 weeks on Sun, Mon, Thu and Sat', recurrence_object.string)

            recurrence_object = Recurrence(enabled=True, interval='week', increment=1)
            recurrence_object.weekdays.monday = True
            recurrence_object.weekdays.sunday = True
            self.assertEqual('every week on Sun and Mon', recurrence_object.string)

            recurrence_object = Recurrence(enabled=True, interval='week', increment=1)
            recurrence_object.weekdays.monday = True
            self.assertEqual('every week on Mon', recurrence_object.string)

        def test_months():
            recurrence_object = Recurrence(enabled=True, interval='month', increment=1)
            self.assertEqual('every month', recurrence_object.string)

            recurrence_object = Recurrence(enabled=True, interval='month', increment=2)
            self.assertEqual('every 2 months', recurrence_object.string)

            recurrence_object = Recurrence(enabled=True, interval='month', increment=1)
            recurrence_object.weekday_of_month.ordinal = 0
            recurrence_object.weekday_of_month.weekday = 5
            self.assertEqual('every month on the first Saturday', recurrence_object.string)

        def test_years():
            recurrence_object = Recurrence(enabled=True, interval='year', increment=1)
            self.assertEqual('every year', recurrence_object.string)
            recurrence_object = Recurrence(enabled=True, interval='year', increment=2)
            self.assertEqual('every 2 years', recurrence_object.string)

        test_disabled()
        test_minutes()
        test_hours()
        test_days()
        test_weeks()
        test_months()
        test_years()
