# COPYRIGHT (C) 2020-2022 Nicotine+ Contributors
# COPYRIGHT (C) 2016-2017 Michael Labouebe <gfarmerfr@free.fr>
# COPYRIGHT (C) 2016 Mutnick <muhing@yahoo.com>
# COPYRIGHT (C) 2013 eLvErDe <gandalf@le-vert.net>
# COPYRIGHT (C) 2008-2012 quinox <quinox@users.sf.net>
# COPYRIGHT (C) 2009 hedonist <ak@sensi.org>
# COPYRIGHT (C) 2006-2009 daelstorm <daelstorm@gmail.com>
# COPYRIGHT (C) 2003-2004 Hyriand <hyriand@thegraveyard.org>
# COPYRIGHT (C) 2001-2003 Alexander Kanavin
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

""" This module contains classes that deal with file transfers:
the transfer manager.
"""

import json
import os
import os.path
import re
import stat
import time

from collections import defaultdict
from collections import deque
from collections import OrderedDict
from operator import itemgetter

from pynicotine import slskmessages
from pynicotine.config import config
from pynicotine.logfacility import log
from pynicotine.scheduler import scheduler
from pynicotine.slskmessages import increment_token
from pynicotine.slskmessages import TransferDirection
from pynicotine.slskmessages import UserStatus
from pynicotine.utils import execute_command
from pynicotine.utils import clean_file
from pynicotine.utils import clean_path
from pynicotine.utils import encode_path
from pynicotine.utils import get_result_bitrate_length
from pynicotine.utils import human_speed
from pynicotine.utils import load_file
from pynicotine.utils import truncate_string_byte
from pynicotine.utils import write_file_and_backup


class Transfer:
    """ This class holds information about a single transfer """

    __slots__ = ("sock", "user", "filename",
                 "path", "token", "size", "file", "start_time", "last_update",
                 "current_byte_offset", "last_byte_offset", "speed", "time_elapsed",
                 "time_left", "modifier", "queue_position", "bitrate", "length",
                 "iterator", "status", "legacy_attempt", "size_changed")

    def __init__(self, user=None, filename=None, path=None, status=None, token=None, size=0,
                 current_byte_offset=None, bitrate=None, length=None):
        self.user = user
        self.filename = filename
        self.path = path
        self.size = size
        self.status = status
        self.token = token
        self.current_byte_offset = current_byte_offset
        self.bitrate = bitrate
        self.length = length

        self.sock = None
        self.file = None
        self.queue_position = 0
        self.modifier = None
        self.start_time = None
        self.last_update = None
        self.last_byte_offset = None
        self.speed = None
        self.time_elapsed = 0
        self.time_left = None
        self.iterator = None
        self.legacy_attempt = False
        self.size_changed = False


