"""
Important: Custom format serialization cannot be implemented as yet due to a bug in the gui _textbuffer.
See https://gitlab.gnome.org/GNOME/gtk/issues/992 for more information
"""

import pathlib
import rfc3987
import typing
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib


# Search Functionality #################################################################################################
class _Search:
    """
    Implements search functionality by adding the given search_highlight_tag to text in the given textbuffer
    that matches the contents of the given search_entry
    """
    def __init__(self, textbuffer: Gtk.TextBuffer, search_entry: Gtk.SearchEntry, search_highlight_tag: Gtk.TextTag):
        self._textbuffer = textbuffer
        self._search_entry = search_entry
        self._search_entry.connect('search-changed', self._on_search_entry_search_changed)
        self._search_highlight_tag = search_highlight_tag

    # Signal Handlers --------------------------------------------------------------------------------------------------
    def _on_search_entry_search_changed(self, _search_entry: Gtk.SearchEntry):
        self._highlight_search_results()

    # Inner methods ----------------------------------------------------------------------------------------------------
    def _highlight_search_results(self):
        """Adds a highlight tag to words that match a search pattern"""
        start_iter = self._textbuffer.get_start_iter()
        end_iter = self._textbuffer.get_end_iter()
        search_text = self._search_entry.get_text()

        # Resets the search tag
        self._textbuffer.remove_tag(self._search_highlight_tag, start_iter, end_iter)
        if search_text:
            # If search entry populated, search for the text starting from the start iter
            match = start_iter.forward_search(search_text, 0, end_iter)
            while match is not None:
                # If match is found, apply the tag and continue the search from the match end iter
                match_start, match_end = match
                self._textbuffer.apply_tag(self._search_highlight_tag, match_start, match_end)
                match = match_end.forward_search(search_text, 0, end_iter)


# Infobar Functionality ################################################################################################
class _InfoBar:
    """Convenience class for setting up the given infobar and child infobar label"""
    def __init__(self, infobar, infobar_label):
        self._infobar = infobar
        self._infobar.connect('response', self._on_infobar_response)
        self._infobar_label = infobar_label

    # Signal Handlers --------------------------------------------------------------------------------------------------
    def _on_infobar_response(self, _infobar, response_id):
        self._process_infobar_response(response_id)

    # Inner methods ----------------------------------------------------------------------------------------------------
    def _process_infobar_response(self, response_id):
        if response_id == Gtk.ResponseType.CLOSE:
            self._infobar.set_revealed(False)
            self._infobar.set_message_type(Gtk.MessageType.INFO)
            self._infobar_label.set_text("")

    # Interface Methods ------------------------------------------------------------------------------------------------
    def display_infobar_message(self, message_type: Gtk.MessageType, message: str):
        self._infobar.set_revealed(True)
        self._infobar.set_message_type(message_type)
        self._infobar_label.set_text(message)


