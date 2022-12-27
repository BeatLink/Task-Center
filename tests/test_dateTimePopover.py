from unittest import TestCase
from datetime_popover import DateTimePicker, DateTimeButton
from datetime import datetime
from gi.repository import Gtk

# todo update test cases


class TestDateTimePopover(TestCase):
    def test__on_calendar_day_selected(self):
        popover = DateTimePicker()
        popover._calendar.select_day(0)
        self.assertEqual(False, popover._clear_date_button.get_sensitive())

        popover = DateTimePicker()
        popover._calendar.select_day(1)
        self.assertEqual(True, popover._clear_date_button.get_sensitive())

    def test__on_time_spinboxes_changed(self):
        popover = DateTimePicker()
        popover._hour_spinbox.set_value(1)
        self.assertEqual(True, popover._clear_time_button.get_sensitive())

        popover = DateTimePicker()
        popover._minute_spinbox.set_value(1)
        self.assertEqual(True, popover._clear_time_button.get_sensitive())

        popover = DateTimePicker()
        popover._hour_spinbox.set_value(0)
        popover._minute_spinbox.set_value(0)
        self.assertEqual(False, popover._clear_time_button.get_sensitive())

    def test__on_current_date_button_clicked(self):
        popover = DateTimePicker()
        initial_hour = popover.hour
        initial_minute = popover.minute
        now = datetime.now()
        popover.gtk_builder.get_object('current_date_button').clicked()
        self.assertEqual(now.year, popover.year)
        self.assertEqual(now.month, popover.month)
        self.assertEqual(now.day, popover.day)
        self.assertEqual(initial_hour, popover.hour)
        self.assertEqual(initial_minute, popover.minute)

    def test__on_clear_date_button_clicked(self):
        now = datetime.now()
        initial_year = now.year
        initial_month = now.month
        initial_hour = now.hour
        initial_minute = now.minute
        popover = DateTimePicker()
        popover.datetime = now
        popover._clear_date_button.clicked()
        self.assertEqual(initial_year, popover.year)
        self.assertEqual(initial_month, popover.month)
        self.assertEqual(0, popover.day)
        self.assertEqual(initial_hour, popover.hour)
        self.assertEqual(initial_minute, popover.minute)

    def test__on_current_time_button_clicked(self):
        popover = DateTimePicker()
        initial_year = popover.year
        initial_month = popover.month
        initial_day = popover.day
        now = datetime.now()
        popover.gtk_builder.get_object('current_time_button').clicked()
        self.assertEqual(initial_year, popover.year)
        self.assertEqual(initial_month, popover.month)
        self.assertEqual(initial_day, popover.day)
        self.assertEqual(now.hour, popover.hour)
        self.assertEqual(now.minute, popover.minute)

    def test__on_clear_time_button_clicked(self):
        now = datetime.now()
        initial_year = now.year
        initial_month = now.month
        initial_day = now.day
        popover = DateTimePicker()
        popover.datetime = now
        popover._clear_time_button.clicked()
        self.assertEqual(initial_year, popover.year)
        self.assertEqual(initial_month, popover.month)
        self.assertEqual(initial_day, popover.day)
        self.assertEqual(0, popover.hour)
        self.assertEqual(0, popover.minute)

    def test_update_clear_date_button(self):
        popover = DateTimePicker()
        popover._calendar.select_day(0)
        popover._update_clear_date_button()
        self.assertEqual(False, popover._clear_date_button.get_sensitive())

        popover = DateTimePicker()
        popover._calendar.select_day(1)
        popover._update_clear_date_button()
        self.assertEqual(True, popover._clear_date_button.get_sensitive())

    def test_update_clear_time_button(self):
        popover = DateTimePicker()
        popover._hour_spinbox.set_value(1)
        popover._update_clear_time_button()
        self.assertEqual(True, popover._clear_time_button.get_sensitive())

        popover = DateTimePicker()
        popover._minute_spinbox.set_value(1)
        popover._update_clear_time_button()
        self.assertEqual(True, popover._clear_time_button.get_sensitive())

        popover = DateTimePicker()
        popover._hour_spinbox.set_value(0)
        popover._minute_spinbox.set_value(0)
        popover._update_clear_time_button()
        self.assertEqual(False, popover._clear_time_button.get_sensitive())

    def test_update_stack_switcher_sensitivity(self):
        popover = DateTimePicker()
        popover._calendar.select_day(0)
        popover._update_stack_switcher_sensitivity()
        self.assertEqual(False, popover._stack_switcher.get_sensitive())

        popover = DateTimePicker()
        popover._calendar.select_day(1)
        popover._update_stack_switcher_sensitivity()
        self.assertEqual(True, popover._stack_switcher.get_sensitive())

    def test_raise_popover(self):
        popover = DateTimePicker()
        popover.raise_popover()
        self.assertEqual(True, popover._popover.get_visible())

    def test_set_relative_to(self):
        window = Gtk.Window()
        popover = DateTimePicker()
        popover.set_relative_to(window)
        self.assertEqual(window, popover._popover.get_relative_to())

    def test_connect_popover_closed_signals(self):
        function_ran = False

        def run_function(*_):
            nonlocal function_ran
            function_ran = True
        popover = DateTimePicker()
        popover.connect_popover_closed_signal(run_function)
        popover._popover.show()
        popover._popover.popdown()
        self.assertEqual(True, function_ran)

    def test_connect_datetime_changed_signal(self):
        def run_function(*_):
            nonlocal function_ran
            function_ran = True

        popover = DateTimePicker()
        popover.connect_datetime_changed_signal(run_function)
        function_ran = False
        popover.year = 2015
        self.assertEqual(True, function_ran)

        popover = DateTimePicker()
        popover.connect_datetime_changed_signal(run_function)
        function_ran = False
        popover.month = 10
        self.assertEqual(True, function_ran)

        popover = DateTimePicker()
        popover.connect_datetime_changed_signal(run_function)
        function_ran = False
        popover.day = 6
        self.assertEqual(True, function_ran)

        popover = DateTimePicker()
        popover.connect_datetime_changed_signal(run_function)
        function_ran = False
        popover.hour = 4
        self.assertEqual(True, function_ran)

        popover = DateTimePicker()
        popover.connect_datetime_changed_signal(run_function)
        function_ran = False
        popover.minute = 15
        self.assertEqual(True, function_ran)

    def test_select_current_date(self):
        popover = DateTimePicker()
        initial_hour = popover.hour
        initial_minute = popover.minute
        now = datetime.now()
        popover.select_current_date()
        self.assertEqual(now.year, popover.year)
        self.assertEqual(now.month, popover.month)
        self.assertEqual(now.day, popover.day)
        self.assertEqual(initial_hour, popover.hour)
        self.assertEqual(initial_minute, popover.minute)

    def test_clear_date(self):
        now = datetime.now()
        initial_year = now.year
        initial_month = now.month
        initial_hour = now.hour
        initial_minute = now.minute
        popover = DateTimePicker()
        popover.datetime = now
        popover.clear_date()
        self.assertEqual(initial_year, popover.year)
        self.assertEqual(initial_month, popover.month)
        self.assertEqual(0, popover.day)
        self.assertEqual(initial_hour, popover.hour)
        self.assertEqual(initial_minute, popover.minute)

    def test_select_current_time(self):
        popover = DateTimePicker()
        initial_year = popover.year
        initial_month = popover.month
        initial_day = popover.day
        now = datetime.now()
        popover.select_current_time()
        self.assertEqual(initial_year, popover.year)
        self.assertEqual(initial_month, popover.month)
        self.assertEqual(initial_day, popover.day)
        self.assertEqual(now.hour, popover.hour)
        self.assertEqual(now.minute, popover.minute)

    def test_clear_time(self):
        now = datetime.now()
        initial_year = now.year
        initial_month = now.month
        initial_day = now.day
        popover = DateTimePicker()
        popover.datetime = now
        popover.clear_time()
        self.assertEqual(initial_year, popover.year)
        self.assertEqual(initial_month, popover.month)
        self.assertEqual(initial_day, popover.day)
        self.assertEqual(0, popover.hour)
        self.assertEqual(0, popover.minute)

    def test_year(self):
        popover = DateTimePicker()
        popover.year = 2013
        self.assertEqual(2013, popover._calendar.get_date().year)

        popover = DateTimePicker()
        popover._calendar.select_month(1, 1996)
        self.assertEqual(1996, popover.year)

    def test_month(self):
        popover = DateTimePicker()
        popover.month = 4
        self.assertEqual(3, popover._calendar.get_date().month)

        popover = DateTimePicker()
        popover._calendar.select_month(8, 1996)
        self.assertEqual(9, popover.month)

    def test_day(self):
        popover = DateTimePicker()
        popover.day = 0
        self.assertEqual(0, popover._calendar.get_date().day)

        popover = DateTimePicker()
        popover.day = 15
        self.assertEqual(15, popover._calendar.get_date().day)

        popover = DateTimePicker()
        popover._calendar.select_day(0)
        self.assertEqual(0, popover.day)

        popover = DateTimePicker()
        popover._calendar.select_day(15)
        self.assertEqual(15, popover.day)

    def test_hour(self):
        popover = DateTimePicker()
        popover.hour = 4
        self.assertEqual(4, popover._hour_spinbox.get_value_as_int())

        popover = DateTimePicker()
        popover._hour_spinbox.set_value(21)
        self.assertEqual(21, popover.hour)

    def test_minute(self):
        popover = DateTimePicker()
        popover.minute = 4
        self.assertEqual(4, popover._minute_spinbox.get_value_as_int())

        popover = DateTimePicker()
        popover._minute_spinbox.set_value(21)
        self.assertEqual(21, popover.minute)

    def test_datetime(self):
        now = datetime.now()
        test_date = None
        popover = DateTimePicker()
        popover.datetime = test_date
        self.assertEqual(now.year, popover.year)
        self.assertEqual(now.month, popover.month)
        self.assertEqual(0, popover.day)
        self.assertEqual(0, popover.hour)
        self.assertEqual(0, popover.minute)

        popover = DateTimePicker()
        popover.day = 0
        self.assertEqual(None, popover.datetime)

        test_date = datetime(1993, 12, 31, 21, 45)
        popover = DateTimePicker()
        popover.datetime = test_date
        self.assertEqual(1993, popover.year)
        self.assertEqual(12, popover.month)
        self.assertEqual(31, popover.day)
        self.assertEqual(21, popover.hour)
        self.assertEqual(45, popover.minute)

        test_date = datetime(1993, 12, 31, 21, 45)
        popover = DateTimePicker()
        popover.year = 1993
        popover.month = 12
        popover.day = 31
        popover.hour = 21
        popover.minute = 45
        self.assertEqual(test_date, popover.datetime)


