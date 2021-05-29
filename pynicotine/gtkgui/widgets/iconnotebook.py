# COPYRIGHT (C) 2020-2021 Nicotine+ Team
# COPYRIGHT (C) 2016-2017 Michael Labouebe <gfarmerfr@free.fr>
# COPYRIGHT (C) 2008-2009 Quinox <quinox@users.sf.net>
# COPYRIGHT (C) 2006-2009 Daelstorm <daelstorm@gmail.com>
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

import sys

from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gtk

from pynicotine.gtkgui.utils import connect_key_press_event
from pynicotine.gtkgui.utils import get_key_press_event_args
from pynicotine.gtkgui.utils import parse_accelerator
from pynicotine.gtkgui.widgets.dialogs import option_dialog
from pynicotine.gtkgui.widgets.popupmenu import PopupMenu
from pynicotine.config import config


""" Icon Notebook """


class ImageLabel(Gtk.Box):

    def __init__(self, label="", onclose=None, closebutton=False, show_icon_start=False, show_icon_end=False):

        Gtk.Box.__init__(self)
        self.set_hexpand(False)

        self.closebutton = closebutton
        self.centered = False

        self.onclose = onclose

        self.label = Gtk.Label()
        self.label.set_halign(Gtk.Align.START)
        self.label.set_hexpand(True)
        self.label.show()

        self.text = label
        self.set_text(self.text)

        self.icon_start = Gtk.Image()
        self.icon_start.set_from_pixbuf(None)
        self.icon_name_start = ""

        if show_icon_start:
            self.icon_start.show()
        else:
            self.icon_start.hide()

        self.icon_end = Gtk.Image()
        self.icon_end.set_from_pixbuf(None)
        self.icon_name_end = ""

        if show_icon_end:
            self.icon_end.show()
        else:
            self.icon_end.hide()

        self._pack_children()

    def _pack_children(self):

        if hasattr(self, "box"):
            if Gtk.get_major_version() == 4:
                while self.box.get_first_child():
                    self.box.remove(self.box.get_first_child())
            else:
                for widget in self.box.get_children():
                    self.box.remove(widget)

            self.eventbox.remove(self.box)

        self.box = Gtk.Box()
        self.box.set_spacing(2)

        if Gtk.get_major_version() == 4:
            self.eventbox = Gtk.Box()
            self.append(self.eventbox)
            self.eventbox.append(self.box)
        else:
            self.eventbox = Gtk.EventBox()
            self.add(self.eventbox)
            self.eventbox.add(self.box)

        self.eventbox.show()

        if self.centered:
            self.set_halign(Gtk.Align.CENTER)
        else:
            self.set_halign(Gtk.Align.FILL)

        self.icon_start.set_margin_end(5)
        self.icon_end.set_margin_start(5)

        if Gtk.get_major_version() == 4:
            self.box.add = self.box.append

        self.box.add(self.icon_start)
        self.box.add(self.label)
        self.box.add(self.icon_end)
        self.box.show()

        if self.closebutton and self.onclose is not None:
            self._add_close_button()

    def _add_close_button(self):

        if hasattr(self, "button"):
            return

        close_image = Gtk.Image()
        self.button = Gtk.Button()

        if Gtk.get_major_version() == 4:
            close_image.set_from_icon_name("window-close-symbolic")
            self.button.set_child(close_image)
            self.button.set_has_frame(False)

            if sys.platform == "darwin":
                # Left align close button on macOS
                self.prepend(self.button)
            else:
                self.append(self.button)

        else:
            close_image.set_from_icon_name("window-close-symbolic", Gtk.IconSize.MENU)
            self.button.add(close_image)
            self.button.set_relief(Gtk.ReliefStyle.NONE)
            self.button.show_all()
            self.add(self.button)

        if self.onclose is not None:
            self.button.connect("clicked", self.onclose)

    def _remove_close_button(self):

        if not hasattr(self, "button"):
            return

        self.remove(self.button)
        del self.button

    def set_onclose(self, closebutton):
        self.closebutton = closebutton

        if self.closebutton:
            self._add_close_button()
        else:
            self._remove_close_button()

    def set_centered(self, centered):
        self.centered = centered
        self._pack_children()

    def set_text_color(self, notify=None, text=None):

        color = config.sections["ui"]["tab_default"]

        if config.sections["notifications"]["notification_tab_colors"]:
            if notify == 1:
                color = config.sections["ui"]["tab_changed"]
            elif notify == 2:
                color = config.sections["ui"]["tab_hilite"]

        try:
            rgba = Gdk.RGBA()
            rgba.parse(color)
        except Exception:
            color = ""

        if text is not None:
            self.text = text

        if not color:
            self.label.set_text("%s" % self.text)
        else:
            from html import escape
            self.label.set_markup("<span foreground=\"%s\">%s</span>" % (color, escape(self.text)))

    def set_show_icon_start(self, show):
        self.icon_start.set_visible(show)

    def set_icon_start(self, icon_name):

        if icon_name == self.icon_name_start:
            return

        self.icon_name_start = icon_name

        if icon_name:
            if Gtk.get_major_version() == 4:
                self.icon_start.set_from_icon_name(icon_name)
            else:
                self.icon_start.set_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        else:
            self.icon_start.set_from_pixbuf(None)

    def get_icon_start(self):
        return self.icon_name_start

    def set_show_icon_end(self, show):
        self.icon_end.set_visible(show)

    def set_icon_end(self, icon_name):

        if icon_name == self.icon_name_end:
            return

        self.icon_name_end = icon_name

        if icon_name:
            if Gtk.get_major_version() == 4:
                self.icon_end.set_from_icon_name(icon_name)
            else:
                self.icon_end.set_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        else:
            self.icon_end.set_from_pixbuf(None)

    def get_icon_end(self):
        return self.icon_name_end

    def set_text(self, lbl):
        self.set_text_color(notify=None, text=lbl)

    def get_text(self):
        return self.label.get_text()