# Link Formatting and Opening Functionality ############################################################################
class _Links:
    def __init__(self, textbuffer: Gtk.TextBuffer, link_tag: Gtk.TextTag,
                 open_link_error_callback: typing.Callable[[GLib.Error], None]):
        self._textbuffer = textbuffer
        self._textbuffer.connect('changed', self._on_textbuffer_changed)
        self._link_tag = link_tag
        self._link_tag.connect('event', self._on_link_tag_event)
        self._open_link_error_callback = open_link_error_callback

    # Signal Handlers --------------------------------------------------------------------------------------------------
    def _on_textbuffer_changed(self, _buffer):
        self._update_links()

    def _on_link_tag_event(self, _texttag, _textview, event: Gdk.Event, textiter: Gtk.TextIter):
        self._open_url_if_left_click(event, textiter)

    # Inner Methods ----------------------------------------------------------------------------------------------------
    def _update_links(self):
        # Get the iter for the entire textbuffer
        start_iter = self._textbuffer.get_start_iter()
        end_iter = self._textbuffer.get_end_iter()

        # Purges any old link tags
        self._textbuffer.remove_tag(self._link_tag, start_iter, end_iter)

        # Gets all text in the textbuffer and saves any valid urls to found_urls
        found_urls = []
        text = self._textbuffer.get_text(start_iter, end_iter, True)
        for word in text.split():
            if rfc3987.match(word, rule='absolute_URI'):
                url_parts = rfc3987.parse(word, rule='absolute_URI')
                if url_parts['scheme'] and (url_parts['authority'] or url_parts['path']):
                    found_urls.append(word)

        # Searches for found urls in the text buffer and applies the the link tag to them
        for url in found_urls:
            match = start_iter.forward_search(url, 0, end_iter)
            while match is not None:
                match_start, match_end = match
                self._textbuffer.remove_all_tags(match_start, match_end)
                self._textbuffer.apply_tag(self._link_tag, match_start, match_end)
                match = match_end.forward_search(url, 0, end_iter)

    def _open_url_if_left_click(self, event: Gdk.Event, textiter: Gtk.TextIter):
        """If the button event received was a left mouse click, find the url and open it"""
        if event.get_event_type() == Gdk.EventType.BUTTON_PRESS and event.button._button == 1:
            start, end = self._get_tag_bounds(textiter, self._link_tag)
            url = self._textbuffer.get_text(start, end, True)
            self._open_link(url)

    @staticmethod
    def _get_tag_bounds(textiter: Gtk.TextIter, tag: Gtk.TextTag):
        """
        Gets the tag range for the given tag if the tag is under Gtk.TextIter. It's copied from zim wiki.
        See https://github.com/zim-desktop-wiki/zim-desktop-wiki/blob/master/zim/gui/pageview.py#L1013
        """
        start = textiter.copy()
        if not start.starts_tag(tag):
            start.backward_to_tag_toggle(tag)
        end = textiter.copy()
        if not end.ends_tag(tag):
            end.forward_to_tag_toggle(tag)
        return start, end

    def _open_link(self, url: str):
        """Opens the given url string with the user's default application, via GTK. URL must be valid with a scheme"""
        try:
            Gtk.show_uri(None, url, Gdk.CURRENT_TIME)
        except GLib.Error as error:
            self._open_link_error_callback(error)


