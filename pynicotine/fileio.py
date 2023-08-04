# COPYRIGHT (C) 2022-2023 Nicotine+ Contributors
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

from collections import deque
from threading import Thread

from pynicotine.events import events


class File:
    __slots__ = ("path", "handle", "final_size", "current_size", "queue")

    def __init__(self, path, handle, final_size, current_size):
        self.path = path
        self.handle = handle
        self.final_size = final_size
        self.current_size = current_size

        self.queue = deque()


class FileIO:

    SLEEP_MIN_IDLE = 0.016  # ~60 times per second

    def __init__(self):

        self._files = {}
        self._scheduled_files = deque()
        self._scheduled_writes = deque()
        self._scheduled_closures = deque()
        self._is_active = True

        for event_name, callback in (
            ("close-file", self._close_file),
            ("open-file", self._open_file),
            ("write-file", self._write_file)
        ):
            events.connect(event_name, callback)

        Thread(target=self._run, name="FileIOThread", daemon=True).start()

    def _open_file(self, file_path, file_handle, current_size, final_size):
        self._scheduled_files.append((file_path, file_handle, current_size, final_size))

    def _write_file(self, file_path, data):
        self._scheduled_writes.append((file_path, data))

    def _close_file(self, file_path):
        self._scheduled_closures.append(file_path)

    def _run(self):

        while self._is_active:
            # Scheduled events additions/removals from other threads
            while self._scheduled_files:
                file_path, file_handle, current_size, final_size = self._scheduled_files.popleft()

                self._files[file_path] = File(path=file_path, handle=file_handle, final_size=final_size, current_size=current_size)

            while self._scheduled_writes:
                file_path, data = self._scheduled_writes.popleft()
                self._files[file_path].queue.append(data)

            for file_obj in self._files.values():
                if not file_obj.queue:
                    continue

                try:
                    byte_obj = file_obj.queue.popleft()
                    file_obj.handle.write(byte_obj)
                    file_obj.current_size += len(byte_obj)

                    if file_obj.current_size >= file_obj.final_size:
                        events.emit("write-file-finished", file_obj.path)

                except (OSError, ValueError) as error:
                    self._scheduled_closures.append(file_obj.path)
                    events.emit("write-file-failed", file_obj.path, error)

            while self._scheduled_closures:
                file_path = self._scheduled_closures.popleft()
                file_obj = self._files.pop(file_path, None)

                if file_obj is not None:
                    file_obj.handle.close()

            time.sleep(self.SLEEP_MIN_IDLE)
