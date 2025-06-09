# COPYRIGHT (C) 2020-2025 Nicotine+ Contributors
# COPYRIGHT (C) 2016-2017 Michael Labouebe <gfarmerfr@free.fr>
# COPYRIGHT (C) 2008-2009 quinox <quinox@users.sf.net>
# COPYRIGHT (C) 2006-2009 daelstorm <daelstorm@gmail.com>
# COPYRIGHT (C) 2003-2004 Hyriand <hyriand@thegraveyard.org>
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

import time

import gi.module

from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Pango

from pynicotine.config import config
from pynicotine.core import core
from pynicotine.gtkgui.application import GTK_API_VERSION
from pynicotine.gtkgui.widgets import clipboard
from pynicotine.gtkgui.widgets.accelerator import Accelerator
from pynicotine.gtkgui.widgets.popupmenu import PopupMenu
from pynicotine.gtkgui.widgets.theme import FILE_TYPE_ICON_LABELS
from pynicotine.gtkgui.widgets.theme import PRIVATE_ICON_LABELS
from pynicotine.gtkgui.widgets.theme import USER_STATUS_ICON_LABELS
from pynicotine.gtkgui.widgets.theme import add_css_class


class Row(GObject.Object):

    def __init__(self, *args):
        super().__init__()
        self.values = [*args]
        self.widgets = [None] * len(self.values)

    def set_value(self, index, value):

        self.values[index] = value
        widget = self.widgets[index]

        if widget is None:
            return

        if isinstance(widget, Gtk.Inscription):
            widget.set_text(value)

        elif isinstance(widget, Gtk.Image):
            widget.set_from_icon_name(value)

        elif isinstance(widget, Gtk.ProgressBar):
            widget.set_fraction(value)

        elif isinstance(widget, Gtk.CheckButton):
            widget.blocked = True
            widget.set_active(value)
            widget.blocked = False