# Main Class ###########################################################################################################
class FormatTextView:
    def __init__(self):
        # Valid tags
        self._tags_list = ('bold', 'italics', 'underline', 'strikethrough')

        # Gtk Builder Setup
        self._builder = Gtk.Builder()
        self._builder.add_from_file(str(pathlib.Path(__file__).resolve().parent / 'format_textview.glade'))
        self._builder.connect_signals(self)

        # Get Widgets
        self._box = self._builder.get_object('box')
        self._textview = self._builder.get_object('textview')
        self._textbuffer = self._builder.get_object('textbuffer')
        self._text_tags_dict = {tag: self._builder.get_object(f'texttag_{tag}') for tag in self._tags_list}
        self._togglebutton_dict = {tag: self._builder.get_object(f'{tag}_togglebutton') for tag in self._tags_list}

        # Connect format button to handlers
        for tag in self._tags_list:
            self._togglebutton_dict[tag].connect('toggled', self._on_format_togglebutton_toggled)

        # Set Default IO Format
        self._default_format = self._textbuffer.register_serialize_tagset()
        self._default_format = self._textbuffer.register_deserialize_tagset()

        # Setup search functionality
        search_entry = self._builder.get_object('search_entry')
        search_highlight_tag = self._builder.get_object('texttag_search_highlight')
        self._search_handler = _Search(self._textbuffer, search_entry, search_highlight_tag)

        # Setup Infobar notification functionality
        infobar = self._builder.get_object('infobar')
        infobar_label = self._builder.get_object('infobar_label')
        self._infobar_manager = _InfoBar(infobar, infobar_label)

        link_tag = self._builder.get_object('texttag_link')
        self._link_manager = _Links(self._textbuffer, link_tag, self._display_open_link_error_message)

    # Signal Handlers --------------------------------------------------------------------------------------------------
    def _on_format_togglebutton_toggled(self, togglebutton: Gtk.ToggleButton):
        self._force_mutual_exclusive_togglebuttons(togglebutton)
        self._format_selected_text()

    def on_textbuffer_insert_text(self, _text_buffer, location, text, _length):
        self._format_new_text(location, text)

    def _on_textbuffer_mark_set(self, _textbuffer, textiter, textmark):
        self._update_togglebuttons(textiter, textmark)

    # Inner Methods ----------------------------------------------------------------------------------------------------
    def _force_mutual_exclusive_togglebuttons(self, toggled_button):
        """Ensures that only one togglebutton can be toggled at a time by deselecting all others when one is toggled"""
        for togglebutton in self._togglebutton_dict.values():
            if togglebutton.get_active() and togglebutton != toggled_button:
                togglebutton.handler_block_by_func(self._on_format_togglebutton_toggled)
                togglebutton.set_active(False)
                togglebutton.handler_unblock_by_func(self._on_format_togglebutton_toggled)

    def _format_selected_text(self):
        """Updates formatting of selected text, depending on which tags are toggled"""
        tag_enabled_dict = {
            texttag: self._togglebutton_dict[tag].get_active() for tag, texttag in self._text_tags_dict.items()}
        if self._textbuffer.get_selection_bounds():
            start, end = self._textbuffer.get_selection_bounds()
            for tag, enabled in tag_enabled_dict.items():
                if enabled:
                    self._textbuffer.apply_tag(tag, start, end)
                else:
                    self._textbuffer.remove_tag(tag, start, end)

    def _format_new_text(self, location, text):
        """Adds formatting to newly typed text, depending on which tags are toggled"""
        enabled_tags = [
            self._text_tags_dict[tag]
            for tag, togglebutton in self._togglebutton_dict.items()
            if togglebutton.get_active()]
        self._textbuffer.handler_block_by_func(self.on_textbuffer_insert_text)
        self._textbuffer.insert_with_tags(location, text, *enabled_tags)
        self._textbuffer.handler_unblock_by_func(self.on_textbuffer_insert_text)
        self._textbuffer.stop_emission_by_name('insert-text')

    def _update_togglebuttons(self, textiter, textmark):
        """Updates the tag togglebuttons depending on tags in selection or at cursor"""

        if self._textbuffer.get_selection_bounds():
            # enable togglebutton only if tag applies to every character in selection
            def has_tag(offset, tag_param):
                # Returns true if iter at offset has a tag
                return self._textbuffer.get_iter_at_offset(offset).has_tag(tag_param)

            def range_has_tag(tag_param):
                # Returns true if all characters in selected text has tag
                start, end = self._textbuffer.get_selection_bounds()
                return all([has_tag(offset, tag_param) for offset in range(start.get_offset(), end.get_offset())])

            # Generates dict of all tags and whether all chars in the range has each tag
            tags_enabled_dict = {tag: range_has_tag(gtk_tag) for tag, gtk_tag in self._text_tags_dict.items()}

            # enables the togglebutton if all chars in range has the tag
            for tag, togglebutton in self._togglebutton_dict.items():
                togglebutton.handler_block_by_func(self._on_format_togglebutton_toggled)
                togglebutton.set_active(True if tags_enabled_dict[tag] else False)
                togglebutton.handler_unblock_by_func(self._on_format_togglebutton_toggled)
        elif textmark.get_name() == 'insert':
            enabled_tags = textiter.get_tags()
            for tag, togglebutton in self._togglebutton_dict.items():
                togglebutton.set_active(True if self._text_tags_dict[tag] in enabled_tags else False)

    def _display_open_link_error_message(self, error):
        self._infobar_manager.display_infobar_message(Gtk.MessageType.WARNING, error.message)

    # Interface Methods ------------------------------------------------------------------------------------------------
    @property
    def box_widget(self):
        return self._box

    def get_text(self, text_format=None):
        text_format = text_format if text_format else self._default_format
        start_iter = self._textbuffer.get_start_iter()
        end_iter = self._textbuffer.get_end_iter()
        return self._textbuffer.serialize(self._textbuffer, text_format, start_iter, end_iter)

    def load_text(self, text, text_format=None):
        text_format = text_format if text_format else self._default_format
        start_iter = self._textbuffer.get_start_iter()
        self._textbuffer.deserialize(self._textbuffer, text_format, start_iter, text)