class Transfers:
    """ This is the transfers manager """

    def __init__(self, core, queue, network_callback, ui_callback=None):

        self.core = core
        self.queue = queue
        self.allow_saving_transfers = False
        self.downloads = deque()
        self.uploads = deque()
        self.active_downloads = set()
        self.active_uploads = set()
        self.privileged_users = set()
        self.requested_folders = defaultdict(dict)
        self.transfer_request_times = {}
        self.upload_speed = 0
        self.token = 0

        self.user_update_counter = 0
        self.user_update_counters = {}

        self.downloads_file_name = os.path.join(config.data_dir, 'downloads.json')
        self.uploads_file_name = os.path.join(config.data_dir, 'uploads.json')

        self.network_callback = network_callback
        self.downloadsview = getattr(ui_callback, "downloads", None)
        self.uploadsview = getattr(ui_callback, "uploads", None)

        self.transfer_timeout_timer_id = None
        self.downloads_timer_id = None
        self.upload_queue_timer_id = None
        self.retry_download_limits_timer_id = None
        self.retry_failed_uploads_timer_id = None

        # Save list of transfers every minute
        scheduler.add(delay=60, callback=lambda: self.network_callback([slskmessages.SaveTransfers()]), repeat=True)

        self.update_download_filters()

    def init_transfers(self):

        self.add_stored_transfers("downloads")
        self.add_stored_transfers("uploads")

        if self.downloadsview:
            self.downloadsview.init_transfers(self.downloads)

        if self.uploadsview:
            self.uploadsview.init_transfers(self.uploads)

        self.allow_saving_transfers = True

    def server_login(self):

        self.requested_folders.clear()
        self.update_limits()
        self.watch_stored_downloads()

        # Check for transfer timeouts
        self.transfer_timeout_timer_id = scheduler.add(delay=1, callback=self._check_transfer_timeouts, repeat=True)

        # Request queue position of queued downloads and retry failed downloads every 3 minutes
        self.downloads_timer_id = scheduler.add(
            delay=180, callback=lambda: self.network_callback([slskmessages.CheckDownloads()]), repeat=True
        )

        # Check if queued uploads can be started every 10 seconds
        self.upload_queue_timer_id = scheduler.add(
            delay=10, callback=lambda: self.network_callback([slskmessages.CheckUploadQueue()]), repeat=True
        )

        # Re-queue limited downloads every 12 minutes
        self.retry_download_limits_timer_id = scheduler.add(
            delay=720, callback=lambda: self.network_callback([slskmessages.RetryDownloadLimits()]), repeat=True
        )

        # Re-queue timed out uploads every 3 minutes
        self.retry_failed_uploads_timer_id = scheduler.add(
            delay=180, callback=lambda: self.network_callback([slskmessages.RetryFailedUploads()]), repeat=True
        )

        if self.downloadsview:
            self.downloadsview.server_login()

        if self.uploadsview:
            self.uploadsview.server_login()

    """ Load Transfers """

    def get_download_queue_file_name(self):

        data_dir = config.data_dir
        downloads_file_json = os.path.join(data_dir, 'downloads.json')
        downloads_file_1_4_2 = os.path.join(data_dir, 'config.transfers.pickle')
        downloads_file_1_4_1 = os.path.join(data_dir, 'transfers.pickle')

        if os.path.exists(encode_path(downloads_file_json)):
            # New file format
            return downloads_file_json

        if os.path.exists(encode_path(downloads_file_1_4_2)):
            # Nicotine+ 1.4.2+
            return downloads_file_1_4_2

        if os.path.exists(encode_path(downloads_file_1_4_1)):
            # Nicotine <=1.4.1
            return downloads_file_1_4_1

        # Fall back to new file format
        return downloads_file_json

    def get_upload_list_file_name(self):

        data_dir = config.data_dir
        uploads_file_json = os.path.join(data_dir, 'uploads.json')

        return uploads_file_json

    @staticmethod
    def load_transfers_file(transfers_file):
        """ Loads a file of transfers in json format """

        transfers_file = encode_path(transfers_file)

        if not os.path.isfile(transfers_file):
            return None

        with open(transfers_file, encoding="utf-8") as handle:
            return json.load(handle)

    @staticmethod
    def load_legacy_transfers_file(transfers_file):
        """ Loads a download queue file in pickle format (legacy) """

        transfers_file = encode_path(transfers_file)

        if not os.path.isfile(transfers_file):
            return None

        with open(transfers_file, "rb") as handle:
            from pynicotine.utils import RestrictedUnpickler
            return RestrictedUnpickler(handle, encoding="utf-8").load()

    def load_transfers(self, transfer_type):

        load_func = self.load_transfers_file

        if transfer_type == "uploads":
            transfers_file = self.get_upload_list_file_name()
        else:
            transfers_file = self.get_download_queue_file_name()

        if transfer_type == "downloads" and not transfers_file.endswith("downloads.json"):
            load_func = self.load_legacy_transfers_file

        return load_file(transfers_file, load_func)

    def add_stored_transfers(self, transfer_type):

        transfers = self.load_transfers(transfer_type)

        if not transfers:
            return

        if transfer_type == "uploads":
            transfer_list = self.uploads
        else:
            transfer_list = self.downloads

        for transfer_row in transfers:
            num_attributes = len(transfer_row)

            if num_attributes < 3:
                continue

            # User / filename / path
            user = transfer_row[0]

            if not isinstance(user, str):
                continue

            filename = transfer_row[1]

            if not isinstance(filename, str):
                continue

            path = transfer_row[2]

            if not isinstance(path, str):
                continue

            # Status
            loaded_status = None

            if num_attributes >= 4:
                loaded_status = str(transfer_row[3])

            if transfer_type == "uploads" and loaded_status != "Finished":
                # Only finished uploads are supposed to be restored
                continue

            if loaded_status in ("Aborted", "Paused"):
                status = "Paused"

            elif loaded_status in ("Filtered", "Finished"):
                status = loaded_status

            else:
                status = "User logged off"

            # Size / offset
            size = 0
            current_byte_offset = None

            if num_attributes >= 5:
                loaded_size = transfer_row[4]

                if loaded_size and isinstance(loaded_size, (int, float)):
                    size = int(loaded_size)

            if num_attributes >= 6:
                loaded_byte_offset = transfer_row[5]

                if loaded_byte_offset and isinstance(loaded_byte_offset, (int, float)):
                    current_byte_offset = int(loaded_byte_offset)

            # Bitrate / length
            bitrate = length = None

            if num_attributes >= 7:
                loaded_bitrate = transfer_row[6]

                if loaded_bitrate is not None:
                    bitrate = str(loaded_bitrate)

            if num_attributes >= 8:
                loaded_length = transfer_row[7]

                if loaded_length is not None:
                    length = str(loaded_length)

            transfer_list.appendleft(
                Transfer(
                    user=user, filename=filename, path=path, status=status, size=size,
                    current_byte_offset=current_byte_offset, bitrate=bitrate, length=length
                )
            )

    def watch_stored_downloads(self):
        """ When logging in, we request to watch the status of our downloads """

        users = set()

        for download in self.downloads:
            if download.status in ("Filtered", "Finished"):
                continue

            users.add(download.user)

        for user in users:
            self.core.watch_user(user)

    """ Privileges """

    def set_privileged_users(self, user_list):
        for user in user_list:
            self.add_to_privileged(user)

    def add_to_privileged(self, user):
        self.privileged_users.add(user)

    def remove_from_privileged(self, user):
        if user in self.privileged_users:
            self.privileged_users.remove(user)

    def is_privileged(self, user):

        if not user:
            return False

        if user in self.privileged_users:
            return True

        return self.is_buddy_prioritized(user)

    def is_buddy_prioritized(self, user):

        if not user:
            return False

        for row in config.sections["server"]["userlist"]:
            if not row or not isinstance(row, list):
                continue

            if user == str(row[0]):
                # All users
                if config.sections["transfers"]["preferfriends"]:
                    return True

                # Only explicitly prioritized users
                try:
                    return bool(row[3])  # Prioritized column
                except IndexError:
                    return False

        return False

    """ File Actions """

    @staticmethod
    def get_file_size(filename):

        try:
            size = os.path.getsize(encode_path(filename))
        except Exception:
            # file doesn't exist (remote files are always this)
            size = 0

        return size

    @staticmethod
    def close_file(file_handle, transfer):

        transfer.file = None

        if file_handle is None:
            return

        try:
            file_handle.close()

        except Exception as error:
            log.add_transfer("Failed to close file %(filename)s: %(error)s", {
                "filename": file_handle.name.decode("utf-8", "replace"),
                "error": error
            })

    """ Limits """

    def _update_regular_limits(self):
        """ Sends the regular speed limits to the networking thread """

        uselimit = config.sections["transfers"]["uselimit"]
        uploadlimit = config.sections["transfers"]["uploadlimit"]
        limitby = config.sections["transfers"]["limitby"]

        self.queue.append(slskmessages.SetUploadLimit(uselimit, uploadlimit, limitby))
        self.queue.append(slskmessages.SetDownloadLimit(config.sections["transfers"]["downloadlimit"]))

    def _update_alt_limits(self):
        """ Sends the alternative speed limits to the networking thread """

        uselimit = True
        uploadlimit = config.sections["transfers"]["uploadlimitalt"]
        limitby = config.sections["transfers"]["limitby"]

        self.queue.append(slskmessages.SetUploadLimit(uselimit, uploadlimit, limitby))
        self.queue.append(slskmessages.SetDownloadLimit(config.sections["transfers"]["downloadlimitalt"]))

    def update_limits(self):

        if config.sections["transfers"]["usealtlimits"]:
            self._update_alt_limits()
            return

        self._update_regular_limits()

    def allow_new_downloads(self, user=None):

        if not config.sections["transfers"]["use_download_slots"]:
            return True

        download_slot_limit = config.sections["transfers"]["download_slots"]

        if user:
            for download in self.active_downloads:
                if download.user == user:
                    return True

        if len(self.active_downloads) >= download_slot_limit:
            return False

        return True

    def queue_limit_reached(self, user):

        file_limit = config.sections["transfers"]["filelimit"]
        queue_size_limit = config.sections["transfers"]["queuelimit"] * 1024 * 1024

        if not file_limit and not queue_size_limit:
            return False, None

        num_files = 0
        queue_size = 0

        for upload in self.uploads:
            if upload.user != user or upload.status != "Queued":
                continue

            if file_limit:
                num_files += 1

                if num_files >= file_limit:
                    return True, "Too many files"

            if queue_size_limit:
                queue_size += upload.size

                if queue_size >= queue_size_limit:
                    return True, "Too many megabytes"

        return False, None

    def slot_limit_reached(self):

        upload_slot_limit = config.sections["transfers"]["uploadslots"]

        if upload_slot_limit <= 0:
            upload_slot_limit = 1

        if len(self.active_uploads) >= upload_slot_limit:
            return True

        return False

    def bandwidth_limit_reached(self):

        bandwidth_limit = config.sections["transfers"]["uploadbandwidth"] * 1024

        if not bandwidth_limit:
            return False

        bandwidth_sum = 0

        for upload in self.uploads:
            if upload.sock is not None and upload.speed is not None:
                bandwidth_sum += upload.speed

                if bandwidth_sum >= bandwidth_limit:
                    return True

        return False

    def allow_new_uploads(self):

        if self.core.shares.rescanning:
            return False

        if config.sections["transfers"]["useupslots"]:
            # Limit by upload slots
            if self.slot_limit_reached():
                return False

        else:
            # Limit by maximum bandwidth
            if self.bandwidth_limit_reached():
                return False

        # No limits
        return True

    def file_is_upload_queued(self, user, filename):

        statuses = ("Queued", "Getting status", "Transferring")

        return next(
            (upload.filename == filename and upload.status in statuses and upload.user == user
             for upload in self.uploads), False
        )

    @staticmethod
    def file_is_readable(filename, real_path):

        try:
            if os.access(encode_path(real_path), os.R_OK):
                return True

            log.add_transfer("Cannot access file, not sharing: %(virtual_name)s with real path %(path)s", {
                "virtual_name": filename,
                "path": real_path
            })

        except Exception:
            log.add_transfer(("Requested file path contains invalid characters or other errors, not sharing: "
                              "%(virtual_name)s with real path %(path)s"), {
                "virtual_name": filename,
                "path": real_path
            })

        return False

    """ Network Events """

    def get_user_status(self, msg):
        """ Server code: 7 """
        """ We get a status of a user and if he's online, we request a file from him """

        update = False
        username = msg.user
        user_offline = (msg.status == UserStatus.OFFLINE)
        download_statuses = ("Queued", "Getting status", "Too many files", "Too many megabytes", "Pending shutdown.",
                             "User logged off", "Connection timeout", "Remote file error", "Cancelled")
        upload_statuses = ("Getting status", "User logged off", "Connection timeout")

        for download in reversed(self.downloads.copy()):
            if (download.user == username
                    and (download.status in download_statuses or download.status.startswith("User limit of"))):
                if user_offline:
                    download.status = "User logged off"
                    self.abort_download(download, abort_reason=None)
                    update = True

                elif download.status == "User logged off":
                    self.get_file(username, download.filename, path=download.path, transfer=download, ui_callback=False)
                    update = True

        if self.downloadsview and update:
            self.downloadsview.update_model()

        update = False

        # We need a copy due to upload auto-clearing modifying the deque during iteration
        for upload in reversed(self.uploads.copy()):
            if upload.user == username and upload.status in upload_statuses:
                if user_offline:
                    if not self.auto_clear_upload(upload):
                        upload.status = "User logged off"
                        self.abort_upload(upload, abort_reason=None)

                    update = True

                elif upload.status == "User logged off":
                    if not self.auto_clear_upload(upload):
                        upload.status = "Cancelled"

                    update = True

        if self.uploadsview and update:
            self.uploadsview.update_model()

    def get_cant_connect_queue_file(self, username, filename, offline):
        """ We can't connect to the user, either way (QueueUpload). """

        for download in self.downloads:
            if download.filename != filename or download.user != username:
                continue

            log.add_transfer("Download attempt for file %(filename)s from user %(user)s timed out", {
                "filename": filename,
                "user": username
            })

            self.abort_download(download, abort_reason="User logged off" if offline else "Connection timeout")
            self.core.watch_user(username)
            break

    def get_cant_connect_upload(self, username, token, offline):
        """ We can't connect to the user, either way (TransferRequest, FileUploadInit). """

        for upload in self.uploads:
            if upload.token != token or upload.user != username:
                continue

            log.add_transfer("Upload attempt for file %(filename)s with token %(token)s to user %(user)s timed out", {
                "filename": upload.filename,
                "token": token,
                "user": username
            })

            if upload.sock is not None:
                log.add_transfer("Existing file connection for upload with token %s already exists?", token)
                return

            upload_cleared = offline and self.auto_clear_upload(upload)

            if not upload_cleared:
                self.abort_upload(upload, abort_reason="User logged off" if offline else "Connection timeout")

            self.core.watch_user(username)
            self.check_upload_queue()
            return

    def folder_contents_response(self, msg, check_num_files=True):
        """ Peer code: 37 """
        """ When we got a contents of a folder, get all the files in it, but
        skip the files in subfolders """

        username = msg.init.target_user
        file_list = msg.list

        log.add_transfer("Received response for folder content request from user %s", username)

        for i in file_list:
            for directory in file_list[i]:
                if os.path.commonprefix([i, directory]) != directory:
                    continue

                files = file_list[i][directory][:]
                num_files = len(files)

                if check_num_files and num_files > 100 and self.downloadsview:
                    self.downloadsview.download_large_folder(username, directory, num_files, msg)
                    return

                destination = self.get_folder_destination(username, directory)
                files.sort(key=itemgetter(1), reverse=config.sections["transfers"]["reverseorder"])

                log.add_transfer(("Attempting to download files in folder %(folder)s for user %(user)s. "
                                  "Destination path: %(destination)s"), {
                    "folder": directory,
                    "user": username,
                    "destination": destination
                })

                for file in files:
                    virtualpath = directory.rstrip('\\') + '\\' + file[1]
                    size = file[2]
                    h_bitrate, _bitrate, h_length, _length = get_result_bitrate_length(size, file[4])

                    self.get_file(
                        username, virtualpath, path=destination,
                        size=size, bitrate=h_bitrate, length=h_length)

    def queue_upload(self, msg):
        """ Peer code: 43 """
        """ Peer remotely queued a download (upload here). This is the modern replacement to
        a TransferRequest with direction 0 (download request). We will initiate the upload of
        the queued file later. """

        user = msg.init.target_user
        filename = msg.file

        log.add_transfer("Received upload request for file %(filename)s from user %(user)s", {
            "user": user,
            "filename": filename,
        })

        real_path = self.core.shares.virtual2real(filename)
        allowed, reason = self.check_queue_upload_allowed(user, msg.init.addr, filename, real_path, msg)

        log.add_transfer(("Upload request for file %(filename)s from user: %(user)s, "
                          "allowed: %(allowed)s, reason: %(reason)s"), {
            "filename": filename,
            "user": user,
            "allowed": allowed,
            "reason": reason
        })

        if not allowed:
            if reason and reason != "Queued":
                self.core.send_message_to_peer(user, slskmessages.UploadDenied(file=filename, reason=reason))

            return

        transfer = Transfer(user=user, filename=filename, path=os.path.dirname(real_path),
                            status="Queued", size=self.get_file_size(real_path))
        self.append_upload(user, filename, transfer)
        self.update_upload(transfer)

        self.core.pluginhandler.upload_queued_notification(user, filename, real_path)
        self.check_upload_queue()

    def transfer_request(self, msg):
        """ Peer code: 40 """

        user = msg.init.target_user

        if msg.direction == TransferDirection.UPLOAD:
            response = self.transfer_request_downloads(msg)

            log.add_transfer(("Responding to download request with token %(token)s for file %(filename)s "
                              "from user: %(user)s, allowed: %(allowed)s, reason: %(reason)s"), {
                "token": response.token, "filename": msg.file, "user": user,
                "allowed": response.allowed, "reason": response.reason
            })

        elif msg.direction == TransferDirection.DOWNLOAD:
            response = self.transfer_request_uploads(msg)

            if response is None:
                return

            log.add_transfer(("Responding to legacy upload request %(token)s for file %(filename)s "
                              "from user %(user)s, allowed: %(allowed)s, reason: %(reason)s"), {
                "token": response.token, "filename": msg.file, "user": user,
                "allowed": response.allowed, "reason": response.reason
            })

        else:
            log.add_transfer(("Received unknown transfer direction %(direction)s for file %(filename)s "
                              "from user %(user)s"), {
                "direction": msg.direction, "filename": msg.file, "user": user
            })
            return

        self.core.send_message_to_peer(user, response)

    def transfer_request_downloads(self, msg):

        user = msg.init.target_user
        filename = msg.file
        size = msg.filesize
        token = msg.token

        log.add_transfer("Received download request with token %(token)s for file %(filename)s from user %(user)s", {
            "token": token,
            "filename": filename,
            "user": user
        })

        cancel_reason = "Cancelled"
        accepted = True

        if not self.allow_new_downloads():
            cancel_reason = "Queued"
            accepted = False

        for download in self.downloads:
            if download.filename != filename or download.user != user:
                continue

            status = download.status

            if status == "Finished":
                # SoulseekQt sends "Complete" as the reason for rejecting the download if it exists
                cancel_reason = "Complete"
                accepted = False
                break

            if status in ("Paused", "Filtered"):
                accepted = False
                break

            if cancel_reason == "Queued":
                download.status = "Locally Queued"
                self.update_download(download)
                break

            # Remote peer is signaling a transfer is ready, attempting to download it

            # If the file is larger than 2GB, the SoulseekQt client seems to
            # send a malformed file size (0 bytes) in the TransferRequest response.
            # In that case, we rely on the cached, correct file size we received when
            # we initially added the download.

            if size > 0:
                if download.size != size:
                    # The remote user's file contents have changed since we queued the download
                    download.size_changed = True

                download.size = size

            download.token = token
            download.status = "Getting status"
            self.transfer_request_times[download] = time.time()
            self.active_downloads.add(download)

            self.update_download(download)
            return slskmessages.TransferResponse(allowed=True, token=token)

        # Check if download exists in our default download folder
        if self.get_existing_download_path(user, filename, "", size):
            cancel_reason = "Complete"
            accepted = False

        # If this file is not in your download queue, then it must be
        # a remotely initiated download and someone is manually uploading to you
        if accepted and self.can_upload(user):
            path = ""
            if config.sections["transfers"]["uploadsinsubdirs"]:
                parentdir = filename.replace('/', '\\').split('\\')[-2]
                path = os.path.join(config.sections["transfers"]["uploaddir"], user, parentdir)

            transfer = Transfer(user=user, filename=filename, path=path, status="Queued",
                                size=size, token=token)
            self.downloads.appendleft(transfer)
            self.update_download(transfer)
            self.core.watch_user(user)

            return slskmessages.TransferResponse(allowed=False, reason="Queued", token=token)

        log.add_transfer("Denied file request: User %(user)s, %(msg)s", {
            'user': user,
            'msg': str(vars(msg))
        })

        return slskmessages.TransferResponse(allowed=False, reason=cancel_reason, token=token)

    def transfer_request_uploads(self, msg):
        """ Remote peer is requesting to download a file through your upload queue.
        Note that the QueueUpload peer message has replaced this method of requesting
        a download in most clients. """

        user = msg.init.target_user
        filename = msg.file
        token = msg.token

        log.add_transfer("Received legacy upload request %(token)s for file %(filename)s from user %(user)s", {
            "token": token,
            "filename": filename,
            "user": user
        })

        # Is user allowed to download?
        real_path = self.core.shares.virtual2real(filename)
        allowed, reason = self.check_queue_upload_allowed(user, msg.init.addr, filename, real_path, msg)

        if not allowed:
            if reason:
                return slskmessages.TransferResponse(allowed=False, reason=reason, token=token)

            return None

        # All checks passed, user can queue file!
        self.core.pluginhandler.upload_queued_notification(user, filename, real_path)

        # Is user already downloading/negotiating a download?
        already_downloading = False

        for upload in self.active_uploads:
            if upload.user == user:
                already_downloading = True
                break

        if not self.allow_new_uploads() or already_downloading:
            transfer = Transfer(user=user, filename=filename, path=os.path.dirname(real_path),
                                status="Queued", size=self.get_file_size(real_path))
            self.append_upload(user, filename, transfer)
            self.update_upload(transfer)

            return slskmessages.TransferResponse(allowed=True, token=token)

        # All checks passed, starting a new upload.
        size = self.get_file_size(real_path)
        transfer = Transfer(user=user, filename=filename, path=os.path.dirname(real_path),
                            status="Getting status", token=token, size=size)

        self.transfer_request_times[transfer] = time.time()
        self.append_upload(user, filename, transfer)
        self.active_uploads.add(transfer)
        self.update_upload(transfer)

        return slskmessages.TransferResponse(allowed=True, token=token, filesize=size)

    def transfer_response(self, msg):
        """ Peer code: 41 """
        """ Received a response to the file request from the peer """

        username = msg.init.target_user
        token = msg.token
        reason = msg.reason

        log.add_transfer(("Received response for upload with token: %(token)s, allowed: %(allowed)s, "
                          "reason: %(reason)s, file size: %(size)s"), {
            "token": token,
            "allowed": msg.allowed,
            "reason": reason,
            "size": msg.filesize
        })

        if reason is not None:
            if reason in ("Queued", "Getting status", "Transferring", "Paused", "Filtered", "User logged off"):
                # Don't allow internal statuses as reason
                reason = "Cancelled"

            for upload in self.uploads:
                if upload.token != token or upload.user != username:
                    continue

                if upload.sock is not None:
                    log.add_transfer("Upload with token %s already has an existing file connection", token)
                    return

                self.abort_upload(upload, abort_reason=reason)

                if reason in ("Complete", "Finished"):
                    # A complete download of this file already exists on the user's end
                    self.upload_finished(upload)

                elif reason in ("Cancelled", "Disallowed extension"):
                    self.auto_clear_upload(upload)

                self.check_upload_queue()
                return

            return

        for upload in self.uploads:
            if upload.token != token or upload.user != username:
                continue

            if upload.sock is not None:
                log.add_transfer("Upload with token %s already has an existing file connection", token)
                return

            self.core.send_message_to_peer(upload.user, slskmessages.FileUploadInit(None, token=token))
            self.check_upload_queue()
            return

        log.add_transfer("Received unknown upload response: %s", str(vars(msg)))

    def transfer_timeout(self, msg):

        transfer = msg.transfer

        log.add_transfer("Transfer %(filename)s with token %(token)s for user %(user)s timed out", {
            "filename": transfer.filename,
            "token": transfer.token,
            "user": transfer.user
        })

        status = "Connection timeout"
        self.core.watch_user(transfer.user)

        if transfer in self.downloads:
            self.abort_download(transfer, abort_reason=status)

        elif transfer in self.uploads:
            self.abort_upload(transfer, abort_reason=status)

        if transfer in self.transfer_request_times:
            del self.transfer_request_times[transfer]

        self.check_upload_queue()

    def download_file_error(self, msg):
        """ Networking thread encountered a local file error for download """

        username = msg.user
        token = msg.token

        for download in self.downloads:
            if download.token != token or download.user != username:
                continue

            self.abort_download(download, abort_reason="Local file error")
            log.add(_("Download I/O error: %s"), msg.error)
            return

    def upload_file_error(self, msg):
        """ Networking thread encountered a local file error for upload """

        username = msg.user
        token = msg.token

        for upload in self.uploads:
            if upload.token != token or upload.user != username:
                continue

            self.abort_upload(upload, abort_reason="Local file error")

            log.add(_("Upload I/O error: %s"), msg.error)
            self.check_upload_queue()
            return

    def file_download_init(self, msg):
        """ A peer is requesting to start uploading a file to us """

        username = msg.init.target_user
        token = msg.token

        for download in self.downloads:
            if download.token != token or download.user != username:
                continue

            filename = download.filename

            log.add_transfer(("Received file download init with token %(token)s for file %(filename)s "
                              "from user %(user)s"), {
                "token": token,
                "filename": filename,
                "user": username
            })

            if download.sock is not None:
                log.add_transfer("Download already has an existing file connection, ignoring init message")
                self.queue.append(slskmessages.CloseConnection(msg.init.sock))
                return

            incomplete_folder = config.sections["transfers"]["incompletedir"]
            need_update = True
            download.sock = msg.init.sock

            if not incomplete_folder:
                if download.path:
                    incomplete_folder = download.path
                else:
                    incomplete_folder = self.get_default_download_folder(username)

            try:
                incomplete_folder_encoded = encode_path(incomplete_folder)

                if not os.path.isdir(incomplete_folder_encoded):
                    os.makedirs(incomplete_folder_encoded)

                if not os.access(incomplete_folder_encoded, os.R_OK | os.W_OK | os.X_OK):
                    raise OSError("Download directory %s Permissions error.\nDir Permissions: %s" %
                                  (incomplete_folder, oct(os.stat(incomplete_folder_encoded)[stat.ST_MODE] & 0o777)))

            except OSError as error:
                log.add(_("OS error: %s"), error)
                self.download_folder_error(download, error)

            else:
                try:
                    incomplete_path = self.get_incomplete_file_path(incomplete_folder, username, filename)
                    file_handle = open(encode_path(incomplete_path), 'ab+')  # pylint: disable=consider-using-with

                    try:
                        import fcntl
                        try:
                            fcntl.lockf(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        except OSError as error:
                            log.add(_("Can't get an exclusive lock on file - I/O error: %s"), error)
                    except ImportError:
                        pass

                    if download.size_changed:
                        # Remote user sent a different file size than we originally requested,
                        # wipe any existing data in the incomplete file to avoid corruption
                        file_handle.truncate(0)

                    # Seek to the end of the file for resuming the download
                    offset = file_handle.seek(0, os.SEEK_END)

                except OSError as error:
                    log.add(_("Download I/O error: %s"), error)
                    self.abort_download(download, abort_reason="Local file error")
                    need_update = False

                else:
                    download.file = file_handle
                    download.last_byte_offset = offset
                    download.queue_position = 0
                    download.last_update = time.time()
                    download.start_time = download.last_update - download.time_elapsed

                    self.core.statistics.append_stat_value("started_downloads", 1)
                    self.core.pluginhandler.download_started_notification(username, filename, incomplete_path)

                    log.add_download(
                        _("Download started: user %(user)s, file %(file)s"), {
                            "user": username,
                            "file": file_handle.name.decode("utf-8", "replace")
                        }
                    )

                    if download.size > offset:
                        download.status = "Transferring"
                        self.queue.append(slskmessages.DownloadFile(
                            init=msg.init, token=token, file=file_handle, leftbytes=(download.size - offset)
                        ))
                        self.queue.append(slskmessages.FileOffset(init=msg.init, offset=offset))

                    else:
                        self.download_finished(download, file_handle=file_handle)
                        need_update = False

            if self.downloadsview:
                self.downloadsview.new_transfer_notification()

            if need_update:
                self.update_download(download)

            return

        # Support legacy transfer system (clients: old Nicotine+ versions, slskd)
        # The user who requested the download initiates the file upload connection
        # in this case, but we always assume an incoming file init message is
        # FileDownloadInit

        log.add_transfer(("Received unknown file download init message with token %s, checking if peer "
                          "requested us to upload a file instead"), token)
        self.file_upload_init(msg)

    def file_upload_init(self, msg):
        """ We are requesting to start uploading a file to a peer """

        username = msg.init.target_user
        token = msg.token

        for upload in self.uploads:
            if upload.token != token or upload.user != username:
                continue

            filename = upload.filename

            log.add_transfer("Initializing upload with token %(token)s for file %(filename)s to user %(user)s", {
                "token": token,
                "filename": filename,
                "user": username
            })

            if upload.sock is not None:
                log.add_transfer("Upload already has an existing file connection, ignoring init message")
                self.queue.append(slskmessages.CloseConnection(msg.init.sock))
                return

            need_update = True
            upload.sock = msg.init.sock

            real_path = self.core.shares.virtual2real(filename)

            if not self.core.shares.file_is_shared(username, filename, real_path):
                self.abort_upload(upload, abort_reason="File not shared.")
                self.check_upload_queue()
                return

            try:
                # Open File
                file_handle = open(encode_path(real_path), "rb")  # pylint: disable=consider-using-with

            except OSError as error:
                log.add(_("Upload I/O error: %s"), error)
                self.abort_upload(upload, abort_reason="Local file error")
                self.check_upload_queue()

            else:
                upload.file = file_handle
                upload.queue_position = 0
                upload.last_update = time.time()
                upload.start_time = upload.last_update - upload.time_elapsed

                self.core.statistics.append_stat_value("started_uploads", 1)
                self.core.pluginhandler.upload_started_notification(username, filename, real_path)

                log.add_upload(
                    _("Upload started: user %(user)s, IP address %(ip)s, file %(file)s"), {
                        "user": username,
                        "ip": self.core.protothread.user_addresses.get(username),
                        "file": filename
                    }
                )

                if upload.size > 0:
                    upload.status = "Transferring"
                    self.queue.append(slskmessages.UploadFile(
                        init=msg.init, token=token, file=file_handle, size=upload.size
                    ))

                else:
                    self.upload_finished(upload, file_handle=file_handle)
                    need_update = False

            if self.uploadsview:
                self.uploadsview.new_transfer_notification()

            if need_update:
                self.update_upload(upload)

            return

        log.add_transfer("Unknown file upload init message with token %s", token)
        self.queue.append(slskmessages.CloseConnection(msg.init.sock))

    def upload_denied(self, msg):
        """ Peer code: 50 """

        user = msg.init.target_user
        filename = msg.file
        reason = msg.reason

        if reason in ("Getting status", "Transferring", "Paused", "Filtered", "User logged off", "Finished"):
            # Don't allow internal statuses as reason
            reason = "Cancelled"

        for download in self.downloads:
            if download.filename != filename or download.user != user:
                continue

            if download.status in ("Finished", "Paused"):
                # SoulseekQt also sends this message for finished downloads when unsharing files, ignore
                continue

            if reason in ("File not shared.", "File not shared", "Remote file error") and not download.legacy_attempt:
                # The peer is possibly using an old client that doesn't support Unicode
                # (Soulseek NS). Attempt to request file name encoded as latin-1 once.

                log.add_transfer("User %(user)s responded with reason '%(reason)s' for download request %(filename)s. "
                                 "Attempting to request file as latin-1.", {
                                     "user": user,
                                     "reason": reason,
                                     "filename": filename
                                 })

                self.abort_download(download, abort_reason=None)
                download.legacy_attempt = True
                self.get_file(user, filename, path=download.path, transfer=download)
                break

            if download.status == "Transferring":
                self.abort_download(download, abort_reason=None)

            download.status = reason
            self.update_download(download)

            log.add_transfer("Download request denied by user %(user)s for file %(filename)s. Reason: %(reason)s", {
                "user": user,
                "filename": filename,
                "reason": msg.reason
            })
            return

    def upload_failed(self, msg):
        """ Peer code: 46 """

        user = msg.init.target_user
        filename = msg.file

        for download in self.downloads:
            if download.filename != filename or download.user != user:
                continue

            if download.status in ("Finished", "Paused", "Download folder error", "Local file error",
                                   "User logged off"):
                # Check if there are more transfers with the same virtual path
                continue

            should_retry = not download.legacy_attempt

            if should_retry:
                # Attempt to request file name encoded as latin-1 once

                self.abort_download(download, abort_reason=None)
                download.legacy_attempt = True
                self.get_file(user, filename, path=download.path, transfer=download)
                break

            # Already failed once previously, give up
            self.abort_download(download, abort_reason="Remote file error")

            log.add_transfer("Upload attempt by user %(user)s for file %(filename)s failed. Reason: %(reason)s", {
                "filename": filename,
                "user": user,
                "reason": download.status
            })
            return

    def file_download(self, msg):
        """ A file download is in progress """

        username = msg.init.target_user
        token = msg.token

        for download in self.downloads:
            if download.token != token or download.user != username:
                continue

            if download in self.transfer_request_times:
                del self.transfer_request_times[download]

            current_time = time.time()
            size = download.size

            download.status = "Transferring"
            download.time_elapsed = current_time - download.start_time
            download.current_byte_offset = current_byte_offset = (size - msg.leftbytes)
            byte_difference = current_byte_offset - download.last_byte_offset

            if byte_difference:
                self.core.statistics.append_stat_value("downloaded_size", byte_difference)

                if size > current_byte_offset or download.speed is None:
                    download.speed = int(max(0, byte_difference // max(1, current_time - download.last_update)))
                    download.time_left = (size - current_byte_offset) // download.speed if download.speed else 0
                else:
                    download.time_left = 0

            download.last_byte_offset = current_byte_offset
            download.last_update = current_time

            self.update_download(download)
            return

    def file_upload(self, msg):
        """ A file upload is in progress """

        username = msg.init.target_user
        token = msg.token

        for upload in self.uploads:
            if upload.token != token or upload.user != username:
                continue

            if upload in self.transfer_request_times:
                del self.transfer_request_times[upload]

            current_time = time.time()
            size = upload.size

            if not upload.last_byte_offset:
                upload.last_byte_offset = msg.offset

            upload.status = "Transferring"
            upload.time_elapsed = current_time - upload.start_time
            upload.current_byte_offset = current_byte_offset = (msg.offset + msg.sentbytes)
            byte_difference = current_byte_offset - upload.last_byte_offset

            if byte_difference:
                self.core.statistics.append_stat_value("uploaded_size", byte_difference)

                if size > current_byte_offset or upload.speed is None:
                    upload.speed = int(max(0, byte_difference // max(1, current_time - upload.last_update)))
                    upload.time_left = (size - current_byte_offset) // upload.speed if upload.speed else 0
                else:
                    upload.time_left = 0

            upload.last_byte_offset = current_byte_offset
            upload.last_update = current_time

            self.update_upload(upload)
            return

    def download_connection_closed(self, msg):
        """ A file download connection has closed for any reason """

        username = msg.user
        token = msg.token

        for download in self.downloads:
            if download.token != token or download.user != username:
                continue

            if download.current_byte_offset is not None and download.current_byte_offset >= download.size:
                self.download_finished(download, file_handle=download.file)
                return

            status = None

            if download.status != "Finished":
                if self.core.user_statuses.get(download.user) == UserStatus.OFFLINE:
                    status = "User logged off"
                else:
                    status = "Cancelled"

            self.abort_download(download, abort_reason=status)
            return

    def upload_connection_closed(self, msg):
        """ A file upload connection has closed for any reason """

        username = msg.user
        token = msg.token
        timed_out = msg.timed_out

        # We need a copy due to upload auto-clearing modifying the deque during iteration
        for upload in self.uploads.copy():
            if upload.token != token or upload.user != username:
                continue

            if not timed_out and upload.current_byte_offset is not None and upload.current_byte_offset >= upload.size:
                # We finish the upload here in case the downloading peer has a slow/limited download
                # speed and finishes later than us

                if upload.speed is not None:
                    # Inform the server about the last upload speed for this transfer
                    log.add_transfer("Sending upload speed %s to the server", human_speed(upload.speed))
                    self.queue.append(slskmessages.SendUploadSpeed(upload.speed))

                self.upload_finished(upload, file_handle=upload.file)
                return

            if upload.status == "Finished":
                return

            status = None

            if self.core.user_statuses.get(upload.user) == UserStatus.OFFLINE:
                status = "User logged off"
            else:
                status = "Cancelled"

                # Transfer ended abruptly. Tell the peer to re-queue the file. If the transfer was
                # intentionally cancelled, the peer should ignore this message.
                self.core.send_message_to_peer(upload.user, slskmessages.UploadFailed(file=upload.filename))

            if not self.auto_clear_upload(upload):
                self.abort_upload(upload, abort_reason=status)

            self.check_upload_queue()
            return

    def place_in_queue_request(self, msg):
        """ Peer code: 51 """

        user = msg.init.target_user
        filename = msg.file
        privileged_user = self.is_privileged(user)
        queue_position = 0
        transfer = None

        if config.sections["transfers"]["fifoqueue"]:
            for upload in reversed(self.uploads):
                # Ignore non-queued files
                if upload.status != "Queued":
                    continue

                if not privileged_user or self.is_privileged(upload.user):
                    queue_position += 1

                # Stop counting on the matching file
                if upload.filename == filename and upload.user == user:
                    transfer = upload
                    break

        else:
            num_queued_users = len(self.user_update_counters)

            for upload in reversed(self.uploads):
                if upload.user != user:
                    continue

                # Ignore non-queued files
                if upload.status != "Queued":
                    continue

                queue_position += num_queued_users

                # Stop counting on the matching file
                if upload.filename == filename:
                    transfer = upload
                    break

        if queue_position > 0:
            self.queue.append(slskmessages.PlaceInQueue(init=msg.init, filename=filename, place=queue_position))

        if transfer is None:
            return

        # Update queue position in our list of uploads
        transfer.queue_position = queue_position
        self.update_upload(transfer, update_parent=False)

    def place_in_queue(self, msg):
        """ Peer code: 44 """
        """ The peer tells us our place in queue for a particular transfer """

        username = msg.init.target_user
        filename = msg.filename

        for download in self.downloads:
            if download.filename == filename and download.status == "Queued" and download.user == username:
                download.queue_position = msg.place
                self.update_download(download, update_parent=False)
                return

    """ Transfer Actions """

    def get_folder(self, user, folder):
        self.core.send_message_to_peer(user, slskmessages.FolderContentsRequest(directory=folder, token=1))

    def get_file(self, user, filename, path="", transfer=None, size=0, bitrate=None, length=None, ui_callback=True):

        path = clean_path(path, absolute=True)
        status = "Queued"

        if not self.allow_new_downloads(user):
            status = "Locally Queued"

        if transfer is None:
            for download in self.downloads:
                if download.filename == filename and download.path == path and download.user == user:
                    if download.status == "Finished":
                        # Duplicate finished download found, verify that it's still present on disk later
                        transfer = download
                        break

                    # Duplicate active/cancelled download found, stop here
                    return

            else:
                transfer = Transfer(
                    user=user, filename=filename, path=path,
                    status=status, size=size, bitrate=bitrate,
                    length=length
                )
                self.downloads.appendleft(transfer)
        else:
            transfer.filename = filename
            transfer.status = status
            transfer.token = None

        self.core.watch_user(user)

        if config.sections["transfers"]["enablefilters"]:
            try:
                downloadregexp = re.compile(config.sections["transfers"]["downloadregexp"], flags=re.IGNORECASE)

                if downloadregexp.search(filename) is not None:
                    log.add_transfer("Filtering: %s", filename)

                    if self.auto_clear_download(transfer):
                        return

                    self.abort_download(transfer, abort_reason="Filtered")

            except re.error:
                pass

        if UserStatus.OFFLINE in (self.core.user_status, self.core.user_statuses.get(user)):
            # Either we are offline or the user we want to download from is
            transfer.status = "User logged off"

        elif transfer.status != "Filtered":
            download_path = self.get_existing_download_path(user, filename, path, size)

            if download_path:
                transfer.status = "Finished"
                transfer.size = transfer.current_byte_offset = size

                log.add_transfer("File %s is already downloaded", download_path)

            elif transfer.status != "Locally Queued":
                log.add_transfer("Adding file %(filename)s from user %(user)s to download queue", {
                    "filename": filename,
                    "user": user
                })
                self.core.send_message_to_peer(
                    user, slskmessages.QueueUpload(file=filename, legacy_client=transfer.legacy_attempt))

        if ui_callback:
            self.update_download(transfer)

    def push_file(self, user, filename, size, path="", transfer=None, bitrate=None, length=None, locally_queued=False):

        real_path = self.core.shares.virtual2real(filename)
        size_attempt = self.get_file_size(real_path)

        if size_attempt > 0:
            size = size_attempt

        if transfer is None:
            if not path:
                path = os.path.dirname(real_path)

            transfer = Transfer(
                user=user, filename=filename, path=path,
                status="Queued", size=size, bitrate=bitrate,
                length=length
            )
            self.append_upload(user, filename, transfer)
        else:
            transfer.filename = filename
            transfer.size = size
            transfer.status = "Queued"
            transfer.token = None

        log.add_transfer("Initializing upload request for file %(file)s to user %(user)s", {
            'file': filename,
            'user': user
        })

        self.core.watch_user(user)

        if UserStatus.OFFLINE in (self.core.user_status, self.core.user_statuses.get(user)):
            # Either we are offline or the user we want to upload to is
            transfer.status = "User logged off"

            if not self.auto_clear_upload(transfer):
                self.update_upload(transfer)
            return

        if not locally_queued:
            self.token = increment_token(self.token)
            transfer.token = self.token
            transfer.status = "Getting status"
            self.transfer_request_times[transfer] = time.time()
            self.active_uploads.add(transfer)

            log.add_transfer("Requesting to upload file %(filename)s with token %(token)s to user %(user)s", {
                "filename": filename,
                "token": transfer.token,
                "user": user
            })

            self.core.send_message_to_peer(
                user, slskmessages.TransferRequest(
                    direction=TransferDirection.UPLOAD, token=transfer.token, file=filename, filesize=size,
                    realfile=real_path))

        self.update_upload(transfer)

    def append_upload(self, user, filename, transferobj):

        previously_queued = False
        old_index = 0

        if self.is_privileged(user):
            transferobj.modifier = "privileged" if user in self.privileged_users else "prioritized"

        for upload in self.uploads:
            if upload.filename == filename and upload.user == user:
                if upload.status == "Queued":
                    # This upload was queued previously
                    # Use the previous queue position
                    transferobj.queue_position = upload.queue_position
                    previously_queued = True

                if upload.status != "Finished":
                    transferobj.current_byte_offset = upload.current_byte_offset
                    transferobj.time_elapsed = upload.time_elapsed
                    transferobj.time_left = upload.time_left
                    transferobj.speed = upload.speed

                if upload in self.transfer_request_times:
                    del self.transfer_request_times[upload]

                self.clear_upload(upload)
                break

            old_index += 1

        if previously_queued:
            self.uploads.insert(old_index, transferobj)
            return

        self.uploads.appendleft(transferobj)

    def can_upload(self, user):

        transfers = config.sections["transfers"]

        if transfers["remotedownloads"]:

            if transfers["uploadallowed"] == 0:
                # No One can sent files to you
                return False

            if transfers["uploadallowed"] == 1:
                # Everyone can sent files to you
                return True

            if (transfers["uploadallowed"] == 2
                    and user in (x[0] for x in config.sections["server"]["userlist"])):
                # Users in userlist
                return True

            if transfers["uploadallowed"] == 3:
                # Trusted buddies
                for row in config.sections["server"]["userlist"]:
                    if row[0] == user and row[4]:
                        return True

        return False

    def get_folder_destination(self, user, folder, remove_prefix="", remove_destination=True):

        if not remove_prefix and '\\' in folder:
            remove_prefix = folder.rsplit('\\', 1)[0]

        # Get the last folders in folder path, excluding remove_prefix
        target_folders = folder.replace(remove_prefix, "").lstrip('\\').replace('\\', os.sep)

        # Check if a custom download location was specified
        if (user in self.requested_folders and folder in self.requested_folders[user]
                and self.requested_folders[user][folder]):
            download_location = self.requested_folders[user][folder]

            if remove_destination:
                del self.requested_folders[user][folder]
        else:
            download_location = self.get_default_download_folder(user)

        # Merge download path with target folder name
        return os.path.join(download_location, target_folders)

    def get_total_uploads_allowed(self):

        if config.sections["transfers"]["useupslots"]:
            maxupslots = config.sections["transfers"]["uploadslots"]

            if maxupslots <= 0:
                maxupslots = 1

            return maxupslots

        lstlen = sum(1 for upload in self.uploads if upload.sock is not None)

        if self.allow_new_uploads():
            return lstlen + 1

        return lstlen or 1

    def get_upload_queue_size(self, username=None):

        if self.is_privileged(username):
            queue_size = 0

            for upload in self.uploads:
                if upload.status == "Queued" and self.is_privileged(upload.user):
                    queue_size += 1

            return queue_size

        return sum(1 for upload in self.uploads if upload.status == "Queued")

    def get_default_download_folder(self, user):

        downloaddir = config.sections["transfers"]["downloaddir"]

        # Check if username subfolders should be created for downloads
        if config.sections["transfers"]["usernamesubfolders"]:
            try:
                downloaddir = os.path.join(downloaddir, clean_file(user))
                downloaddir_encoded = encode_path(downloaddir)

                if not os.path.isdir(downloaddir_encoded):
                    os.makedirs(downloaddir_encoded)

            except Exception as error:
                log.add(_("Unable to save download to username subfolder, falling back "
                          "to default download folder. Error: %s") % error)

        return downloaddir

    def get_download_destination(self, user, virtual_path, target_path):
        """ Returns the download destination of a virtual file path """

        folder_path = target_path if target_path else self.get_default_download_folder(user)
        basename = clean_file(virtual_path.replace('/', '\\').split('\\')[-1])

        return folder_path, basename

    def get_existing_download_path(self, user, virtual_path, target_path, size, always_return=False):
        """ Returns the download path of a previous download, if available """

        folder, basename = self.get_download_destination(user, virtual_path, target_path)
        basename_root, extension = os.path.splitext(basename)
        download_path = os.path.join(folder, basename)
        counter = 1

        while os.path.isfile(encode_path(download_path)):
            if os.stat(encode_path(download_path)).st_size == size:
                # Found a previous download with a matching file size
                return download_path

            basename = basename_root + " (" + str(counter) + ")" + extension
            download_path = os.path.join(folder, basename)
            counter += 1

        if always_return:
            # Get a download path even if it doesn't exist anymore
            return download_path

        return None

    @staticmethod
    def get_incomplete_file_path(incomplete_folder, username, virtual_path):
        """ Returns the path to store a download while it's still transferring """

        from hashlib import md5
        md5sum = md5()
        md5sum.update((virtual_path + username).encode('utf-8'))
        prefix = "INCOMPLETE" + md5sum.hexdigest()

        # Ensure file name doesn't exceed 255 bytes in length
        base_name, extension = os.path.splitext(clean_file(virtual_path.replace('/', '\\').split('\\')[-1]))
        base_name_limit = 255 - len(prefix) - len(extension.encode('utf-8'))
        base_name = truncate_string_byte(base_name, base_name_limit)

        if base_name_limit < 0:
            extension = truncate_string_byte(extension, 255 - len(prefix))

        return os.path.join(incomplete_folder, prefix + base_name + extension)

    @staticmethod
    def get_renamed(name):
        """ When a transfer is finished, we remove INCOMPLETE~ or INCOMPLETE
        prefix from the file's name.

        Checks if a file with the same name already exists, and adds a number
        to the file name if that's the case. """

        filename, extension = os.path.splitext(name)
        counter = 1

        while os.path.exists(encode_path(name)):
            name = filename + " (" + str(counter) + ")" + extension
            counter += 1

        return name

    def file_downloaded_actions(self, user, filepath):

        if config.sections["notifications"]["notification_popup_file"]:
            self.core.notifications.new_text_notification(
                _("%(file)s downloaded from %(user)s") % {
                    'user': user,
                    'file': filepath.rsplit(os.sep, 1)[1]
                },
                title=_("File downloaded")
            )

        if config.sections["transfers"]["afterfinish"]:
            try:
                execute_command(config.sections["transfers"]["afterfinish"], filepath)
                log.add(_("Executed: %s"), config.sections["transfers"]["afterfinish"])

            except Exception:
                log.add(_("Trouble executing '%s'"), config.sections["transfers"]["afterfinish"])

    def folder_downloaded_actions(self, user, folderpath):

        # walk through downloads and break if any file in the same folder exists, else execute
        statuses = ("Finished", "Paused", "Filtered")

        for download in self.downloads:
            if download.path == folderpath and download.status not in statuses:
                return

        if not folderpath:
            return

        if config.sections["notifications"]["notification_popup_folder"]:
            self.core.notifications.new_text_notification(
                _("%(folder)s downloaded from %(user)s") % {
                    'user': user,
                    'folder': folderpath
                },
                title=_("Folder downloaded")
            )

        if config.sections["transfers"]["afterfolder"]:
            try:
                execute_command(config.sections["transfers"]["afterfolder"], folderpath)
                log.add(_("Executed on folder: %s"), config.sections["transfers"]["afterfolder"])

            except Exception:
                log.add(_("Trouble executing on folder: %s"), config.sections["transfers"]["afterfolder"])

    def download_folder_error(self, transfer, error):

        self.abort_download(transfer, abort_reason="Download folder error")
        self.core.notifications.new_text_notification(
            _("OS error: %s") % error, title=_("Download folder error"))

    def download_finished(self, transfer, file_handle=None):

        self.close_file(file_handle, transfer)
        self.active_downloads.discard(transfer)
        self.check_download_queue(previous_user=transfer.user)

        folder, basename = self.get_download_destination(transfer.user, transfer.filename, transfer.path)
        folder_encoded = encode_path(folder)
        newname = self.get_renamed(os.path.join(folder, basename))

        try:
            if not os.path.isdir(folder_encoded):
                os.makedirs(folder_encoded)

            import shutil
            shutil.move(file_handle.name, encode_path(newname))

        except OSError as error:
            log.add(
                _("Couldn't move '%(tempfile)s' to '%(file)s': %(error)s"), {
                    'tempfile': file_handle.name.decode("utf-8", "replace"),
                    'file': newname,
                    'error': error
                }
            )
            self.download_folder_error(transfer, error)
            return

        transfer.status = "Finished"
        transfer.current_byte_offset = transfer.size
        transfer.sock = None
        transfer.token = None

        self.core.statistics.append_stat_value("completed_downloads", 1)

        # Attempt to show notification and execute commands
        self.file_downloaded_actions(transfer.user, newname)
        self.folder_downloaded_actions(transfer.user, transfer.path)

        if self.downloadsview:
            # Main tab highlight (bright)
            self.downloadsview.new_transfer_notification(finished=True)

        # Attempt to autoclear this download, if configured
        if not self.auto_clear_download(transfer):
            self.update_download(transfer)

        self.core.pluginhandler.download_finished_notification(transfer.user, transfer.filename, newname)

        log.add_download(
            _("Download finished: user %(user)s, file %(file)s"), {
                'user': transfer.user,
                'file': transfer.filename
            }
        )

    def upload_finished(self, transfer, file_handle=None):

        self.close_file(file_handle, transfer)
        self.active_uploads.discard(transfer)

        transfer.status = "Finished"
        transfer.current_byte_offset = transfer.size
        transfer.sock = None
        transfer.token = None

        log.add_upload(
            _("Upload finished: user %(user)s, IP address %(ip)s, file %(file)s"), {
                'user': transfer.user,
                'ip': self.core.protothread.user_addresses.get(transfer.user),
                'file': transfer.filename
            }
        )

        self.core.statistics.append_stat_value("completed_uploads", 1)

        # Autoclear this upload
        if not self.auto_clear_upload(transfer):
            self.update_upload(transfer)

        real_path = self.core.shares.virtual2real(transfer.filename)
        self.core.pluginhandler.upload_finished_notification(transfer.user, transfer.filename, real_path)

        self.check_upload_queue()

    def auto_clear_download(self, download):

        if config.sections["transfers"]["autoclear_downloads"]:
            self.clear_download(download)
            return True

        return False

    def auto_clear_upload(self, upload):

        if config.sections["transfers"]["autoclear_uploads"]:
            self.update_user_counter(upload.user)
            self.clear_upload(upload)
            return True

        return False

    def update_download(self, transfer, update_parent=True):

        if self.downloadsview:
            self.downloadsview.update_model(transfer, update_parent=update_parent)

    def update_upload(self, transfer, update_parent=True):

        user = transfer.user
        status = transfer.status

        if self.uploadsview:
            self.uploadsview.update_model(transfer, update_parent=update_parent)

        if status == "Queued" and user in self.user_update_counters:
            # Don't update existing user counter for queued uploads
            # We don't want to push the user back in the queue if they enqueued new files
            return

        if status == "Transferring":
            # Avoid unnecessary updates while transferring
            return

        self.update_user_counter(user)

    def _check_transfer_timeouts(self):

        current_time = time.time()

        if self.transfer_request_times:
            for transfer, start_time in self.transfer_request_times.copy().items():
                # When our port is closed, certain clients can take up to ~30 seconds before they
                # initiate a 'F' connection, since they only send an indirect connection request after
                # attempting to connect to our port for a certain time period.
                # Known clients: Nicotine+ 2.2.0 - 3.2.0, 2 s; Soulseek NS, ~20 s; soulseeX, ~30 s.
                # To account for potential delays while initializing the connection, add 15 seconds
                # to the timeout value.

                if (current_time - start_time) >= 45:
                    self.network_callback([slskmessages.TransferTimeout(transfer)])

    def check_queue_upload_allowed(self, user, addr, filename, real_path, msg):

        # Is user allowed to download?
        ip_address, _port = addr
        checkuser, reason = self.core.network_filter.check_user(user, ip_address)

        if not checkuser:
            return False, reason

        if self.core.shares.rescanning:
            self.core.shares.pending_network_msgs.append(msg)
            return False, None

        # Is that file already in the queue?
        if self.file_is_upload_queued(user, filename):
            return False, "Queued"

        # Has user hit queue limit?
        enable_limits = True

        if config.sections["transfers"]["friendsnolimits"]:
            friend = user in (x[0] for x in config.sections["server"]["userlist"])

            if friend:
                enable_limits = False

        if enable_limits:
            limit_reached, reason = self.queue_limit_reached(user)

            if limit_reached:
                return False, reason

        # Do we actually share that file with the world?
        if (not self.core.shares.file_is_shared(user, filename, real_path)
                or not self.file_is_readable(filename, real_path)):
            return False, "File not shared."

        return True, None

    def check_download_queue(self, previous_user=None):

        if not config.sections["transfers"]["use_download_slots"]:
            return

        if not self.allow_new_downloads():
            return

        statuses = ["Locally Queued"]

        if previous_user:
            statuses += ["Queued"]

        user = previous_user
        found_queued = False

        for download in reversed(self.downloads):
            if download.status not in statuses:
                continue

            if user is None:
                user = download.user

            elif user != download.user:
                continue

            found_queued = True

            if download.status == "Locally Queued":
                self.get_file(user, download.filename, path=download.path, transfer=download)

        if previous_user and not found_queued:
            self.check_download_queue()

    def check_downloads(self, *_args):

        statuslist_failed = ("Connection timeout", "Local file error", "Remote file error")

        for download in reversed(self.downloads):
            if download.status in statuslist_failed:
                # Retry failed downloads every 3 minutes

                self.abort_download(download, abort_reason=None)
                self.get_file(download.user, download.filename, path=download.path, transfer=download)

            if download.status == "Queued":
                # Request queue position every 3 minutes

                self.core.send_message_to_peer(
                    download.user,
                    slskmessages.PlaceInQueueRequest(file=download.filename, legacy_client=download.legacy_attempt)
                )

    def get_upload_candidate(self):
        """ Retrieve a suitable queued transfer for uploading.
        Round Robin: Get the first queued item from the oldest user
        FIFO: Get the first queued item in the list """

        round_robin_queue = not config.sections["transfers"]["fifoqueue"]
        active_statuses = ("Getting status", "Transferring")
        privileged_queue = False

        first_queued_transfers = OrderedDict()
        queued_users = {}
        uploading_users = set()

        for upload in reversed(self.uploads):
            if upload.status == "Queued":
                user = upload.user

                if user not in first_queued_transfers and user not in uploading_users:
                    first_queued_transfers[user] = upload

                if user in queued_users:
                    continue

                privileged = self.is_privileged(user)
                queued_users[user] = privileged

            elif upload.status in active_statuses:
                # We're currently uploading a file to the user
                user = upload.user

                if user in uploading_users:
                    continue

                uploading_users.add(user)

                if user in first_queued_transfers:
                    del first_queued_transfers[user]

        oldest_time = None
        target_user = None

        for user, privileged in queued_users.items():
            if privileged and user not in uploading_users:
                privileged_queue = True
                break

        if not round_robin_queue:
            # skip the looping below (except the cleanup) and get the first
            # user of the highest priority we saw above
            for user in first_queued_transfers:
                if privileged_queue and not queued_users[user]:
                    continue

                target_user = user
                break

        for user, update_time in self.user_update_counters.copy().items():
            if user not in queued_users:
                del self.user_update_counters[user]
                continue

            if not round_robin_queue or user in uploading_users:
                continue

            if privileged_queue and not queued_users[user]:
                continue

            if not oldest_time:
                oldest_time = update_time + 1

            if update_time < oldest_time:
                target_user = user
                oldest_time = update_time

        if not target_user:
            return None

        return first_queued_transfers[target_user]

    def check_upload_queue(self, *_args):
        """ Find next file to upload """

        if not self.uploads:
            # No uploads exist
            return

        if not self.allow_new_uploads():
            return

        upload_candidate = self.get_upload_candidate()

        if upload_candidate is None:
            return

        user = upload_candidate.user

        log.add_transfer(
            "Checked upload queue, attempting to upload file %(file)s to user %(user)s", {
                'file': upload_candidate.filename,
                'user': user
            }
        )

        self.push_file(
            user=user, filename=upload_candidate.filename, size=upload_candidate.size, transfer=upload_candidate
        )

    def update_user_counter(self, user):
        """ Called when an upload associated with a user has changed. The user update counter
        is used by the Round Robin queue system to determine which user has waited the longest
        since their last download. """

        self.user_update_counter += 1
        self.user_update_counters[user] = self.user_update_counter

    def ban_users(self, users, ban_message=None):
        """ Ban a user, cancel all the user's uploads, send a 'Banned'
        message via the transfers, and clear the transfers from the
        uploads list. """

        if ban_message:
            banmsg = "Banned (%s)" % ban_message
        elif config.sections["transfers"]["usecustomban"]:
            banmsg = "Banned (%s)" % config.sections["transfers"]["customban"]
        else:
            banmsg = "Banned"

        for upload in self.uploads.copy():
            if upload.user not in users:
                continue

            self.clear_upload(upload, denied_message=banmsg)

        for user in users:
            self.core.network_filter.ban_user(user)

        self.check_upload_queue()

    def retry_download(self, transfer):

        if transfer.status in ("Transferring", "Finished"):
            return

        user = transfer.user

        self.abort_download(transfer, abort_reason=None)
        self.get_file(user, transfer.filename, path=transfer.path, transfer=transfer)

    def retry_downloads(self, downloads):
        for download in downloads:
            self.retry_download(download)

    def retry_download_limits(self, *_args):

        statuslist_limited = ("Too many files", "Too many megabytes")

        for download in reversed(self.downloads):
            if download.status in statuslist_limited or download.status.startswith("User limit of"):
                # Re-queue limited downloads every 12 minutes

                log.add_transfer("Re-queuing file %(filename)s from user %(user)s in download queue", {
                    "filename": download.filename,
                    "user": download.user
                })

                self.abort_download(download, abort_reason=None)
                self.get_file(download.user, download.filename, path=download.path, transfer=download)

    def retry_upload(self, transfer):

        active_statuses = ["Getting status", "Transferring"]

        if transfer.status in active_statuses + ["Finished"]:
            # Don't retry active or finished uploads
            return

        user = transfer.user

        for upload in self.uploads:
            if upload.user != user:
                continue

            if upload.status in active_statuses:
                # User already has an active upload, queue the retry attempt
                if transfer.status != "Queued":
                    transfer.status = "Queued"
                    self.update_upload(transfer)
                return

        self.push_file(user, transfer.filename, transfer.size, transfer.path, transfer=transfer)

    def retry_uploads(self, uploads):
        for upload in uploads:
            self.retry_upload(upload)

    def retry_failed_uploads(self, *_args):

        for upload in reversed(self.uploads):
            if upload.status == "Connection timeout":
                upload.status = "Queued"
                self.update_upload(upload)

    def abort_download(self, download, abort_reason="Paused", update_parent=True):

        log.add_transfer(("Aborting download, user \"%(user)s\", filename \"%(filename)s\", token \"%(token)s\", "
                          "status \"%(status)s\""), {
            "user": download.user,
            "filename": download.filename,
            "token": download.token,
            "status": download.status
        })

        download.legacy_attempt = False
        download.size_changed = False
        download.token = None
        download.queue_position = 0

        if download in self.transfer_request_times:
            del self.transfer_request_times[download]

        if download.sock is not None:
            self.queue.append(slskmessages.CloseConnection(download.sock))
            download.sock = None

        if download.file is not None:
            self.close_file(download.file, download)

            log.add_download(
                _("Download aborted, user %(user)s file %(file)s"), {
                    "user": download.user,
                    "file": download.filename
                }
            )

        if download in self.active_downloads:
            self.active_downloads.discard(download)
            self.check_download_queue(previous_user=download.user)

        if abort_reason:
            download.status = abort_reason

        if self.downloadsview:
            self.downloadsview.abort_transfer(download, abort_reason, update_parent)

    def abort_downloads(self, downloads, abort_reason="Paused"):

        for download in downloads:
            if download.status not in (abort_reason, "Finished"):
                self.abort_download(download, abort_reason=abort_reason, update_parent=False)

        if self.downloadsview:
            self.downloadsview.abort_transfers(downloads, abort_reason)

    def abort_upload(self, upload, denied_message=None, abort_reason="Aborted", update_parent=True):

        log.add_transfer(("Aborting upload, user \"%(user)s\", filename \"%(filename)s\", token \"%(token)s\", "
                          "status \"%(status)s\""), {
            "user": upload.user,
            "filename": upload.filename,
            "token": upload.token,
            "status": upload.status
        })

        upload.token = None
        upload.queue_position = 0

        if upload in self.transfer_request_times:
            del self.transfer_request_times[upload]

        if upload.sock is not None:
            self.queue.append(slskmessages.CloseConnection(upload.sock))
            upload.sock = None

        if upload.file is not None:
            self.close_file(upload.file, upload)

            log.add_upload(
                _("Upload aborted, user %(user)s file %(file)s"), {
                    "user": upload.user,
                    "file": upload.filename
                }
            )

        elif denied_message and upload.status == "Queued":
            self.core.send_message_to_peer(
                upload.user, slskmessages.UploadDenied(file=upload.filename, reason=denied_message))

        if upload in self.active_uploads:
            self.active_uploads.discard(upload)
            self.check_upload_queue()

        if abort_reason:
            upload.status = abort_reason

        if self.uploadsview:
            self.uploadsview.abort_transfer(upload, abort_reason, update_parent)

    def abort_uploads(self, uploads, denied_message=None, abort_reason="Aborted"):

        for upload in uploads:
            if upload.status not in (abort_reason, "Finished"):
                self.abort_upload(
                    upload, denied_message=denied_message, abort_reason=abort_reason, update_parent=False)

        if self.uploadsview:
            self.uploadsview.abort_transfers(uploads, abort_reason)

    def clear_download(self, download, update_parent=True):

        self.abort_download(download, abort_reason=None)
        self.downloads.remove(download)

        if self.downloadsview:
            self.downloadsview.clear_transfer(download, update_parent)

    def clear_downloads(self, downloads=None, statuses=None):

        if downloads is None:
            # Clear all downloads
            downloads = self.downloads

        for download in downloads.copy():
            if statuses and download.status not in statuses:
                continue

            self.clear_download(download, update_parent=False)

        if self.downloadsview:
            self.downloadsview.clear_transfers(downloads, statuses)

    def clear_upload(self, upload, denied_message=None, update_parent=True):

        self.abort_upload(upload, denied_message=denied_message, abort_reason=None)
        self.uploads.remove(upload)

        if self.uploadsview:
            self.uploadsview.clear_transfer(upload, update_parent)

    def clear_uploads(self, uploads=None, statuses=None):

        if uploads is None:
            # Clear all uploads
            uploads = self.uploads

        for upload in uploads.copy():
            if statuses and upload.status not in statuses:
                continue

            self.clear_upload(upload, update_parent=False)

        if self.uploadsview:
            self.uploadsview.clear_transfers(uploads, statuses)

    """ Filters """

    def update_download_filters(self):

        failed = {}
        outfilter = "(\\\\("
        download_filters = sorted(config.sections["transfers"]["downloadfilters"])
        # Get Filters from config file and check their escaped status
        # Test if they are valid regular expressions and save error messages

        for item in download_filters:
            dfilter, escaped = item
            if escaped:
                dfilter = re.escape(dfilter)
                dfilter = dfilter.replace("\\*", ".*")

            try:
                re.compile("(" + dfilter + ")")
                outfilter += dfilter

                if item is not download_filters[-1]:
                    outfilter += "|"

            except re.error as error:
                failed[dfilter] = error

        outfilter += ")$)"

        try:
            re.compile(outfilter)

        except re.error as error:
            # Strange that individual filters _and_ the composite filter both fail
            log.add(_("Error: Download Filter failed! Verify your filters. Reason: %s"), error)
            config.sections["transfers"]["downloadregexp"] = ""
            return

        config.sections["transfers"]["downloadregexp"] = outfilter

        # Send error messages for each failed filter to log window
        if not failed:
            return

        errors = ""

        for dfilter, error in failed.items():
            errors += "Filter: %s Error: %s " % (dfilter, error)

        log.add(_("Error: %(num)d Download filters failed! %(error)s "), {'num': len(failed), 'error': errors})

    """ Exit """

    def get_downloads(self):
        """ Get a list of downloads """
        return [
            [download.user, download.filename, download.path, download.status, download.size,
             download.current_byte_offset, download.bitrate, download.length]
            for download in reversed(self.downloads)
        ]

    def get_uploads(self):
        """ Get a list of finished uploads """
        return [
            [upload.user, upload.filename, upload.path, upload.status, upload.size, upload.current_byte_offset,
             upload.bitrate, upload.length]
            for upload in reversed(self.uploads) if upload.status == "Finished"
        ]

    def save_downloads_callback(self, filename):
        json.dump(self.get_downloads(), filename, ensure_ascii=False)

    def save_uploads_callback(self, filename):
        json.dump(self.get_uploads(), filename, ensure_ascii=False)

    def save_transfers(self, *_args):
        """ Save list of transfers """

        if not self.allow_saving_transfers:
            # Don't save if transfers didn't load properly!
            return

        config.create_data_folder()

        for transfers_file, callback in (
            (self.downloads_file_name, self.save_downloads_callback),
            (self.uploads_file_name, self.save_uploads_callback)
        ):
            write_file_and_backup(transfers_file, callback)

    def server_disconnect(self):

        for timer_id in (self.transfer_timeout_timer_id, self.downloads_timer_id, self.upload_queue_timer_id,
                         self.retry_download_limits_timer_id, self.retry_failed_uploads_timer_id):
            scheduler.cancel(timer_id)

        need_update = False

        for download in self.downloads:
            if download.status not in ("Finished", "Filtered", "Paused"):
                download.status = "User logged off"
                self.abort_download(download, abort_reason=None)
                need_update = True

        if self.downloadsview and need_update:
            self.downloadsview.update_model()

        need_update = False

        for upload in self.uploads.copy():
            if upload.status != "Finished":
                need_update = True
                self.clear_upload(upload)

        if self.uploadsview and need_update:
            self.uploadsview.update_model()

        self.privileged_users.clear()
        self.requested_folders.clear()
        self.transfer_request_times.clear()
        self.user_update_counters.clear()

        if self.downloadsview:
            self.downloadsview.server_disconnect()

        if self.uploadsview:
            self.uploadsview.server_disconnect()

    def quit(self):
        self.save_transfers()
