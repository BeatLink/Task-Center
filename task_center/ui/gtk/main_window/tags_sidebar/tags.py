import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject


from task_center.src.gui.main_window.tasks.tags import TagPaneManager


class GtkTagManager:
    def __init__(self, gtk_builder):
        self._builder = gtk_builder
        self.tag_pane_manager = TagPaneManager(self._builder)

class TagPaneManager:
    """
    Handles the visibility and positioning of the tag pane and its related widgets
    """

    def __init__(self, builder):
        self.pane = builder.get_object('pane')
        self.headerbar_pane = builder.get_object('headerbar_pane')
        self.tag_box = builder.get_object('tag_box')
        self.tag_headerbar = builder.get_object('tag_headerbar')
        self._show_tags_togglebutton = builder.get_object('show_tags_togglebutton')

        # link the tag headerbar pane visibility with the show tag togglebutton
        GObject.Binding.bind_property(
            self._show_tags_togglebutton, 'active', self.tag_box, 'visible',
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE
        )

        # link the visibilities of the tag box and the tag headerbar
        GObject.Binding.bind_property(
            self.tag_box, 'visible', self.tag_headerbar, 'visible',
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE
        )

        # link the tag pane and tag headerbar pane positions
        GObject.Binding.bind_property(
            self.pane, 'position', self.headerbar_pane, 'position',
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE
        )

    # Properties -------------------------------------------------------------------------------------------------------
    @property
    def tag_pane_visibility(self):
        return self._show_tags_togglebutton.get_active()

    @tag_pane_visibility.setter
    def tag_pane_visibility(self, visibility):
        self._show_tags_togglebutton.set_active(visibility)
