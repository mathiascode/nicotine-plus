# SPDX-FileCopyrightText: 2020-2026 Nicotine+ Contributors
# SPDX-FileCopyrightText: 2009 quinox <quinox@users.sf.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from inspect import currentframe

from pynicotine.pluginsystem import BasePlugin


class Plugin(BasePlugin):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.settings = {}
        self.metasettings = {}

        # These are too noisy, don't enable them by default
        verbose_events = {"public_room_message_notification", "distrib_search_notification"}

        for function_name in Plugin.__dict__:
            if function_name.startswith("_"):
                continue

            self.settings[function_name] = (function_name not in verbose_events)
            self.metasettings[function_name] = {
                "description": f"{function_name}()",
                "group": "Logged Events" if function_name.endswith("_event") else "Logged Notifications",
                "type": "bool"
            }

        self.log("__init__()")

    def _trigger_log(self, parameter_arguments=""):

        function_name = currentframe().f_back.f_code.co_name

        if not self.settings[function_name]:
            return

        self.log(f"{function_name}({parameter_arguments})")

    def init(self):
        self._trigger_log()

    def disable(self):
        self._trigger_log()

    def loaded_notification(self):
        self._trigger_log()

    def unloaded_notification(self):
        self._trigger_log()

    def shutdown_notification(self):
        self._trigger_log()

    def public_room_message_notification(self, room_name, username, message):
        self._trigger_log(f"room_name={room_name}, username={username}, message={message}")

    def search_request_notification(self, search_term, username, token):
        self._trigger_log(f"search_term={search_term}, username={username}, token={token}")

    def distrib_search_notification(self, search_term, username, token):
        self._trigger_log(f"search_term={search_term}, username={username}, token={token}")

    def incoming_private_chat_event(self, username, message):
        self._trigger_log(f"username={username}, message={message}")

    def incoming_private_chat_notification(self, username, message):
        self._trigger_log(f"username={username}, message={message}")

    def incoming_public_chat_event(self, room_name, username, message):
        self._trigger_log(f"room_name={room_name}, username={username}, message={message}")

    def incoming_public_chat_notification(self, room_name, username, message):
        self._trigger_log(f"room_name={room_name}, username={username}, message={message}")

    def outgoing_private_chat_event(self, username, message):
        self._trigger_log(f"username={username}, message={message}")

    def outgoing_private_chat_notification(self, username, message):
        self._trigger_log(f"username={username}, message={message}")

    def outgoing_public_chat_event(self, room_name, message):
        self._trigger_log(f"room_name={room_name}, message={message}")

    def outgoing_public_chat_notification(self, room_name, message):
        self._trigger_log(f"room_name={room_name}, message={message}")

    def outgoing_global_search_event(self, search_term):
        self._trigger_log(f"search_term={search_term}")

    def outgoing_room_search_event(self, room_name, search_term):
        self._trigger_log(f"room_name={room_name}, search_term={search_term}")

    def outgoing_buddy_search_event(self, search_term):
        self._trigger_log(f"search_term={search_term}")

    def outgoing_user_search_event(self, users, search_term):
        self._trigger_log(f"users={users}, search_term={search_term}")

    def user_resolve_notification(self, username, ip_address, port, country_code):
        self._trigger_log(f"username={username}, ip_address={ip_address}, port={port}, country_code={country_code}")

    def server_connect_notification(self):
        self._trigger_log()

    def server_disconnect_notification(self, userchoice):
        self._trigger_log(f"userchoice={userchoice}")

    def join_chatroom_notification(self, room_name):
        self._trigger_log(f"room_name={room_name}")

    def leave_chatroom_notification(self, room_name):
        self._trigger_log(f"room_name={room_name}")

    def user_join_chatroom_notification(self, room_name, username):
        self._trigger_log(f"room_name={room_name}, username={username}")

    def user_leave_chatroom_notification(self, room_name, username):
        self._trigger_log(f"room_name={room_name}, username={username}")

    def private_room_membership_granted_notification(self, room_name):
        self._trigger_log(f"room_name={room_name}")

    def private_room_membership_revoked_notification(self, room_name):
        self._trigger_log(f"room_name={room_name}")

    def private_room_member_added_notification(self, room_name, username):
        self._trigger_log(f"room_name={room_name}, username={username}")

    def private_room_member_removed_notification(self, room_name, username):
        self._trigger_log(f"room_name={room_name}, username={username}")

    def private_room_operatorship_granted_notification(self, room_name):
        self._trigger_log(f"room_name={room_name}")

    def private_room_operatorship_revoked_notification(self, room_name):
        self._trigger_log(f"room_name={room_name}")

    def private_room_operator_added_notification(self, room_name, username):
        self._trigger_log(f"room_name={room_name}, username={username}")

    def private_room_operator_removed_notification(self, room_name, username):
        self._trigger_log(f"room_name={room_name}, username={username}")

    def user_stats_notification(self, username, stats):
        self._trigger_log(f"username={username}, stats={stats}")

    def user_status_notification(self, username, status, privileged):
        self._trigger_log(f"username={username}, status={status}, privileged={privileged}")

    def upload_queued_notification(self, username, virtual_path, real_path):
        self._trigger_log(f"username={username}, virtual_path={virtual_path}, real_path={real_path}")

    def upload_started_notification(self, username, virtual_path, real_path):
        self._trigger_log(f"username={username}, virtual_path={virtual_path}, real_path={real_path}")

    def upload_finished_notification(self, username, virtual_path, real_path):
        self._trigger_log(f"username={username}, virtual_path={virtual_path}, real_path={real_path}")

    def download_started_notification(self, username, virtual_path, real_path):
        self._trigger_log(f"username={username}, virtual_path={virtual_path}, real_path={real_path}")

    def download_finished_notification(self, username, virtual_path, real_path):
        self._trigger_log(f"username={username}, virtual_path={virtual_path}, real_path={real_path}")
