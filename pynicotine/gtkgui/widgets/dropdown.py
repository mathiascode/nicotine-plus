# COPYRIGHT (C) 2023 Nicotine+ Contributors
#
# GNU GENERAL PUBLIC LICENSE
#    Version 3, 29 June 2007
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk
from gi.repository import Pango

from pynicotine.gtkgui.application import GTK_API_VERSION
from pynicotine.gtkgui.widgets.textentry import CompletionEntry
from pynicotine.gtkgui.widgets.theme import add_css_class


class DropDown:

    def __init__(self, container, has_entry=False, has_entry_completion=False, entry=None, label=None, visible=True,
                 selected_callback=None, items=None):

        self.selected_callback = selected_callback
        self.ids = {}
        self.positions = {}

        self.inner_container = None
        self.entry = entry
        self.entry_completion = None

        if GTK_API_VERSION >= 4:
            self.model = Gtk.StringList()
            self.widget = self.inner_container = Gtk.DropDown(
                factory=self._create_factory(visible=not has_entry),
                list_factory=self._create_factory(ellipsize=False),
                model=self.model, show_arrow=not has_entry, valign=Gtk.Align.CENTER, visible=True
            )
            self.widget.connect("notify::selected", self._on_item_selected)

            if has_entry:
                self.entry = Gtk.Entry(hexpand=True, visible=True) if entry is None else entry
                self.inner_container = Gtk.Box(visible=True)

                self.inner_container.append(self.entry)
                self.inner_container.append(self.widget)
                add_css_class(self.inner_container, "linked")

                popover = self.widget.get_last_child()
                popover.connect("notify::visible", self._on_dropdown_visible)

            container.append(self.inner_container)
        else:
            self.widget = self.inner_container = Gtk.ComboBoxText(
                has_entry=has_entry, valign=Gtk.Align.CENTER, visible=True
            )
            self.model = self.widget.get_model()

            if has_entry:
                if self.entry is None:
                    self.entry = self.widget.get_child()
                else:
                    self.entry = entry
                    #self.widget.get_child().unparent()
                    self.widget.set_property("child", entry)

                self.widget.connect("notify::popup-shown", self._on_dropdown_visible)
            else:
                for cell in self.widget.get_cells():
                    cell.set_property("ellipsize", Pango.EllipsizeMode.END)

            container.add(self.widget)

            if selected_callback:
                self.widget.connect("changed", self._on_item_selected)

        if has_entry:
            self.entry.set_width_chars(10)

            if has_entry_completion:
                self.entry_completion = CompletionEntry(self.entry)

        if label:
            label.set_mnemonic_widget(self.widget)

        if items:
            self.add_items(items)

        self.set_visible(visible)

    def _create_factory(self, ellipsize=True, visible=True):

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self._on_factory_setup, ellipsize, visible)

        if visible:
            factory.connect("bind", self._on_factory_bind)

        return factory

    def add_items(self, items):
        for item, item_id in items:
            self.append(item, item_id)

    def append(self, item, item_id=None):

        if item_id is None:
            item_id = item

        if GTK_API_VERSION >= 4:
            position = self.model.get_n_items()
            self.model.append(item)
        else:
            position = self.model.iter_n_children()
            self.widget.append_text(item)

        if self.entry_completion:
            self.entry_completion.add_completion(item)

        self.ids[position] = item_id
        self.positions[item_id] = position

    def get_selected_pos(self):

        if GTK_API_VERSION >= 4:
            return self.widget.get_selected()

        return self.widget.get_active()

    def get_selected_id(self):
        return self.ids[self.get_selected_pos()]

    def get_text(self):
        return self.entry.get_text()

    def set_selected_pos(self, position):

        if GTK_API_VERSION >= 4:
            self.widget.set_selected(position)
        else:
            self.widget.set_active(position)

    def set_selected_id(self, item_id):

        position = self.positions.get(item_id)

        if position is None:
            position = 0

        self.set_selected_pos(position)

    def set_text(self, text):
        self.entry.set_text(text)

    def remove_pos(self, position):

        if GTK_API_VERSION >= 4:
            self.model.remove(position)
        else:
            self.widget.remove(position)

        if self.entry_completion:
            self.entry_completion.remove_completion(self.ids[position])

    def remove_id(self, item_id):
        position = self.positions[item_id]
        self.remove_pos(position)

    def clear(self):

        self.ids.clear()
        self.positions.clear()

        if GTK_API_VERSION >= 4:
            self.model.splice(0, self.model.get_n_items())
            return

        self.widget.remove_all()

        if self.entry_completion:
            self.entry_completion.clear()

    def set_visible(self, visible):
        self.inner_container.set_visible(visible)

    def _on_factory_setup(self, factory, list_item, ellipsize, visible):

        label = Gtk.Label(xalign=0)

        if ellipsize:
            label.set_ellipsize(Pango.EllipsizeMode.END)

        if visible:
            list_item.set_child(label)
            return

        icon = Gtk.Image(icon_name="pan-down-symbolic")
        list_item.set_child(icon)

    def _on_factory_bind(self, factory, list_item):

        label = list_item.get_child()
        string_obj = list_item.get_item()

        label.set_text(string_obj.get_string())

    def _on_dropdown_visible(self, popover, param):

        visible = popover.get_property(param.name)

        if not visible:
            self.entry.grab_focus_without_selecting()
            self.entry.set_position(-1)
            return

        if GTK_API_VERSION == 3:
            return

        parent = self.entry.get_parent()
        popover = self.widget.get_last_child()
        scrolled_window = popover.get_child()

        popover.set_offset(-parent.get_width() + self.widget.get_width(), 0)
        scrolled_window.set_size_request(parent.get_width(), -1)

    def _on_item_selected(self, *_args):

        if self.selected_callback:
            self.selected_callback(self)

        if GTK_API_VERSION == 3 or self.entry is None:
            return

        item = self.widget.get_selected_item()

        if item is not None:
            self.set_text(item.get_string())