class TreeView:

    def __init__(self, window, parent, columns, has_tree=False, multi_select=False,
                 persistent_sort=False, name=None, secondary_name=None, activate_row_callback=None,
                 focus_in_callback=None, select_row_callback=None, delete_accelerator_callback=None,
                 search_entry=None):

        self.window = window
        self.widget = None
        self.model = None
        self.multi_select = multi_select
        self.iterators = {}
        self.has_tree = has_tree
        self._widget_name = name
        self._secondary_name = secondary_name
        self._columns = columns
        self._data_types = []
        self._iterator_keys = {}
        self._iterator_key_column = 0
        self._column_ids = {}
        self._column_offsets = {}
        self._column_gvalues = {}
        self._column_gesture_controllers = []
        self._column_numbers = None
        self._default_sort_column = None
        self._default_sort_column_widget = None
        self._default_sort_type = Gtk.SortType.ASCENDING
        self._sort_column = None
        self._sort_column_widget = None
        self._sort_type = None
        self._persistent_sort = persistent_sort
        self._last_redraw_time = 0
        self._selection = None
        self._h_adjustment = parent.get_hadjustment()
        self._v_adjustment = parent.get_vadjustment()
        self._v_adjustment_upper = 0
        self._v_adjustment_value = 0
        self._is_scrolling_to_row = False
        self.notify_value_handler = self._v_adjustment.connect("notify::value", self.on_v_adjustment_value)

        if GTK_API_VERSION >= 4:
            self.widget = Gtk.ColumnView(visible=True)
            parent.set_child(self.widget)  # pylint: disable=no-member
        else:
            self.widget = Gtk.TreeView(fixed_height_mode=True, has_tooltip=True, visible=True)
            self._selection = self.widget.get_selection()
            parent.add(self.widget)        # pylint: disable=no-member

        self._column_menu = self.widget.column_menu = PopupMenu(
            self.window.application, self.widget, callback=self.on_column_header_menu, connect_events=False)

        self._initialise_columns(columns)

        Accelerator("<Primary>c", self.widget, self.on_copy_cell_data_accelerator)
        Accelerator("<Primary>f", self.widget, self.on_start_search)

        Accelerator("Left", self.widget, self.on_collapse_row_accelerator)
        Accelerator("minus", self.widget, self.on_collapse_row_blocked_accelerator)
        Accelerator("Right", self.widget, self.on_expand_row_accelerator)
        Accelerator("plus", self.widget, self.on_expand_row_blocked_accelerator)
        Accelerator("equal", self.widget, self.on_expand_row_blocked_accelerator)
        Accelerator("backslash", self.widget, self.on_expand_row_level_accelerator)

        if multi_select:
            if GTK_API_VERSION >= 4:
                self.widget.set_enable_rubberband(True)
            else:
                self.widget.set_rubber_banding(True)
                self._selection.set_mode(Gtk.SelectionMode.MULTIPLE)

        if activate_row_callback:
            if GTK_API_VERSION >= 4:
                self.widget.connect("activate", self.on_activate_row_gtk4, activate_row_callback)
            else:
                self.widget.connect("row-activated", self.on_activate_row_gtk3, activate_row_callback)

        if focus_in_callback:
            if GTK_API_VERSION >= 4:
                focus_controller = Gtk.EventControllerFocus()
                focus_controller.connect("enter", self.on_focus_in, focus_in_callback)
                self.widget.add_controller(focus_controller)  # pylint: disable=no-member
            else:
                self.widget.connect("focus-in-event", self.on_focus_in, focus_in_callback)

        if select_row_callback:
            if GTK_API_VERSION >= 4:
                self._selection.connect("selection-changed", self.on_select_row_gtk4, select_row_callback)
            else:
                self._selection.connect("changed", self.on_select_row_gtk3, select_row_callback)

        if delete_accelerator_callback:
            Accelerator("Delete", self.widget, self.on_delete_accelerator, delete_accelerator_callback)

        if GTK_API_VERSION == 3:
            if search_entry:
                self.widget.set_search_entry(search_entry)

            self._query_tooltip_handler = self.widget.connect("query-tooltip", self.on_tooltip)
            self.widget.connect("move-cursor", self.on_key_move_cursor)
            self.widget.set_search_equal_func(self.on_search_match)

        add_css_class(self.widget, "data-table")
        add_css_class(self.widget, "treeview-spacing")

    def destroy(self):

        # Prevent updates while destroying widget
        if GTK_API_VERSION == 3:
            self.widget.disconnect(self._query_tooltip_handler)

        self._v_adjustment.disconnect(self.notify_value_handler)

        self._column_menu.destroy()
        self.__dict__.clear()

    def create_model(self):

        if GTK_API_VERSION >= 4:
            self.model = Gio.ListStore(item_type=Row)
            sort_model = Gtk.SortListModel(model=self.model, sorter=self.widget.get_sorter())
            self._selection = Gtk.MultiSelection(model=sort_model) if self.multi_select else Gtk.SingleSelection(model=sort_model)
            self.widget.set_model(self._selection)
            return self.model

        # Bypass Tree/ListStore overrides for improved performance in set_value()
        gtk_module = gi.module.get_introspection_module("Gtk")
        model_class = gtk_module.TreeStore if self.has_tree else gtk_module.ListStore

        if hasattr(gtk_module.ListStore, "insert_with_valuesv"):
            gtk_module.ListStore.insert_with_values = gtk_module.ListStore.insert_with_valuesv

        self.model = model_class()
        self.model.set_column_types(self._data_types)

        if self._sort_column is not None and self._sort_type is not None:
            self.model.set_sort_column_id(self._sort_column, self._sort_type)

        self.widget.set_model(self.model)
        return self.model

    def redraw(self):
        """Workaround for GTK 3 issue where GtkTreeView doesn't refresh changed
        values if horizontal scrolling is present while fixed-height mode is
        enabled."""

        if GTK_API_VERSION != 3 or self._h_adjustment.get_value() <= 0:
            return

        current_time = time.monotonic()

        if (current_time - self._last_redraw_time) < 1:
            return

        self._last_redraw_time = current_time
        self.widget.queue_draw()

    def _append_columns(self, cols, column_config):

        # Restore column order from config
        for column_id in column_config:
            column = cols.get(column_id)

            if column is not None:
                self.widget.append_column(column)

        added_columns = self.widget.get_columns()

        # If any columns were missing in the config, append them
        for index, column in enumerate(cols.values()):
            if column not in added_columns:
                if GTK_API_VERSION >= 4:
                    self.widget.insert_column(index, column)
                else:
                    self.widget.insert_column(column, index)

        column_header_row = None
        has_visible_column_header = False

        for index, column in enumerate(self.widget.get_columns()):
            if GTK_API_VERSION >= 4:
                column_header = None

                for widget in list(self.widget):
                    if widget.get_css_name() == "header":
                        column_header = list(widget)[index]

                column_header_row = column_header.get_parent()

                gesture_click = Gtk.GestureClick()
                column_header.add_controller(gesture_click)                  # pylint: disable=no-member

                if self._sort_column == column.sort_column_id:
                    self._sort_column_widget = column
                    self.widget.sort_by_column(column, self._sort_type)

                if self._default_sort_column == column.sort_column_id:
                    self._default_sort_column_widget = column

                column_header.connect("notify::css-classes", self.on_column_position_changed_header)
            else:
                column_header = column.get_button()
                gesture_click = Gtk.GestureMultiPress(widget=column_header)  # pylint: disable=c-extension-no-member

            gesture_click.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
            gesture_click.connect("pressed", self.on_column_header_pressed, column)
            self._column_gesture_controllers.append(gesture_click)

            title_container = next(iter(column_header))
            title_widget = next(iter(title_container)) if column.xalign < 1 else list(title_container)[-1]

            if not column.header_visible:
                title_widget.set_visible(False)
            else:
                has_visible_column_header = True

            if GTK_API_VERSION == 3:
                continue

            if column.xalign == 1:
                title_widget = next(iter(title_container))
                title_widget.set_halign(Gtk.Align.END)
                title_widget.set_hexpand(True)

                title_container.remove(title_widget)
                title_container.append(title_widget)

        # Read Show / Hide column settings from last session
        for column_id, column in cols.items():
            column.set_visible(bool(column_config.get(column_id, {}).get("visible", True)))

        if GTK_API_VERSION >= 4:
            column_header_row.set_visible(has_visible_column_header)

            def on_sorter_changed(*_args):
                if hasattr(self, "widget") and self.model.get_n_items() > 0:
                    self.widget.scroll_to(0, None, Gtk.ListScrollFlags.FOCUS)

            self.widget.get_sorter().connect("changed", on_sorter_changed)
        else:
            self.widget.set_headers_visible(has_visible_column_header)

            if self._sort_column is not None and self._sort_type is not None:
                self.model.set_sort_column_id(self._sort_column, self._sort_type)

    def _update_column_properties(self, *_args):

        columns = self.widget.get_columns()
        resizable_set = False

        for column in reversed(columns):
            if not column.get_visible():
                continue

            if not resizable_set:
                # Make sure the last visible column isn't resizable
                column.set_resizable(False)
                column.set_fixed_width(-1)

                resizable_set = True
                continue

            # Make the previously last column resizable again
            column.set_resizable(True)
            break

        # Set first non-icon column as the expander column
        for column in columns:
            if column.type != "icon" and column.get_visible():
                #self.widget.set_expander_column(column)
                break

    def _initialise_column_ids(self, columns):

        self._data_types = []
        int_types = {GObject.TYPE_UINT, GObject.TYPE_UINT64}

        for column_index, (column_id, column_data) in enumerate(columns.items()):
            data_type = column_data.get("data_type")

            if not data_type:
                column_type = column_data.get("column_type")

                if column_type == "progress":
                    data_type = GObject.TYPE_INT

                elif column_type == "toggle":
                    data_type = GObject.TYPE_BOOLEAN

                else:
                    data_type = GObject.TYPE_STRING

            self._column_ids[column_id] = column_index
            self._data_types.append(data_type)

            if data_type not in int_types:
                continue

            self._column_gvalues[column_index] = value = GObject.Value(data_type)

            # Optimization: bypass PyGObject's set_value override
            value.set_value = value.set_uint if data_type == GObject.TYPE_UINT else value.set_uint64

        self._column_numbers = list(self._column_ids.values())

    def _create_text_factory(self, column_index, nat_chars=0, text_underline_column=None, text_weight_column=None):

        def _on_factory_setup(factory, list_item):

            cell = Gtk.Inscription(
                focusable=True, margin_start=12, margin_end=12, margin_top=4, margin_bottom=4,
                nat_chars=nat_chars, wrap_mode=Pango.WrapMode.NONE, xalign=0.0
            )
            list_item.set_child(cell)

        def _on_factory_bind(factory, list_item, column_index, text_underline_column, text_weight_column):

            cell = list_item.get_child()
            row = list_item.get_item()
            row.widgets[column_index] = cell

            if text_underline_column is not None or text_weight_column is not None:
                has_text_underline = row.values[text_underline_column] if text_underline_column is not None else False
                has_text_weight = row.values[text_weight_column] if text_weight_column is not None else False

                attributes = cell.get_attributes()
                attributes.change(
                    Pango.attr_underline_new(
                        Pango.Underline.SINGLE if has_text_underline else Pango.Style.NORMAL
                    )
                )
                attributes.change(
                    Pango.attr_weight_new(
                        Pango.Weight.BOLD if has_text_weight else Pango.Weight.NORMAL
                    )
                )

            cell.set_text(row.values[column_index])

        def _on_factory_unbind(factory, list_item, column_index):
            row = list_item.get_item()
            row.widgets[column_index] = None

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", _on_factory_setup)
        factory.connect("bind", _on_factory_bind, column_index, text_underline_column, text_weight_column)
        factory.connect("unbind", _on_factory_unbind, column_index)

        return factory

    def _create_number_factory(self, column_index, nat_chars=None):

        def _on_factory_setup(factory, list_item):

            cell = Gtk.Inscription(
                focusable=True, margin_start=12, margin_end=12, margin_top=4, margin_bottom=4,
                nat_chars=nat_chars, wrap_mode=Pango.WrapMode.NONE, xalign=1.0
            )
            list_item.set_child(cell)

        def _on_factory_bind(factory, list_item, column_index):

            cell = list_item.get_child()
            row = list_item.get_item()
            row.widgets[column_index] = cell
            cell.set_text(row.values[column_index])

        def _on_factory_unbind(factory, list_item, column_index):
            row = list_item.get_item()
            row.widgets[column_index] = None

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", _on_factory_setup)
        factory.connect("bind", _on_factory_bind, column_index)
        factory.connect("unbind", _on_factory_unbind, column_index)

        return factory

    def _create_progress_factory(self, column_index):

        def _on_factory_setup(factory, list_item):
            progress_bar = Gtk.ProgressBar(focusable=True, show_text=True)
            list_item.set_child(progress_bar)

        def _on_factory_bind(factory, list_item, column_index):

            progress_bar = list_item.get_child()
            row = list_item.get_item()
            fraction = row.values[column_index]

            row.widgets[column_index] = progress_bar
            progress_bar.set_fraction(fraction)
            progress_bar.set_text(f"{fraction}%")

        def _on_factory_unbind(factory, list_item, column_index):
            row = list_item.get_item()
            row.widgets[column_index] = None

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", _on_factory_setup)
        factory.connect("bind", _on_factory_bind, column_index)
        factory.connect("unbind", _on_factory_unbind, column_index)

        return factory

    def _create_toggle_factory(self, column_index, toggled_callback):

        def _on_factory_setup(factory, list_item):
            toggle = Gtk.CheckButton(
                focusable=True, halign=Gtk.Align.CENTER, margin_start=13, margin_end=13
            )
            list_item.set_child(toggle)

        def _on_factory_bind(factory, list_item, column_index, toggled_callback):

            toggle = list_item.get_child()
            row = list_item.get_item()
            row.widgets[column_index] = toggle
            toggle.set_active(row.values[column_index])
            toggle.blocked = False
            toggle.position = list_item.get_position()
            toggle.signal_id = toggle.connect("toggled", self.on_toggle_gtk4, toggled_callback)

        def _on_factory_unbind(factory, list_item, column_index):

            toggle = list_item.get_child()
            row = list_item.get_item()

            toggle.disconnect(toggle.signal_id)
            toggle.blocked = False
            toggle.signal_id = None
            toggle.position = None
            row.widgets[column_index] = None

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", _on_factory_setup)
        factory.connect("bind", _on_factory_bind, column_index, toggled_callback)
        factory.connect("unbind", _on_factory_unbind, column_index)

        return factory

    def _create_icon_factory(self, column_index, is_country_flag=False):

        def _on_factory_setup(factory, list_item):
            icon = Gtk.Image(focusable=True, halign=Gtk.Align.END, pixel_size=21 if is_country_flag else -1)
            list_item.set_child(icon)

        def _on_factory_bind(factory, list_item, column_index):

            icon = list_item.get_child()
            row = list_item.get_item()
            row.widgets[column_index] = icon
            icon.set_from_icon_name(row.values[column_index])

        def _on_factory_unbind(factory, list_item, column_index):
            row = list_item.get_item()
            row.widgets[column_index] = None

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", _on_factory_setup)
        factory.connect("bind", _on_factory_bind, column_index)
        factory.connect("unbind", _on_factory_unbind, column_index)

        return factory

    def _initialise_columns(self, columns):

        def sort_strings(row_a, row_b, column_index):
            a = row_a.values[column_index].lower()
            b = row_b.values[column_index].lower()
            return (a > b) - (a < b)

        def sort_numbers(row_a, row_b, column_index):
            a = row_a.values[column_index]
            b = row_b.values[column_index]
            return (a > b) - (a < b)

        self._initialise_column_ids(columns)
        self.model = self.create_model()

        progress_padding = 1
        height_padding = 4
        width_padding = 10 if GTK_API_VERSION >= 4 else 12

        column_widgets = {}
        column_config = {}
        has_visible_column_header = False

        for column_index, (column_id, column_data) in enumerate(columns.items()):
            title = column_data.get("title")
            iterator_key = column_data.get("iterator_key")
            sort_data_column = column_data.get("sort_column", column_id)
            sort_column_id = self._column_ids[sort_data_column]
            default_sort_type = column_data.get("default_sort_type")

            if iterator_key:
                # Use values from this column as keys for iterator mapping
                self._iterator_key_column = column_index

            if default_sort_type:
                # Sort treeview by values in this column by default
                self._default_sort_column = sort_column_id
                self._default_sort_type = (Gtk.SortType.DESCENDING if default_sort_type == "descending"
                                           else Gtk.SortType.ASCENDING)

                if self._sort_column is None and self._sort_type is None:
                    self._sort_column = self._default_sort_column
                    self._sort_type = self._default_sort_type

            if title is None:
                # Hidden data column
                continue

            column_type = column_data["column_type"]
            width = column_data.get("width")
            should_expand_column = column_data.get("expand_column")
            sensitive_column = column_data.get("sensitive_column")

            if self._widget_name:
                try:
                    column_config = config.sections["columns"][self._widget_name][self._secondary_name]
                except KeyError:
                    column_config = config.sections["columns"][self._widget_name]

                column_properties = column_config.get(column_id, {})
                column_sort_type = column_properties.get("sort")

                # Restore saved column width
                if column_type != "icon":
                    width = column_properties.get("width", width)

                if column_sort_type and self._persistent_sort:
                    # Sort treeview by values in this column by default
                    self._sort_column = sort_column_id
                    self._sort_type = (Gtk.SortType.DESCENDING if column_sort_type == "descending"
                                       else Gtk.SortType.ASCENDING)

            # Allow individual cells to receive visual focus
            mode = Gtk.CellRendererMode.ACTIVATABLE if len(columns) > 1 else Gtk.CellRendererMode.INERT
            xalign = 0.0

            if GTK_API_VERSION >= 4:
                sorter = Gtk.CustomSorter()
                sort_func = sort_strings if self._data_types[sort_column_id] == GObject.TYPE_STRING else sort_numbers
                sorter.set_sort_func(sort_func, sort_column_id)

            if column_type == "text":
                text_underline_column = column_data.get("text_underline_column")
                text_weight_column = column_data.get("text_weight_column")
                text_underline_column_index = text_weight_column_index = None

                if text_underline_column is not None:
                    text_underline_column_index = self._column_ids[text_underline_column]

                if text_weight_column is not None:
                    text_weight_column_index = self._column_ids[text_weight_column]

                if GTK_API_VERSION >= 4:
                    nat_chars = width // 4 if width else 0
                    column = Gtk.ColumnViewColumn(
                        title=title, factory=self._create_text_factory(
                            column_index, nat_chars, text_underline_column_index, text_weight_column_index
                        ),
                        sorter=sorter
                    )
                else:
                    renderer = Gtk.CellRendererText(
                        mode=mode, single_paragraph_mode=True, xpad=width_padding, ypad=height_padding
                    )
                    column = Gtk.TreeViewColumn(title=title, cell_renderer=renderer, text=column_index)

                    if text_underline_column_index is not None:
                        column.add_attribute(renderer, "underline", text_underline_column_index)

                    if text_weight_column_index is not None:
                        column.add_attribute(renderer, "weight", text_weight_column_index)

            elif column_type == "number":
                xalign = 1

                if GTK_API_VERSION >= 4:
                    nat_chars = width // 4 if width else 0
                    column = Gtk.ColumnViewColumn(
                        title=title, factory=self._create_number_factory(column_index, nat_chars),
                        sorter=sorter
                    )
                else:
                    renderer = Gtk.CellRendererText(mode=mode, xalign=xalign, xpad=width_padding, ypad=height_padding)
                    column = Gtk.TreeViewColumn(title=title, cell_renderer=renderer, text=column_index)
                    column.set_alignment(xalign)

            elif column_type == "progress":
                xalign = 1

                if GTK_API_VERSION >= 4:
                    column = Gtk.ColumnViewColumn(
                        title=title, factory=self._create_progress_factory(column_index),
                        sorter=sorter
                    )
                else:
                    renderer = Gtk.CellRendererProgress(mode=mode, ypad=progress_padding)
                    column = Gtk.TreeViewColumn(title=title, cell_renderer=renderer, value=column_index)
                    column.set_alignment(xalign)

            elif column_type == "toggle":
                xalign = 0.5

                if GTK_API_VERSION >= 4:
                    column = Gtk.ColumnViewColumn(
                        title=title, factory=self._create_toggle_factory(column_index, column_data["toggle_callback"]),
                        sorter=sorter
                    )
                else:
                    renderer = Gtk.CellRendererToggle(mode=mode, xalign=xalign, xpad=13)
                    renderer.connect("toggled", self.on_toggle_gtk3, column_data["toggle_callback"])

                    column = Gtk.TreeViewColumn(title=title, cell_renderer=renderer, active=column_index)
                    inconsistent_column = column_data.get("inconsistent_column")

                    if inconsistent_column is not None:
                        column.add_attribute(renderer, "inconsistent", self._column_ids[inconsistent_column])

            elif column_type == "icon":
                if GTK_API_VERSION >= 4:
                    column = Gtk.ColumnViewColumn(
                        title=title, factory=self._create_icon_factory(column_index, column_id == "country"),
                        sorter=sorter
                    )
                else:
                    icon_args = {}

                    if column_id == "country":
                        if GTK_API_VERSION >= 4:
                            # Custom icon size defined in theme.py
                            icon_args["icon_size"] = Gtk.IconSize.NORMAL  # pylint: disable=no-member
                        else:
                            # Use the same size as the original icon
                            icon_args["stock_size"] = 0

                    renderer = Gtk.CellRendererPixbuf(mode=mode, xalign=1.0, **icon_args)
                    column = Gtk.TreeViewColumn(title=title, cell_renderer=renderer, icon_name=column_index)

            if GTK_API_VERSION == 3:
                # Required for fixed height mode
                column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
                column.set_reorderable(True)
                column.set_min_width(24)
                column.set_sort_column_id(sort_column_id)

                if sensitive_column:
                    column.add_attribute(renderer, "sensitive", self._column_ids[sensitive_column])

            if width is not None:
                column.set_resizable(column_type != "icon")

            if isinstance(width, int) and width > 0:
                column.set_fixed_width(width)

            if should_expand_column:
                column.set_expand(True)

            if GTK_API_VERSION >= 4:
                if self._widget_name:
                    column.connect("notify::fixed-width", self.on_column_position_changed)

                column.connect("notify::visible", self._update_column_properties)
            else:
                if self._widget_name:
                    column.connect("notify::x-offset", self.on_column_position_changed)

                column.connect("notify::visible", self._update_column_properties)

            column.id = column_id
            column.type = column_type
            column.sort_column_id = sort_column_id
            column.xalign = xalign
            column.header_visible = not column_data.get("hide_header", False)
            column.tooltip_callback = column_data.get("tooltip_callback")

            column_widgets[column_id] = column

        self._append_columns(column_widgets, column_config)
        self._update_column_properties()

    def save_columns(self):
        """Save a treeview's column widths and visibilities for the next
        session."""

        if not self._widget_name:
            return

        saved_columns = {}
        column_config = config.sections["columns"]

        for index, column in enumerate(self.widget.get_columns()):
            title = column.id
            visible = column.get_visible()
            sort_column_id = column.sort_column_id

            if GTK_API_VERSION >= 4:
                width = column.get_fixed_width()
            else:
                width = column.get_width()

            # A column width of zero should not be saved to the config.
            # When a column is hidden, the correct width will be remembered during the
            # run it was hidden. Subsequent runs will yield a zero width, so we
            # attempt to re-use a previously saved non-zero column width instead.
            try:
                if width <= 0:
                    if not visible:
                        saved_columns[title] = {
                            "visible": visible,
                            "width": column_config[self._widget_name][title]["width"]
                        }

                    continue

            except KeyError:
                # No previously saved width, going with zero
                pass

            saved_columns[title] = columns = {"visible": visible, "width": width}

            if not self._persistent_sort:
                continue

            if sort_column_id == self._sort_column and sort_column_id != self._default_sort_column:
                columns["sort"] = "descending" if self._sort_type == Gtk.SortType.DESCENDING else "ascending"

        if self._secondary_name is not None:
            if self._widget_name not in column_config:
                column_config[self._widget_name] = {}

            column_config[self._widget_name][self._secondary_name] = saved_columns
        else:
            column_config[self._widget_name] = saved_columns

    def freeze(self):

        if GTK_API_VERSION >= 4:
            self.widget.set_model(None)
            return

        self.model.set_sort_column_id(Gtk.TREE_SORTABLE_UNSORTED_SORT_COLUMN_ID, Gtk.SortType.ASCENDING)

    def unfreeze(self):

        if GTK_API_VERSION >= 4:
            self.widget.set_model(self._selection)
            return

        if self._sort_column is not None and self._sort_type is not None:
            self.model.set_sort_column_id(self._sort_column, self._sort_type)

    def set_show_expanders(self, show):
        if GTK_API_VERSION == 3:
            self.widget.set_show_expanders(show)

    def add_row(self, values, select_row=True, parent_iterator=None):

        key = values[self._iterator_key_column]

        if key in self.iterators:
            return None

        position = 0  # Insert at the beginning for large performance improvement
        value_columns = []
        included_values = []

        for index, value in enumerate(values):
            if not value and index is not self._sort_column:
                # Skip empty values if not active sort column to avoid unnecessary work
                continue

            if index in self._column_gvalues:
                # Need gvalue conversion for large integers
                gvalue = self._column_gvalues[index]
                gvalue.set_value(value or 0)
                value = gvalue

            value_columns.append(index)
            included_values.append(value)

        if GTK_API_VERSION >= 4:
            self.iterators[key] = iterator = self.model.get_n_items()
            row = Row(*values)
            self.model.append(row)

        elif self.has_tree:
            self.iterators[key] = iterator = self.model.insert_with_values(
                parent_iterator, position, value_columns, included_values
            )
        else:
            self.iterators[key] = iterator = self.model.insert_with_values(
                position, value_columns, included_values
            )

        self._iterator_keys[iterator] = key

        if select_row:
            self.select_row(iterator)

        return iterator

    def get_selected_rows(self):

        if GTK_API_VERSION >= 4:
            selected = self._selection.get_selection()

            for i in range(selected.get_size()):
                yield selected.get_nth(i)
            return

        _model, paths = self._selection.get_selected_rows()

        for path in paths:
            yield self.model.get_iter(path)

    def get_num_selected_rows(self):

        if GTK_API_VERSION >= 4:
            return self._selection.get_selection().get_size()

        return self._selection.count_selected_rows()

    def get_focused_row(self):

        if GTK_API_VERSION >= 4:
            return

        path, _column = self.widget.get_cursor()

        if path is None:
            return None

        return self.model.get_iter(path)

    def get_row_value(self, iterator, column_id):

        if GTK_API_VERSION >= 4:
            item = self.model.get_item(iterator)
            column_index = self._column_ids[column_id]
            return item.values[column_index]

        return self.model.get_value(iterator, self._column_ids[column_id])

    def set_row_value(self, iterator, column_id, value):

        if GTK_API_VERSION >= 4:
            item = self.model.get_item(iterator)
            column_index = self._column_ids[column_id]
            item.set_value(column_index, value)
            return

        column_index = self._column_ids[column_id]

        if column_index in self._column_gvalues:
            # Need gvalue conversion for large integers
            gvalue = self._column_gvalues[column_index]
            gvalue.set_value(value)
            value = gvalue

        return self.model.set_value(iterator, column_index, value)

    def set_row_values(self, iterator, column_ids, values):

        if GTK_API_VERSION >= 4:
            item = self.model.get_item(iterator)

            for index, column_id in enumerate(column_ids):
                column_index = self._column_ids[column_id]
                item.set_value(column_index, values[index])
            return

        value_columns = []

        for index, column_id in enumerate(column_ids):
            column_index = self._column_ids[column_id]

            if column_index in self._column_gvalues:
                # Need gvalue conversion for large integers
                gvalue = self._column_gvalues[column_index]
                gvalue.set_value(values[index])
                values[index] = gvalue

            value_columns.append(column_index)

        return self.model.set(iterator, value_columns, values)

    def remove_row(self, iterator):

        del self.iterators[self._iterator_keys[iterator]]
        self.model.remove(iterator)

        if GTK_API_VERSION >= 4:
            end_position = self.model.get_n_items()
            new_iterator_keys = {}

            for position in range(iterator, end_position):
                column_id = self._iterator_keys.pop(position + 1)
                new_iterator_keys[position] = column_id
                self.iterators[column_id] = position

            self._iterator_keys.update(new_iterator_keys)

    def select_row(self, iterator=None, expand_rows=True, should_scroll=True):

        if iterator is None:
            # Select first row if available
            if GTK_API_VERSION >= 4:
                if not self.model.get_n_items():
                    return

                iterator = 0
            else:
                iterator = self.model.get_iter_first()

                if iterator is None:
                    return

        if should_scroll:
            if GTK_API_VERSION >= 4:
                self.widget.scroll_to(
                    iterator, column=None, flags=Gtk.ListScrollFlags.FOCUS | Gtk.ListScrollFlags.SELECT)
            else:
                path = self.model.get_path(iterator)

                if expand_rows:
                    self.widget.expand_to_path(path)

                self._is_scrolling_to_row = True
                self.widget.set_cursor(path)
                self.widget.scroll_to_cell(path, column=None, use_align=True, row_align=0.5, col_align=0.5)
            return

        if GTK_API_VERSION >= 4:
            self._selection.select_item(iterator, True)
        else:
            self._selection.select_iter(iterator)

    def select_all_rows(self):
        self._selection.select_all()

    def unselect_all_rows(self):
        self._selection.unselect_all()

    def expand_row(self, iterator):

        if GTK_API_VERSION == 3:
            path = self.model.get_path(iterator)
            return self.widget.expand_row(path, open_all=False)

        return True

    def collapse_row(self, iterator):

        if GTK_API_VERSION == 3:
            path = self.model.get_path(iterator)
            return self.widget.collapse_row(path)

        return True

    def expand_all_rows(self):
        if GTK_API_VERSION == 3:
            self.widget.expand_all()

    def collapse_all_rows(self):
        if GTK_API_VERSION == 3:
            self.widget.collapse_all()

    def expand_root_rows(self):

        if GTK_API_VERSION >= 4:
            return

        model = self.model
        iterator = model.get_iter_first()

        while iterator:
            path = model.get_path(iterator)
            self.widget.expand_row(path, open_all=False)
            iterator = model.iter_next(iterator)

    def get_focused_column(self):
        _path, column = self.widget.get_cursor()
        return column.id

    def get_visible_columns(self):

        for column in self.widget.get_columns():
            if column.get_visible():
                yield column.id

    def is_empty(self):
        return not self.iterators

    def is_selection_empty(self):

        if GTK_API_VERSION >= 4:
            return self._selection.get_selection().get_size() <= 0

        return self._selection.count_selected_rows() <= 0

    def is_row_expanded(self, iterator):
        path = self.model.get_path(iterator)
        return self.widget.row_expanded(path)

    def is_row_selected(self, iterator):

        if GTK_API_VERSION >= 4:
            return self._selection.is_selected(iterator)

        return self._selection.iter_is_selected(iterator)

    def grab_focus(self):
        self.widget.grab_focus()

    def clear(self):

        self.widget.set_model(None)
        self.freeze()

        if GTK_API_VERSION >= 4:
            self.model.remove_all()
        else:
            self.model.clear()

        self.iterators.clear()
        self._iterator_keys.clear()

        self.unfreeze()

        if GTK_API_VERSION >= 4:
            self.widget.set_model(self._selection)
        else:
            self.widget.set_model(self.model)

    @staticmethod
    def get_icon_label(column, icon_name, is_short_country_label=False):

        if column.id == "country":
            country_code = icon_name[-2:].upper()

            if is_short_country_label:
                return country_code

            country_name = core.network_filter.COUNTRIES.get(country_code, _("Unknown"))
            return f"{country_name} ({country_code})"

        if column.id == "status":
            return USER_STATUS_ICON_LABELS[icon_name]

        if column.id == "private":
            return PRIVATE_ICON_LABELS.get(icon_name, "")

        if column.id == "file_type":
            return FILE_TYPE_ICON_LABELS[icon_name]

        return icon_name

    def on_toggle_gtk3(self, _widget, path, callback):
        callback(self, self.model.get_iter(path))

    def on_toggle_gtk4(self, widget, callback):

        if not widget.blocked:
            callback(self, widget.position)

    def on_activate_row_gtk3(self, _widget, path, column, callback):
        callback(self, self.model.get_iter(path), column.id)

    def on_activate_row_gtk4(self, _widget, iterator, callback):
        callback(self, iterator, None)

    def on_focus_in(self, *args):

        if GTK_API_VERSION >= 4:
            _widget, callback = args
        else:
            _widget, _controller, callback = args

        callback(self)

    def on_select_row_gtk3(self, selection, callback):

        iterator = None

        if self.multi_select:
            iterator = next(self.get_selected_rows(), None)
        else:
            _model, iterator = selection.get_selected()

        callback(self, iterator)

    def on_select_row_gtk4(self, selection, _position, _n_items, callback):
        iterator = selection.get_selection().get_nth(0)
        callback(self, iterator)

    def on_delete_accelerator(self, _treeview, _state, callback):
        callback(self)

    def on_column_header_pressed(self, controller, _num_p, _pos_x, _pos_y, column):
        """Reset sorting when column header has been pressed three times."""

        sort_column_id = column.sort_column_id

        if self._default_sort_column is None:
            # No default sort column for treeview, keep standard GTK behavior
            self.save_columns()
            return False

        if self._data_types[sort_column_id] == GObject.TYPE_STRING or column.id in {"in_queue", "queue_position"}:
            # String value (or queue position column): ascending sort by default
            first_sort_type = Gtk.SortType.ASCENDING
            second_sort_type = Gtk.SortType.DESCENDING
        else:
            # Numerical value: descending sort by default
            first_sort_type = Gtk.SortType.DESCENDING
            second_sort_type = Gtk.SortType.ASCENDING

        is_different_column = True

        if self._sort_column != sort_column_id:
            self._sort_column = sort_column_id
            self._sort_column_widget = column
            self._sort_type = first_sort_type

        elif self._sort_type == first_sort_type:
            self._sort_type = second_sort_type
            is_different_column = False

        elif self._sort_type == second_sort_type:
            # Reset treeview to default state
            self._sort_column = self._default_sort_column
            self._sort_column_widget = self._default_sort_column_widget
            self._sort_type = self._default_sort_type

        if GTK_API_VERSION >= 4:
            if is_different_column:
                self.widget.sort_by_column(None, self._sort_type)

            self.widget.sort_by_column(self._sort_column_widget, self._sort_type)
        else:
            self.model.set_sort_column_id(self._sort_column, self._sort_type)

        self.save_columns()

        controller.set_state(Gtk.EventSequenceState.CLAIMED)
        return True

    def on_column_header_toggled(self, _action, _state, column):
        column.set_visible(not column.get_visible())
        self._update_column_properties()

    def on_invert_sort_order(self, *_args):

        self._sort_type = (Gtk.SortType.DESCENDING if self._sort_type == Gtk.SortType.ASCENDING
                           else Gtk.SortType.ASCENDING)

        if GTK_API_VERSION >= 4:
            self.widget.sort_by_column(self._sort_column_widget, self._sort_type)
        else:
            self.model.set_sort_column_id(self._sort_column, self._sort_type)

        self.save_columns()

    def on_reset_sort_column(self, *_args):

        self._sort_column = self._default_sort_column
        self._sort_column_widget = self._default_sort_column_widget
        self._sort_type = self._default_sort_type

        if GTK_API_VERSION >= 4:
            self.widget.sort_by_column(None, self._sort_type)
            self.widget.sort_by_column(self._sort_column_widget, self._sort_type)
        else:
            self.model.set_sort_column_id(self._sort_column, self._sort_type)

        self.save_columns()

    def on_reset_columns(self, *_args):

        sorted_columns = sorted(
            self.widget.get_columns(),
            key=lambda column: list(self._columns.keys()).index(column.id)
        )

        for column_index, column_data in reversed(list(enumerate(self._columns.values()))):
            if column_index >= len(sorted_columns):
                continue

            column = sorted_columns[column_index]
            width = column_data.get("width")

            if width is not None:
                column.set_resizable(column.type != "icon")

            if not width:
                width = -1

            column.set_fixed_width(width)
            column.set_visible(True)

            if GTK_API_VERSION >= 4:
                self.widget.insert_column(0, column)
            else:
                self.widget.move_column_after(column, None)

        self.on_reset_sort_column()

    def on_column_header_menu(self, menu, _treeview):

        columns = self.widget.get_columns()
        visible_columns = [column for column in columns if column.get_visible()]
        menu.clear()

        sort_label = _("A_scending") if self._sort_type == Gtk.SortType.DESCENDING else _("De_scending")
        sort_menu = PopupMenu(self.window.application)
        sort_menu.add_items(
            ("#" + sort_label, self.on_invert_sort_order),
            ("", None),
            ("#" + _("_Reset Sort Column"), self.on_reset_sort_column)
        )

        for column_num, column in enumerate(columns, start=1):
            title = column.get_title()

            if not title:
                title = _("Column #%i") % column_num

            menu.add_items(
                ("$" + title, None)
            )
            menu.update_model()
            menu.actions[title].set_state(GLib.Variant.new_boolean(column in visible_columns))

            if column in visible_columns:
                menu.actions[title].set_enabled(len(visible_columns) > 1)

            menu.actions[title].connect("activate", self.on_column_header_toggled, column)

        menu.add_items(
            ("", None),
            (">" + _("_Sort Order"), sort_menu),
            ("#" + _("Reset Columns"), self.on_reset_columns)
        )
        menu.update_model()

    def on_column_position_changed(self, column, _param):
        """Save column position and width to config."""

        column_id = column.id

        if GTK_API_VERSION >= 4:
            offset = column.get_fixed_width()
        else:
            offset = column.get_x_offset()

        if self._column_offsets.get(column_id) == offset:
            return

        self._column_offsets[column_id] = offset
        self.save_columns()

    def on_column_position_changed_header(self, _column_header, _param):
        """Save column position and width to config."""

        GLib.idle_add(self.save_columns)

    def on_key_move_cursor(self, _widget, step, *_args):

        if step != Gtk.MovementStep.BUFFER_ENDS:
            return

        # We are scrolling to the end using the End key. Disable the
        # auto-scroll workaround to actually change the scroll adjustment value.
        self._is_scrolling_to_row = True

    def on_v_adjustment_value(self, *_args):

        upper = self._v_adjustment.get_upper()

        if not self._is_scrolling_to_row and upper != self._v_adjustment_upper and self._v_adjustment_value <= 0:
            # When new rows are added while sorting is enabled, treeviews
            # auto-scroll to the new position of the currently visible row.
            # Disable this behavior while we're at the top to prevent jumping
            # to random positions as rows are populated.
            self._v_adjustment.set_value(0)
        else:
            self._v_adjustment_value = self._v_adjustment.get_value()

        self._v_adjustment_upper = upper
        self._is_scrolling_to_row = False

    def on_search_match(self, model, _column, search_term, iterator):

        if not search_term:
            return True

        accepted_column_types = {"text", "number"}

        for column_index, column_data in enumerate(self._columns.values()):
            if "column_type" not in column_data:
                continue

            if column_data["column_type"] not in accepted_column_types:
                continue

            column_value = model.get_value(iterator, column_index)

            if column_value and search_term.lower() in column_value.lower():
                return False

        return True

    def on_tooltip(self, _widget, pos_x, pos_y, _keyboard_mode, tooltip):

        bin_x, bin_y = self.widget.convert_widget_to_bin_window_coords(pos_x, pos_y)
        is_blank, path, column, _cell_x, _cell_y = self.widget.is_blank_at_pos(bin_x, bin_y)

        if is_blank:
            return False

        iterator = self.model.get_iter(path)

        if column.tooltip_callback:
            value = column.tooltip_callback(self, iterator)
        else:
            value = self.get_row_value(iterator, column.id)

        if not value:
            return False

        if not isinstance(value, str):
            return False

        if column.type == "icon":
            value = self.get_icon_label(column, value)

        # Update tooltip position
        self.widget.set_tooltip_cell(tooltip, path, column)

        tooltip.set_text(value)
        return True

    def on_copy_cell_data_accelerator(self, *_args):
        """Ctrl+C: copy cell data."""

        path, column = self.widget.get_cursor()

        if path is None:
            return False

        iterator = self.model.get_iter(path)
        value = str(self.model.get_value(iterator, column.sort_column_id))

        if not value:
            return False

        if column.type == "icon":
            value = self.get_icon_label(column, value, is_short_country_label=True)

        clipboard.copy_text(value)
        return True

    def on_start_search(self, *_args):
        """Ctrl+F: start search."""

        self.widget.emit("start-interactive-search")

    def on_collapse_row_accelerator(self, *_args):
        """Left: collapse row."""

        iterator = self.get_focused_row()

        if iterator is None:
            return False

        return self.collapse_row(iterator)

    def on_collapse_row_blocked_accelerator(self, *_args):
        """minus: collapse row (block search)."""

        self.on_collapse_row_accelerator()
        return True

    def on_expand_row_accelerator(self, *_args):
        """Right: expand row."""

        iterator = self.get_focused_row()

        if iterator is None:
            return False

        return self.expand_row(iterator)

    def on_expand_row_blocked_accelerator(self, *_args):
        """plus, equal: expand row (block search)."""

        self.on_expand_row_accelerator()
        return True

    def on_expand_row_level_accelerator(self, *_args):
        """\backslash: collapse or expand to show subs."""

        iterator = self.get_focused_row()

        if iterator is None:
            return False

        self.collapse_row(iterator)  # show 2nd level
        self.expand_row(iterator)
        return True


