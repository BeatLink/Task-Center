#!/usr/bin/env python3
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from task_center.core.models.recurrence import Recurrence
from task_center.ui.gtk.main_window.taskview.datetime_button import DateTimeButton

class RecurrenceButton:
    """
    This class handles the logic for the recurrence editor popover
    """
    def __init__(self):
        # gui builder preparation
        glade_file_path = str((pathlib.Path(__file__).parent / "recurrence_popover.glade").resolve())
        builder = Gtk.Builder()
        builder.add_from_file(glade_file_path)
        builder.connect_signals(self)
        # widget fetching
        self.popover = builder.get_object('popover')
        self.enabled_toggle = builder.get_object('enabled_toggle')
        self.increment_spinbutton = builder.get_object('increment_spinbutton')
        self.interval_menu = builder.get_object('interval_menu')
        self.weekdays_label = builder.get_object('weekdays_label')
        self.weekdays_box = builder.get_object('weekdays_box')
        self.weekday_sunday_toggle = builder.get_object('sunday_togglebutton')
        self.weekday_monday_toggle = builder.get_object('monday_togglebutton')
        self.weekday_tuesday_toggle = builder.get_object('tuesday_togglebutton')
        self.weekday_wednesday_toggle = builder.get_object('wednesday_togglebutton')
        self.weekday_thursday_toggle = builder.get_object('thursday_togglebutton')
        self.weekday_friday_toggle = builder.get_object('friday_togglebutton')
        self.weekday_saturday_toggle = builder.get_object('saturday_togglebutton')
        self.day_of_month_label = builder.get_object('day_of_month_label')
        self.day_of_month_box = builder.get_object('day_of_month_box')
        self.day_of_month_inner_box = builder.get_object('day_of_month_inner_box')
        self.day_of_month_set_button = builder.get_object('day_of_month_set_button')
        self.day_of_month_position_menu = builder.get_object('day_of_month_position_menu')
        self.day_of_month_menu = builder.get_object('day_of_month_menu')
        self.day_of_month_clear_button = builder.get_object('day_of_month_clear_button')
        self.stop_type_box = builder.get_object('stop_type_box')
        self.stop_type_menu = builder.get_object('stop_type_menu')
        self.stop_number_spinbox = builder.get_object('stop_number_spinbox')
        self.button = builder.get_object('button')
        self.stop_date_picker = DateTimeButton()
        self.stop_date_picker.button.set_visible(False)
        self.stop_type_box.pack_start(self.stop_date_picker.button, True, True, 0)

    # element updaters -------------------------------------------------------------------------------------------------
    def _on_button_clicked(self, *_):
        self.popover.popover.show()

    def _on_popover_closed(self, *_):
        recurrence = self.get_data()
        self.button.set_label("Repeats " + recurrence.string if recurrence.enabled else "Does not Repeat")

    def _on_enabled_toggle_state_set(self, *_):
        enabled = self.enabled_toggle.get_active()
        for element in [
                self.increment_spinbutton,
                self.interval_menu,
                self.weekdays_box,
                self.day_of_month_box,
                self.stop_type_box]:
            element.set_sensitive(enabled)

    def _on_increment_spinbutton_value_changed(self, *_):
        active_value = self.interval_menu.get_active_id()
        self.interval_menu.remove_all()
        for interval in ['Minute', 'Hour', 'Day', 'Week', 'Month', 'Year']:
            interval_string = f'{interval}s' if self.increment_spinbutton.get_value_as_int() > 1 else interval
            self.interval_menu.append(interval.lower(), interval_string)
        self.interval_menu.set_active_id(active_value)

    def _on_interval_menu_changed(self, *_):
        for weekday_widget in [self.weekdays_box, self.weekdays_label]:
            weekday_widget.set_visible(True if self.interval_menu.get_active_id() == 'week' else False)
        for day_of_month_widget in [self.day_of_month_label, self.day_of_month_box]:
            day_of_month_widget.set_visible(True if self.interval_menu.get_active_id() == 'month' else False)

    def _on_day_of_month_set_button_clicked(self, *_):
        self.day_of_month_inner_box.set_visible(True)
        self.day_of_month_set_button.set_visible(False)

    def _on_day_of_month_clear_button_clicked(self, *_):
        self.day_of_month_inner_box.set_visible(False)
        self.day_of_month_set_button.set_visible(True)

    def _on_stop_type_menu_changed(self, *_):
        self.stop_number_spinbox.set_visible(True if self.stop_type_menu.get_active_id() == 'number' else False)
        self.stop_date_picker.button.set_visible(True if self.stop_type_menu.get_active_id() == 'date' else False)

    # Recurrence Saving Methods ----------------------------------------------------------------------------------------
    def get_data(self):
        recurrence = Recurrence()
        recurrence.enabled = self.enabled_toggle.get_active()
        recurrence.interval = self.interval_menu.get_active_id()
        recurrence.increment = self.increment_spinbutton.get_value_as_int()
        recurrence.weekdays.sunday = self.weekday_sunday_toggle.get_active()
        recurrence.weekdays.monday = self.weekday_monday_toggle.get_active()
        recurrence.weekdays.tuesday = self.weekday_tuesday_toggle.get_active()
        recurrence.weekdays.wednesday = self.weekday_wednesday_toggle.get_active()
        recurrence.weekdays.thursday = self.weekday_thursday_toggle.get_active()
        recurrence.weekdays.friday = self.weekday_friday_toggle.get_active()
        recurrence.weekdays.saturday = self.weekday_saturday_toggle.get_active()
        if self.day_of_month_inner_box.get_visible():
            recurrence.weekday_of_month.ordinal = self.day_of_month_position_menu.get_active_id()
            recurrence.weekday_of_month.weekday = self.day_of_month_menu.get_active_id()
        else:
            recurrence.weekday_of_month.ordinal = None
            recurrence.weekday_of_month.weekday = None

        recurrence.stop_info.type = self.stop_type_menu.get_active_id()
        recurrence.stop_info.number = self.stop_number_spinbox.get_value_as_int()
        recurrence.stop_info.date = self.stop_date_picker.get_datetime()
        return recurrence

    def set_data(self, recurrence: Recurrence):
        self.enabled_toggle.set_active(recurrence.enabled)
        self.increment_spinbutton.set_value(recurrence.increment)
        self.interval_menu.set_active_id(recurrence.interval)
        self.weekday_sunday_toggle.set_active(recurrence.weekdays.sunday)
        self.weekday_monday_toggle.set_active(recurrence.weekdays.monday)
        self.weekday_tuesday_toggle.set_active(recurrence.weekdays.tuesday)
        self.weekday_wednesday_toggle.set_active(recurrence.weekdays.wednesday)
        self.weekday_thursday_toggle.set_active(recurrence.weekdays.thursday)
        self.weekday_friday_toggle.set_active(recurrence.weekdays.friday)
        self.weekday_saturday_toggle.set_active(recurrence.weekdays.saturday)
        self.day_of_month_position_menu.set_active_id(recurrence.weekday_of_month.ordinal)
        self.day_of_month_menu.set_active_id(recurrence.weekday_of_month.weekday)
        self.stop_type_menu.set_active_id(recurrence.stop_info.type)
        self.stop_number_spinbox.set_value(recurrence.stop_info.number)
        self.stop_date_picker.set_datetime(recurrence.stop_info.date)
        self._on_enabled_toggle_state_set()
        self._on_increment_spinbutton_value_changed()
        self._on_interval_menu_changed()
        if recurrence.weekday_of_month.weekday and recurrence.weekday_of_month.ordinal:
            self._on_day_of_month_set_button_clicked()
        else:
            self._on_day_of_month_clear_button_clicked()
        self._on_day_of_month_set_button_clicked()
        self._on_stop_type_menu_changed()