class TestDateTimeButton(TestCase):
    def test__on_button_clicked(self):
        dt_button = DateTimeButton()
        self.assertEqual(False, dt_button.picker._popover.get_visible())
        dt_button._button.clicked()
        self.assertEqual(True, dt_button.picker._popover.get_visible())

    def test_on_popover_closed(self):
        dt_button = DateTimeButton()
        self.assertEqual(None, dt_button.picker.datetime)
        self.assertEqual('Select Date', dt_button._button.get_label())

        dt_button.picker._popover.show()
        dt_button.picker._calendar.select_month(5, 2018)
        dt_button.picker._calendar.select_day(20)
        dt_button.picker._hour_spinbox.set_value(5)
        dt_button.picker._minute_spinbox.set_value(30)
        dt_button.picker._popover.popdown()

        self.assertEqual(datetime(2018, 6, 20, 5, 30), dt_button.picker.datetime)
        self.assertEqual('2018-06-20 at 05:30', dt_button._button.get_label())

    def test_set_date_button_label(self):
        no_date_format_string = "Test No Date Set"
        dt_button = DateTimeButton(no_date_string=no_date_format_string)
        dt_button.datetime = None
        dt_button._set_date_button_label()
        self.assertEqual(no_date_format_string, dt_button._button.get_label())

        # if date alone. label should be date label
        date_alone_string = "%m,%d,%Y"
        dt_button = DateTimeButton(date_format_string=date_alone_string)
        dt_button.picker.datetime = datetime(2018, 7, 5)
        dt_button._set_date_button_label()
        self.assertEqual('07,05,2018', dt_button._button.get_label())

        # if time is set. label should be datetime label
        date_alone_string = "%m,%d,%Y"
        datetime_label = "%Y/%m/%d at %H:%M:%S"
        dt_button = DateTimeButton(date_format_string=date_alone_string, datetime_format_string=datetime_label)
        dt_button.picker.datetime = datetime(2018, 7, 5, 21, 43)
        dt_button._set_date_button_label()
        self.assertEqual('2018/07/05 at 21:43:00', dt_button._button.get_label())
