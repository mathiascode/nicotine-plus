# SPDX-FileCopyrightText: 2021-2025 Nicotine+ Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

import sys

from gi.repository import Gdk
from gi.repository import Gtk

from pynicotine.gtkgui.application import GTK_API_VERSION


class Accelerator:

    if GTK_API_VERSION >= 4:
        shortcut_triggers = {}
    else:
        KEYMAP = Gdk.Keymap.get_for_display(Gdk.Display.get_default())  # pylint: disable=c-extension-no-member
        keycodes_mods = {}

    def __init__(self, accelerator, widget, callback, user_data=None):

        if GTK_API_VERSION >= 4:
            if sys.platform == "darwin":
                # Use Command key instead of Ctrl in accelerators on macOS
                accelerator = accelerator.replace("<Primary>", "<Meta>")

            shortcut_trigger = self.shortcut_triggers.get(accelerator)

            if not hasattr(widget, "shortcut_controller"):
                widget.shortcut_controller = Gtk.ShortcutController(
                    propagation_phase=Gtk.PropagationPhase.CAPTURE
                )
                widget.add_controller(widget.shortcut_controller)

            if not shortcut_trigger:
                self.shortcut_triggers[accelerator] = shortcut_trigger = Gtk.ShortcutTrigger.parse_string(accelerator)

            widget.shortcut_controller.add_shortcut(
                Gtk.Shortcut(
                    trigger=shortcut_trigger,
                    action=Gtk.CallbackAction.new(callback, user_data)
                )
            )
            return

        # GTK 3 replacement for Gtk.ShortcutController
        self.keycodes, self.required_mods = self.parse_accelerator(accelerator)
        self.callback = callback
        self.user_data = user_data

        widget.connect("key-press-event", self._activate_accelerator)

    @classmethod
    def parse_accelerator(cls, accelerator):

        keycodes_mods_accel = cls.keycodes_mods.get(accelerator)

        if not keycodes_mods_accel:
            *_args, key, mods = Gtk.accelerator_parse(accelerator)

            if key:
                _valid, keys = cls.KEYMAP.get_entries_for_keyval(key)
                keycodes = {key.keycode for key in keys}
            else:
                keycodes = []

            cls.keycodes_mods[accelerator] = keycodes_mods_accel = (keycodes, mods)

        return keycodes_mods_accel

    def _activate_accelerator(self, widget, event):

        activated_mods = event.state
        required_mods = self.required_mods
        excluded_mods = ALL_MODIFIERS & ~required_mods

        if required_mods & ~activated_mods:
            # Missing required modifiers
            return False

        if activated_mods & excluded_mods:
            # Too many/irrelevant modifiers
            return False

        if event.hardware_keycode not in self.keycodes:
            # Invalid key
            return False

        return self.callback(widget, None, self.user_data)


if GTK_API_VERSION == 3:
    ALL_MODIFIERS = (Accelerator.parse_accelerator("<Primary>")[1]
                     | Accelerator.parse_accelerator("<Shift>")[1]
                     | Accelerator.parse_accelerator("<Alt>")[1])
else:
    ALL_MODIFIERS = []