class IconNotebook:
    """ This class implements a pseudo Gtk.Notebook
    On top of what a Gtk.Notebook provides:
    - Icons on the notebook tab
    - Dropdown menu for unread tabs
    - A few shortcuts
    """

    def __init__(self, tabclosers=False, show_hilite_image=True, reorderable=True, show_status_image=False, notebookraw=None):

        # We store the real Gtk.Notebook object
        self.notebook = notebookraw
        self.notebook.set_show_border(False)

        self.tabclosers = tabclosers
        self.reorderable = reorderable

        self._show_hilite_image = show_hilite_image
        self._show_status_image = show_status_image

        self.key_controller = connect_key_press_event(self.notebook, self.on_key_press_event)
        self.notebook.connect("switch-page", self.on_switch_page)

        if Gtk.get_major_version() == 4:
            self.window = self.notebook.get_root()

            self.unread_button = Gtk.MenuButton.new()
            self.unread_button.set_icon_name("emblem-important-symbolic")
            self.unread_button.set_has_frame(False)
        else:
            self.window = self.notebook.get_toplevel()
            self.popup_enable()

            self.unread_button = Gtk.MenuButton.new()
            self.unread_button.set_image(Gtk.Image.new_from_icon_name("emblem-important-symbolic", Gtk.IconSize.BUTTON))
            self.unread_button.set_relief(Gtk.ReliefStyle.NONE)

        self.unread_button.set_tooltip_text(_("Unread Tabs"))
        self.unread_button.set_halign(Gtk.Align.CENTER)
        self.unread_button.set_valign(Gtk.Align.CENTER)

        context = self.unread_button.get_style_context()
        context.add_class("circular")

        self.notebook.set_action_widget(self.unread_button, Gtk.PackType.END)

        self.popup_menu_unread = PopupMenu(widget=self.unread_button)
        self.unread_button.set_menu_model(self.popup_menu_unread)
        self.unread_pages = []

    def get_labels(self, page):
        tab_label = self.notebook.get_tab_label(page)
        menu_label = self.notebook.get_menu_label(page)

        return tab_label, menu_label

    def set_reorderable(self, reorderable):

        self.reorderable = reorderable

        for i in range(self.notebook.get_n_pages()):
            page = self.notebook.get_nth_page(i)
            self.notebook.set_tab_reorderable(page, self.reorderable)

    def set_tab_closers(self, closers):

        self.tabclosers = closers

        for i in range(self.notebook.get_n_pages()):
            page = self.notebook.get_nth_page(i)
            tab_label, menu_label = self.get_labels(page)

            tab_label.set_onclose(self.tabclosers)

    def show_hilite_images(self, show_image=True):

        self._show_hilite_image = show_image

        for i in range(self.notebook.get_n_pages()):
            page = self.notebook.get_nth_page(i)
            tab_label, menu_label = self.get_labels(page)

            tab_label.set_show_icon_end(self._show_hilite_image)

    def show_status_images(self, show_image=True):

        self._show_status_image = show_image

        for i in range(self.notebook.get_n_pages()):
            page = self.notebook.get_nth_page(i)
            tab_label, menu_label = self.get_labels(page)

            tab_label.set_show_icon_start(self._show_status_image)

    def set_tab_pos(self, pos):
        self.notebook.set_tab_pos(pos)

    def append_page(self, page, label, onclose=None, fulltext=None, status=None):

        closebutton = self.tabclosers

        label_tab = ImageLabel(
            label, onclose, closebutton=closebutton,
            show_icon_end=self._show_hilite_image,
            show_icon_start=self._show_status_image
        )
        label_tab.set_icon_start(GLib.get_prgname() + "-status-offline")

        if fulltext is None:
            fulltext = label

        # menu for all tabs
        label_tab_menu = ImageLabel(label)

        if Gtk.get_major_version() == 4:
            self.gesture_click = Gtk.GestureClick()
            self.gesture_click.set_button(Gdk.BUTTON_MIDDLE)
            self.gesture_click.connect("pressed", self.on_tab_click_controller, page)
            label_tab.add_controller(self.gesture_click)

        else:
            label_tab.connect("button-press-event", self.on_tab_click_event, page)

        label_tab.show()

        Gtk.Notebook.append_page_menu(self.notebook, page, label_tab, label_tab_menu)

        if status:
            self.set_user_status(page, label, status)
        else:
            label_tab.set_tooltip_text(fulltext)

        self.notebook.set_tab_reorderable(page, self.reorderable)
        self.notebook.set_show_tabs(True)

    def remove_page(self, page):

        Gtk.Notebook.remove_page(self.notebook, self.page_num(page))

        if self.notebook.get_n_pages() == 0:
            self.notebook.set_show_tabs(False)

    def remove_all_pages_response(self, dialog, response_id, data):

        dialog.destroy()

        if response_id == Gtk.ResponseType.OK:
            for i in reversed(range(self.notebook.get_n_pages())):
                page = self.notebook.get_nth_page(i)
                tab_label, menu_label = self.get_labels(page)
                tab_label.onclose(dialog)

    def remove_all_pages(self):

        option_dialog(
            parent=self.window,
            title=_('Close All Tabs?'),
            message=_('Are you sure you wish to close all tabs?'),
            callback=self.remove_all_pages_response
        )

    def get_page_owner(self, page, items):

        n = self.page_num(page)
        page = self.get_nth_page(n)

        return next(owner for owner, tab in items.items() if tab.Main is page)

    def on_tab_popup(self, widget, page):
        # Dummy implementation
        pass

    def set_status_image(self, page, status):

        tab_label, menu_label = self.get_labels(page)

        if status == 1:
            icon_name = "away"
        elif status == 2:
            icon_name = "online"
        else:
            icon_name = "offline"

        icon_name = GLib.get_prgname() + "-status-" + icon_name
        tab_label.set_icon_start(icon_name)
        menu_label.set_icon_start(icon_name)

    def set_user_status(self, page, user, status):

        if status == 1:
            status_text = _("Away")
        elif status == 2:
            status_text = _("Online")
        else:
            status_text = _("Offline")

        if not config.sections["ui"]["tab_status_icons"]:
            self.set_text(page, "%s (%s)" % (user[:15], status_text))
        else:
            self.set_text(page, user)

        self.set_status_image(page, status)

        # Set a tab tooltip containing the user's status and name
        tab_label, menu_label = self.get_labels(page)
        tab_label.set_tooltip_text("%s (%s)" % (user, status_text))

    def set_hilite_image(self, page, status):

        tab_label, menu_label = self.get_labels(page)
        icon_name = None

        if status > 0:
            icon_name = (GLib.get_prgname() + "-hilite-notify", GLib.get_prgname() + "-hilite-default")[status - 1]

        if status == 1 and tab_label.get_icon_end() == GLib.get_prgname() + "-hilite-default":
            # Chat mentions have priority over normal notifications
            return

        tab_label.set_icon_end(icon_name)
        menu_label.set_icon_end(icon_name)

        # Determine if button for unread notifications should be shown
        if icon_name:
            if page not in self.unread_pages:
                self.unread_pages.append(page)
                self.popup_menu_unread.clear()

                for page in self.unread_pages:
                    tab_label, menu_label = self.get_labels(page)
                    self.popup_menu_unread.setup(
                        ("#" + tab_label.get_text(), self.set_unread_page, self.page_num(page))
                    )

                self.unread_button.show()
            return

        if page in self.unread_pages:
            self.unread_pages.remove(page)

        if not self.unread_pages:
            self.unread_button.hide()

    def set_text(self, page, label):

        tab_label, menu_label = self.get_labels(page)

        tab_label.set_text(label)
        menu_label.set_text(label)

    def set_text_colors(self, status):

        for i in range(self.notebook.get_n_pages()):
            page = self.notebook.get_nth_page(i)
            self.set_text_color(page, status)

    def set_text_color(self, page, status):

        tab_label, menu_label = self.get_labels(page)
        tab_label.set_text_color(status)

    def request_hilite(self, page):

        current = self.get_nth_page(self.get_current_page())
        if current == page:
            return

        self.set_hilite_image(page, status=2)
        self.set_text_color(page, status=2)

    def request_changed(self, page):

        current = self.get_nth_page(self.get_current_page())
        if current == page:
            return

        self.set_hilite_image(page, status=1)
        self.set_text_color(page, status=1)

    def get_current_page(self):
        return self.notebook.get_current_page()

    def set_current_page(self, page_num):
        return self.notebook.set_current_page(page_num)

    def set_unread_page(self, action, state, page_num):
        self.notebook.set_current_page(page_num)

    def get_nth_page(self, page_num):
        return self.notebook.get_nth_page(page_num)

    def page_num(self, page):
        return self.notebook.page_num(page)

    def popup_enable(self):
        self.notebook.popup_enable()

    def popup_disable(self):
        self.notebook.popup_disable()

    def show(self):
        self.notebook.show()

    def on_tab_click_controller(self, *args):

        page = args[-1]
        tab_label, menu_label = self.get_labels(page)
        tab_label.onclose(None)

    def on_tab_click_event(self, widget, event, page):

        if event.button == Gdk.BUTTON_MIDDLE:
            # Middle click
            self.on_tab_click_controller(page)

        return False

    def on_key_press_event(self, *args):

        keyval, keycode, state = get_key_press_event_args(*args)
        key, codes_w, mods = parse_accelerator("<Primary>w")
        key, codes_f4, mods = parse_accelerator("<Primary>F4")

        if state & mods:
            if keycode in codes_w or \
               keycode in codes_f4:
                # Ctrl+W and Ctrl+F4: close current tab

                page = self.get_nth_page(self.get_current_page())
                tab_label, menu_label = self.get_labels(page)
                tab_label.onclose(None)
                return True

        return False

    def on_switch_page(self, notebook, new_page, page_num):

        # Hide widgets on previous page for a performance boost
        current_page = self.get_nth_page(self.get_current_page())

        if Gtk.get_major_version() == 4:
            children = current_page
        else:
            children = current_page.get_children()

        for child in children:
            child.hide()

        if Gtk.get_major_version() == 4:
            children = new_page
        else:
            children = new_page.get_children()

        for child in children:
            child.show()

        # Dismiss tab notification
        self.set_hilite_image(new_page, status=0)
        self.set_text_color(new_page, status=0)