# Legacy Functions (to be removed) #


def create_grouping_menu(window, active_mode, callback):

    action_id = f"grouping-{GLib.uuid_string_random()}"
    menu = Gio.Menu()

    menuitem = Gio.MenuItem.new(_("Ungrouped"), f"win.{action_id}::ungrouped")
    menu.append_item(menuitem)

    menuitem = Gio.MenuItem.new(_("Group by Folder"), f"win.{action_id}::folder_grouping")
    menu.append_item(menuitem)

    menuitem = Gio.MenuItem.new(_("Group by User"), f"win.{action_id}::user_grouping")
    menu.append_item(menuitem)

    state = GLib.Variant.new_string(active_mode)
    action = Gio.SimpleAction(name=action_id, parameter_type=state.get_type(), state=state)
    action.connect("change-state", callback)

    window.add_action(action)
    action.change_state(state)

    return menu


def set_treeview_selected_row(treeview, bin_x, bin_y):
    """Handles row selection when right-clicking in a treeview."""

    if GTK_API_VERSION >= 4:
        widget = treeview.pick(bin_x, bin_y, 0)

        while widget.get_css_name() != "cell" and widget != treeview:
            widget = widget.get_parent()

        if widget != treeview:
            #treeview.get_model().select_item(widget.get_position(), False)
            pass
        else:
            treeview.get_model().unselect_all()

        return

    pathinfo = treeview.get_path_at_pos(bin_x, bin_y)
    selection = treeview.get_selection()

    if pathinfo is not None:
        path, column, _cell_x, _cell_y = pathinfo

        # Make sure we don't attempt to select a single row if the row is already
        # in a selection of multiple rows, otherwise the other rows will be unselected
        if selection.count_selected_rows() <= 1 or not selection.path_is_selected(path):
            treeview.grab_focus()
            treeview.set_cursor(path, column, False)
    else:
        selection.unselect_all()
