#!/usr/bin/env python3
"""
Name: DatetimeButton

Description:
    This class implements a Python GTK button to select dates and times. Once clicked, a popover will be raised to
    select dates and times. Dates are set using a calendar widget with buttons to clear the date and select the current
    date. Times are set using an hour and a minute spinbox with buttons to clear the time or set the current time.
    Note however that times are represented using 24 Hours instead of AM/PM. Also, the minutes are limited to increments
    of 5.

Usage:
    Instantiate the class then add the DateTimeButton.button to your GUI where needed. The datetime value can
    be set and retrieved using the DateTimeButton.get_datetime() and DateTimeButton.set_datetime() methods respectively.

License: GNU GPL3+
"""

# Imports ##############################################################################################################
import pathlib
from datetime import datetime
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Helper logic #####################################################################################################
def _enlarge_spinbox_font(spinbutton):
    css = b'''spinbutton {font-size: 400%;}'''
    style_provider = Gtk.CssProvider()
    style_provider.load_from_data(css)
    spinbox_style_context = spinbutton.get_style_context()
    spinbox_style_context.add_provider(style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def _show_leading_zeros(spinbutton):
    adjustment = spinbutton.get_adjustment()
    value = int(adjustment.get_value())
    spinbutton.set_text(f'{value:02d}')
    return True


# DateTimeButton Class ################################################################################################
class DateTimeButton:
    def __init__(
            self, date_format_string='%Y-%m-%d',
            time_format_string="%Y-%m-%d at %H:%M",
            no_date_string="No Date Selected"):

        self.date_format_string = date_format_string
        self.time_format_string = time_format_string
        self.no_date_string = no_date_string

        glade_file_path = str(pathlib.Path(__file__).resolve().parent / "datetime_button.glade")
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(glade_file_path)
        self.gtk_builder.connect_signals(self)

        # Widget Setup
        self.button = self.gtk_builder.get_object("button")
        self.popover = self.gtk_builder.get_object('popover')
        self.stack = self.gtk_builder.get_object("stack")
        self.stack_switcher = self.gtk_builder.get_object('stack_switcher')
        self.calendar = self.gtk_builder.get_object('calendar')
        self.clear_date_button = self.gtk_builder.get_object('clear_date_button')
        self.hour_spinbox = self.gtk_builder.get_object('hour_spinbox')
        self.minute_spinbox = self.gtk_builder.get_object('minute_spinbox')
        self.clear_time_button = self.gtk_builder.get_object('clear_time_button')

        # Spinbox setup
        for spinbox in [self.hour_spinbox, self.minute_spinbox]:
            _enlarge_spinbox_font(spinbox)
            spinbox.connect('output', _show_leading_zeros)
        self._on_popover_closed()

    # element handlers -------------------------------------------------------------------------------------------------
    def _on_button_clicked(self, *_):
        self.popover.show()
        self.popover.show_all()

    def _on_calendar_day_selected(self, *_):
        self.clear_date_button.set_sensitive(True if self.calendar.get_date().day else False)
        self.stack_switcher.set_sensitive(True if self.calendar.get_date().day else False)
        if not self.calendar.get_date().day:
            self.stack.set_visible_child_name('date')

    def _on_time_spinboxes_changed(self, *_):
        hour = self.hour_spinbox.get_value_as_int()
        minute = self.minute_spinbox.get_value_as_int()
        sensitive = True if hour or minute else False
        self.clear_time_button.set_sensitive(sensitive)

    def _on_current_date_button_clicked(self, *_):
        current_date = datetime.now()
        self.calendar.select_month(current_date.month - 1 , current_date.year)
        self.calendar.select_day(current_date.day)

    def _on_clear_date_button_clicked(self, *_):
        current_date = datetime.now()
        self.calendar.select_month(current_date.month - 1, current_date.year)
        self.calendar.select_day(0)

    def _on_current_time_button_clicked(self, *_):
        current_time = datetime.now()
        self.hour_spinbox.set_value(current_time.hour)
        self.minute_spinbox.set_value(5 * round(current_time.minute/5))
        self._on_time_spinboxes_changed()

    def _on_clear_time_button_clicked(self, *_):
        self.hour_spinbox.set_value(0)
        self.minute_spinbox.set_value(0)
        self._on_time_spinboxes_changed()

    def _on_popover_closed(self, *_):
        datetime_obj = self.get_datetime()
        if datetime_obj:
            time_present = self.get_datetime().minute != 0 and self.get_datetime().hour != 0
            format_string = self.time_format_string if time_present else self.date_format_string
            self.button.set_label(datetime_obj.strftime(format_string))
        else:
            self.button.set_label(self.no_date_string)

    # datetime properties ----------------------------------------------------------------------------------------------
    def get_datetime(self):
        year = self.calendar.get_date().year
        month =  self.calendar.get_date().month + 1
        day = self.calendar.get_date().day
        hour = self.hour_spinbox.get_value_as_int()
        minute = self.minute_spinbox.get_value_as_int()

        if self.calendar.get_date().day:
            return datetime(year, month, day, hour, minute)

    def set_datetime(self, datetime_object):
        if datetime_object:
            self.calendar.select_month(datetime_object.month - 1, datetime_object.year)
            self.calendar.select_day(datetime_object.day)
            self.hour_spinbox.set_value(datetime_object.hour if hasattr(datetime_object, 'hour') else 0)
            self.minute_spinbox.set_value(round(datetime_object.minute / 5) * 5 if hasattr(datetime_object, 'minute') else 0)
            self._on_calendar_day_selected()
            self._on_time_spinboxes_changed()
        else:
            self._on_clear_date_button_clicked()
            self._on_clear_time_button_clicked()
        self._on_popover_closed()
