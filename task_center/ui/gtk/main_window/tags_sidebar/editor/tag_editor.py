
import gi
import pathlib
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class TagEditor:
    """
    This class handles the logic for the tag_editor_dialog
    """
    # Todo add further documentation here
    def __init__(self, set_relative_to=None, connect_signals=None):
        # gui builder preparation
        glade_file_path = str((pathlib.Path(__file__).parent / "tag_editor.glade").resolve())
        builder = Gtk.Builder()
        builder.add_from_file(glade_file_path)
        builder.connect_signals(self)

        builder.get_object('criteria_builder_window').show()
        self.task_attributes_menu = builder.get_object('task_attributes_menu')
        self.task_attributes_menu.connect('changed', self.on_task_attributes_menu_changed)

        self.string_criteria_box = builder.get_object('string_criteria_box')
        self.recurrence_attributes_menu = builder.get_object('recurrence_attributes_menu')
        self.recurrence_attributes_menu.connect('changed', self.on_reccurrence_attribute_menu_changed)
        self.date_criteria_box = builder.get_object('date_criteria_box')
        self.number_criteria_box = builder.get_object('number_criteria_box')
        self.recurrence_interval_menu = builder.get_object('recurrence_interval_menu')

        self.on_task_attributes_menu_changed(self.task_attributes_menu)

    def on_task_attributes_menu_changed(self, menu: Gtk.ComboBoxText):
        if menu.get_active_id() == 'title' or menu.get_active_id() == 'description':
            self.recurrence_attributes_menu.set_visible(False)
            self.date_criteria_box.set_visible(False)
            self.number_criteria_box.set_visible(False)
            self.string_criteria_box.set_visible(True)
            self.recurrence_interval_menu.set_visible(False)

        elif menu.get_active_id() == 'start_date' or menu.get_active_id() == 'due_date' or menu.get_active_id() == 'done_date':
            self.recurrence_attributes_menu.set_visible(False)
            self.date_criteria_box.set_visible(True)
            self.number_criteria_box.set_visible(False)
            self.string_criteria_box.set_visible(False)

        elif menu.get_active_id() == 'recurrence':
            self.recurrence_attributes_menu.show()
            self.date_criteria_box.hide()
            self.number_criteria_box.set_visible(False)
            self.string_criteria_box.set_visible(False)

    def on_reccurrence_attribute_menu_changed(self, menu: Gtk.ComboBoxText):
        if menu.get_active_id() == 'interval':
            pass



if __name__ == '__main__':
    editor = TagEditor()
    Gtk.main()