# SPDX-FileCopyrightText: 2025 Nicotine+ Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

from pynicotine.events import events
from pynicotine.pluginsystem import BasePlugin


class Plugin(BasePlugin):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.settings = {
            "watch_all_rooms": True,
            "prioritize_buddies": False,
            "rooms": []
        }
        self.metasettings = {
            "watch_all_rooms": {
                "description": "Watch every joined private room",
                "type": "bool"
            },
            "prioritize_buddies": {
                "description": "Give buddies priority status",
                "type": "bool"
            },
            "rooms": {
                "description": "Watched private rooms:",
                "type": "list string"
            }
        }

    def private_room_member_added_notification(self, room_name, username):

        if username == self.core.users.login_username:
            return

        if not self.settings["watch_all_rooms"] and room_name not in self.settings["rooms"]:
            return

        self.core.buddies.add_buddy(username)

        if not self.core.buddies.users[username].note:
            self.core.buddies.set_buddy_note(username, f"Auto-Buddy member in private room {room_name}")

        if self.settings["prioritize_buddies"]:
            self.core.buddies.set_buddy_prioritized(username, True)
