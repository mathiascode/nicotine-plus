# Copyright (C) 2020 Nicotine+ Team
# Copyright (C) 2007 daelstorm. All rights reserved.
# Copyright (c) 2003-2004 Hyriand. All rights reserved.
#
# Based on code from PySoulSeek, original copyright note:
# Copyright (c) 2001-2003 Alexander Kanavin. All rights reserved.
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

"""
This module implements Soulseek networking protocol.
"""

import select
import selectors
import socket
import struct
import sys
import threading
import time
from collections import defaultdict
from errno import EINTR
from gettext import gettext as _

from pynicotine.logfacility import log
from pynicotine.slskmessages import AcceptChildren
from pynicotine.slskmessages import AckNotifyPrivileges
from pynicotine.slskmessages import AddThingIHate
from pynicotine.slskmessages import AddThingILike
from pynicotine.slskmessages import AddToPrivileged
from pynicotine.slskmessages import AddUser
from pynicotine.slskmessages import AdminMessage
from pynicotine.slskmessages import BranchLevel
from pynicotine.slskmessages import BranchRoot
from pynicotine.slskmessages import CantConnectToPeer
from pynicotine.slskmessages import ChangePassword
from pynicotine.slskmessages import CheckPrivileges
from pynicotine.slskmessages import ChildDepth
from pynicotine.slskmessages import ConnClose
from pynicotine.slskmessages import ConnectError
from pynicotine.slskmessages import ConnectToPeer
from pynicotine.slskmessages import DistribAlive
from pynicotine.slskmessages import DistribAliveInterval
from pynicotine.slskmessages import DistribBranchLevel
from pynicotine.slskmessages import DistribBranchRoot
from pynicotine.slskmessages import DistribChildDepth
from pynicotine.slskmessages import DistribSearch
from pynicotine.slskmessages import DistribServerSearch
from pynicotine.slskmessages import DownloadFile
from pynicotine.slskmessages import ExactFileSearch
from pynicotine.slskmessages import FileError
from pynicotine.slskmessages import FileRequest
from pynicotine.slskmessages import FileSearch
from pynicotine.slskmessages import FileSearchRequest
from pynicotine.slskmessages import FileSearchResult
from pynicotine.slskmessages import FolderContentsRequest
from pynicotine.slskmessages import FolderContentsResponse
from pynicotine.slskmessages import GetPeerAddress
from pynicotine.slskmessages import GetSharedFileList
from pynicotine.slskmessages import GetUserStats
from pynicotine.slskmessages import GetUserStatus
from pynicotine.slskmessages import GivePrivileges
from pynicotine.slskmessages import GlobalRecommendations
from pynicotine.slskmessages import GlobalUserList
from pynicotine.slskmessages import HaveNoParent
from pynicotine.slskmessages import IncConn
from pynicotine.slskmessages import IncPort
from pynicotine.slskmessages import InternalMessage
from pynicotine.slskmessages import ItemRecommendations
from pynicotine.slskmessages import ItemSimilarUsers
from pynicotine.slskmessages import JoinPublicRoom
from pynicotine.slskmessages import JoinRoom
from pynicotine.slskmessages import LeavePublicRoom
from pynicotine.slskmessages import LeaveRoom
from pynicotine.slskmessages import Login
from pynicotine.slskmessages import MessageAcked
from pynicotine.slskmessages import MessageUser
from pynicotine.slskmessages import MinParentsInCache
from pynicotine.slskmessages import PossibleParents
from pynicotine.slskmessages import NotifyPrivileges
from pynicotine.slskmessages import OutConn
from pynicotine.slskmessages import ParentInactivityTimeout
from pynicotine.slskmessages import ParentMinSpeed
from pynicotine.slskmessages import ParentSpeedRatio
from pynicotine.slskmessages import PeerInit
from pynicotine.slskmessages import PeerMessage
from pynicotine.slskmessages import PeerTransfer
from pynicotine.slskmessages import PierceFireWall
from pynicotine.slskmessages import PlaceholdUpload
from pynicotine.slskmessages import PlaceInLineResponse
from pynicotine.slskmessages import PlaceInQueue
from pynicotine.slskmessages import PlaceInQueueRequest
from pynicotine.slskmessages import PMessageUser
from pynicotine.slskmessages import PopupMessage
from pynicotine.slskmessages import PrivateRoomAdded
from pynicotine.slskmessages import PrivateRoomAddOperator
from pynicotine.slskmessages import PrivateRoomAddUser
from pynicotine.slskmessages import PrivateRoomDismember
from pynicotine.slskmessages import PrivateRoomDisown
from pynicotine.slskmessages import PrivateRoomOperatorAdded
from pynicotine.slskmessages import PrivateRoomOperatorRemoved
from pynicotine.slskmessages import PrivateRoomOwned
from pynicotine.slskmessages import PrivateRoomRemoved
from pynicotine.slskmessages import PrivateRoomRemoveOperator
from pynicotine.slskmessages import PrivateRoomRemoveUser
from pynicotine.slskmessages import PrivateRoomSomething
from pynicotine.slskmessages import PrivateRoomToggle
from pynicotine.slskmessages import PrivateRoomUsers
from pynicotine.slskmessages import PrivilegedUsers
from pynicotine.slskmessages import PublicRoomMessage
from pynicotine.slskmessages import QueuedDownloads
from pynicotine.slskmessages import QueueFailed
from pynicotine.slskmessages import QueueUpload
from pynicotine.slskmessages import Recommendations
from pynicotine.slskmessages import Relogged
from pynicotine.slskmessages import RemoveThingIHate
from pynicotine.slskmessages import RemoveThingILike
from pynicotine.slskmessages import RemoveUser
from pynicotine.slskmessages import RoomAdded
from pynicotine.slskmessages import RoomList
from pynicotine.slskmessages import RoomRemoved
from pynicotine.slskmessages import RoomSearch
from pynicotine.slskmessages import RoomTickerAdd
from pynicotine.slskmessages import RoomTickerRemove
from pynicotine.slskmessages import RoomTickerSet
from pynicotine.slskmessages import RoomTickerState
from pynicotine.slskmessages import SayChatroom
from pynicotine.slskmessages import SearchInactivityTimeout
from pynicotine.slskmessages import SearchParent
from pynicotine.slskmessages import SearchRequest
from pynicotine.slskmessages import SendSpeed
from pynicotine.slskmessages import SendUploadSpeed
from pynicotine.slskmessages import ServerConn
from pynicotine.slskmessages import ServerMessage
from pynicotine.slskmessages import ServerPing
from pynicotine.slskmessages import SetCurrentConnectionCount
from pynicotine.slskmessages import SetDownloadLimit
from pynicotine.slskmessages import SetGeoBlock
from pynicotine.slskmessages import SetStatus
from pynicotine.slskmessages import SetUploadLimit
from pynicotine.slskmessages import SetWaitPort
from pynicotine.slskmessages import SharedFileList
from pynicotine.slskmessages import SharedFoldersFiles
from pynicotine.slskmessages import SimilarUsers
from pynicotine.slskmessages import TransferRequest
from pynicotine.slskmessages import TransferResponse
from pynicotine.slskmessages import TunneledMessage
from pynicotine.slskmessages import UnknownPeerMessage
from pynicotine.slskmessages import UploadFailed
from pynicotine.slskmessages import UploadFile
from pynicotine.slskmessages import UploadQueueNotification
from pynicotine.slskmessages import UserInfoReply
from pynicotine.slskmessages import UserInfoRequest
from pynicotine.slskmessages import UserInterests
from pynicotine.slskmessages import UserJoinedRoom
from pynicotine.slskmessages import UserLeftRoom
from pynicotine.slskmessages import UserPrivileged
from pynicotine.slskmessages import UserSearch
from pynicotine.slskmessages import WishlistInterval
from pynicotine.slskmessages import WishlistSearch


# Set our actual file limit to the OS's hard limit as a failsafe
# If this limit is set too close to our artificial MAXFILELIMIT
# limit, Nicotine+ will freak out due to too many open files
if sys.platform == "win32":
    from pynicotine.multiselect import multiselect
    import ctypes

    ctypes.cdll.msvcrt._setmaxstdio(8192)

    MAXFILELIMIT = 1024
else:
    import resource
    softlimit, hardlimit = resource.getrlimit(resource.RLIMIT_NOFILE)

    try:
        resource.setrlimit(resource.RLIMIT_NOFILE, (hardlimit, hardlimit))
    except Exception:
        pass

    # Set our artificial file limit to prevent freezing the GUI
    # The max is 1024, but can be lower if the hard limit is too low
    # TODO: investigate if we can improve the performance somehow
    # and bump this limit
    MAXFILELIMIT = min(max(int(hardlimit * 0.75), 50), 1024)


class Connection:
    """
    Holds data about a connection. conn is a socket object,
    addr is (ip, port) pair, ibuf and obuf are input and output msgBuffer,
    init is a PeerInit object (see slskmessages docstrings).
    """
    def __init__(self, conn=None, addr=None):
        self.conn = conn
        self.addr = addr
        self.ibuf = bytearray()
        self.obuf = bytearray()
        self.init = None
        self.lastreadlength = 100 * 1024


class ServerConnection(Connection):
    """
    Server socket
    """
    def __init__(self, conn=None, addr=None):
        Connection.__init__(self, conn, addr)
        self.lastping = time.time()


class PeerConnection(Connection):
    def __init__(self, conn=None, addr=None, init=None):
        Connection.__init__(self, conn, addr)
        self.filereq = None
        self.filedown = None
        self.fileupl = None
        self.filereadbytes = 0
        self.bytestoread = 0
        self.init = init
        self.piercefw = None
        self.lastactive = time.time()

        self.starttime = None  # Used for upload bandwidth management
        self.sentbytes2 = 0
        self.readbytes2 = 0


class PeerConnectionInProgress:
    """ As all p2p connect()s are non-blocking, this class is used to
    hold data about a connection that is not yet established. msgObj is
    a message to be sent after the connection has been established.
    """
    def __init__(self, conn=None, msgObj=None):
        self.conn = conn
        self.msgObj = msgObj
        self.lastactive = time.time()


class SlskProtoThread(threading.Thread):
    """ This is a networking thread that actually does all the communication.
    It sends data to the UI thread via a callback function and receives data
    via a Queue object.
    """

    """ Server and peers send each other small binary messages, that start
    with length and message code followed by the actual message data.
    These are the codes."""

    servercodes = {
        Login: 1,
        SetWaitPort: 2,
        GetPeerAddress: 3,
        AddUser: 5,
        RemoveUser: 6,
        GetUserStatus: 7,
        SayChatroom: 13,
        JoinRoom: 14,
        LeaveRoom: 15,
        UserJoinedRoom: 16,
        UserLeftRoom: 17,
        ConnectToPeer: 18,
        MessageUser: 22,
        MessageAcked: 23,
        FileSearch: 26,
        SetStatus: 28,
        ServerPing: 32,
        SendSpeed: 34,  # Depreciated
        SharedFoldersFiles: 35,
        GetUserStats: 36,
        QueuedDownloads: 40,  # Depreciated
        Relogged: 41,
        UserSearch: 42,
        AddThingILike: 51,
        RemoveThingILike: 52,
        Recommendations: 54,
        GlobalRecommendations: 56,
        UserInterests: 57,
        PlaceInLineResponse: 60,  # Depreciated
        RoomAdded: 62,  # Depreciated
        RoomRemoved: 63,  # Depreciated
        RoomList: 64,
        ExactFileSearch: 65,  # Depreciated
        AdminMessage: 66,
        GlobalUserList: 67,  # Depreciated
        TunneledMessage: 68,  # Depreciated
        PrivilegedUsers: 69,
        HaveNoParent: 71,
        SearchParent: 73,
        ParentMinSpeed: 83,  # Unused
        ParentSpeedRatio: 84,  # Unused
        ParentInactivityTimeout: 86,  # Depreciated
        SearchInactivityTimeout: 87,  # Depreciated
        MinParentsInCache: 88,  # Depreciated
        DistribAliveInterval: 90,  # Depreciated
        AddToPrivileged: 91,
        CheckPrivileges: 92,
        SearchRequest: 93,
        AcceptChildren: 100,
        PossibleParents: 102,
        WishlistSearch: 103,
        WishlistInterval: 104,
        SimilarUsers: 110,
        ItemRecommendations: 111,
        ItemSimilarUsers: 112,
        RoomTickerState: 113,
        RoomTickerAdd: 114,
        RoomTickerRemove: 115,
        RoomTickerSet: 116,
        AddThingIHate: 117,
        RemoveThingIHate: 118,
        RoomSearch: 120,
        SendUploadSpeed: 121,
        UserPrivileged: 122,
        GivePrivileges: 123,
        NotifyPrivileges: 124,
        AckNotifyPrivileges: 125,
        BranchLevel: 126,  # Unimplemented
        BranchRoot: 127,  # Unimplemented
        ChildDepth: 129,  # Unimplemented
        PrivateRoomUsers: 133,
        PrivateRoomAddUser: 134,
        PrivateRoomRemoveUser: 135,
        PrivateRoomDismember: 136,
        PrivateRoomDisown: 137,
        PrivateRoomSomething: 138,
        PrivateRoomAdded: 139,
        PrivateRoomRemoved: 140,
        PrivateRoomToggle: 141,
        ChangePassword: 142,
        PrivateRoomAddOperator: 143,
        PrivateRoomRemoveOperator: 144,
        PrivateRoomOperatorAdded: 145,
        PrivateRoomOperatorRemoved: 146,
        PrivateRoomOwned: 148,
        JoinPublicRoom: 150,
        LeavePublicRoom: 151,
        PublicRoomMessage: 152,
        CantConnectToPeer: 1001
    }

    peercodes = {
        GetSharedFileList: 4,
        SharedFileList: 5,
        FileSearchRequest: 8,
        FileSearchResult: 9,
        UserInfoRequest: 15,
        UserInfoReply: 16,
        PMessageUser: 22,
        FolderContentsRequest: 36,
        FolderContentsResponse: 37,
        TransferRequest: 40,
        TransferResponse: 41,
        PlaceholdUpload: 42,  # Depreciated
        QueueUpload: 43,
        PlaceInQueue: 44,
        UploadFailed: 46,
        QueueFailed: 50,
        PlaceInQueueRequest: 51,
        UploadQueueNotification: 52,
        UnknownPeerMessage: 12547
    }

    distribclasses = {
        0: DistribAlive,
        3: DistribSearch,
        4: DistribBranchLevel,  # Unimplemented
        5: DistribBranchRoot,  # Unimplemented
        7: DistribChildDepth,  # Unimplemented
        93: DistribServerSearch
    }

    IN_PROGRESS_STALE_AFTER = 30
    # The value of 30 was pulled out of thin air. When we let the OS handle this:
    # - Linux seems okay, stale in progress conns get killed after a minute or two
    # - With Windows, based on #473, it would seem these connections are never removed
    CONNECTION_MAX_IDLE = 60
    CONNCOUNT_UI_INTERVAL = 0.5

    def __init__(self, ui_callback, queue, bindip, port, config, eventprocessor):
        """ ui_callback is a UI callback function to be called with messages
        list as a parameter. queue is Queue object that holds messages from UI
        thread.
        """
        threading.Thread.__init__(self)

        self._ui_callback = ui_callback
        self._queue = queue
        self._want_abort = 0
        self._bindip = bindip
        self._config = config
        self._eventprocessor = eventprocessor

        self.serverclasses = {}
        for i in self.servercodes:
            self.serverclasses[self.servercodes[i]] = i

        self.peerclasses = {}
        for i in self.peercodes:
            self.peerclasses[self.peercodes[i]] = i

        self._p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._p.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self._conns = {}
        self._connsinprogress = {}
        self._uploadlimit = (self._calcLimitNone, 0)
        self._downloadlimit = (self._calcDownloadLimitByTotal, self._config.sections["transfers"]["downloadlimit"])
        self._limits = {}
        self._dlimits = {}

        self.last_conncount_ui_update = self.last_file_update = time.time()

        # GeoIP Config
        self._geoip = None
        # GeoIP Database
        self.geoip = self._eventprocessor.geoip

        portrange = (port, port) if port else config.sections["server"]["portrange"]
        listenport = None

        for listenport in range(int(portrange[0]), int(portrange[1]) + 1):
            try:
                self._p.bind((bindip or '', listenport))
            except socket.error:
                listenport = None
            else:
                self._p.listen(1)
                self._ui_callback([IncPort(listenport)])
                break

        if listenport is not None:
            self.setDaemon(True)
            self.start()
        else:
            short_message = _("Could not bind to a local port, aborting connection")
            long_message = _(
                "The range you specified for client connection ports was "
                "{}-{}, but none of these were usable. Increase and/or ".format(portrange[0], portrange[1]) +
                "move the range and restart Nicotine+."
            )
            if portrange[0] < 1024:
                long_message += "\n\n" + _(
                    "Note that part of your range lies below 1024, this is usually not allowed on"
                    " most operating systems with the exception of Windows."
                )
            self._ui_callback([PopupMessage(short_message, long_message)])

    def _isUpload(self, conn):
        return conn.__class__ is PeerConnection and conn.fileupl is not None

    def _isDownload(self, conn):
        return conn.__class__ is PeerConnection and conn.filedown is not None

    def _calcUploadSpeed(self, i):
        curtime = time.time()

        if i.starttime is None:
            i.starttime = curtime

        elapsed = curtime - i.starttime

        if elapsed == 0:
            return 0
        else:
            return i.sentbytes2 / elapsed

    def _calcDownloadSpeed(self, i):
        curtime = time.time()

        if i.starttime is None:
            i.starttime = curtime

        elapsed = curtime - i.starttime

        if elapsed == 0:
            return 0
        else:
            return i.readbytes2 / elapsed

    def _calcUploadLimitByTransfer(self, conns, i):
        max = self._uploadlimit[1] * 1024.0
        limit = max - self._calcUploadSpeed(i) + 1024

        if limit < 1024.0:
            return int(0)

        return int(limit)

    def _calcUploadLimitByTotal(self, conns, i):
        max = self._uploadlimit[1] * 1024.0
        bw = 0.0

        for j in conns.values():
            if self._isUpload(j):
                bw += self._calcUploadSpeed(j)

        limit = max - bw + 1024

        if limit < 1024.0:
            return int(0)

        return int(limit)

    def _calcDownloadLimitByTotal(self, conns, i):
        max = self._downloadlimit[1] * 1024.0
        bw = 0.0

        for j in conns:
            if self._isDownload(j):
                bw += self._calcDownloadSpeed(j)

        limit = max - bw + 1023

        if limit < 1024.0:
            return int(0)

        return int(limit)

    def _calcLimitNone(self, conns, i):
        return None

    # randomly selects a safe connection to kill and closes the socket--
    # Will not kill upload, download, or server connections
    def killOverflowConnection(self, conns):
        victim_conn = None

        for (k, v) in conns.items():
            if self._isUpload(v):
                continue

            if self._isDownload(v):
                continue

            if k is self._server_socket:
                continue

            victim_conn = k
            break

        if victim_conn is None:
            return False

        del conns[victim_conn]

        # if endpoint is not connected, will get an exception on sockets...
        try:
            pn = victim_conn.getpeername()
            print('Killing overflow connection ', pn)
            victim_conn.shutdown(socket.SHUT_RDWR)
            victim_conn.close()
        except Exception:
            return False

        return True

    def socketStillActive(self, conn):
        try:
            connection = self._conns[conn]
        except KeyError:
            return False

        return len(connection.obuf) > 0 or len(connection.ibuf) > 0

    def ipBlocked(self, address):
        if address is None:
            return True

        ips = self._config.sections["server"]["ipblocklist"]
        s_address = address.split(".")

        for ip in ips:
            # No Wildcard in IP
            if "*" not in ip:
                if address == ip:
                    return True
                continue

            # Wildcard in IP
            parts = ip.split(".")
            seg = 0

            for part in parts:
                # Stop if there's no wildcard or matching string number
                if part != s_address[seg] and part != "*":
                    break

                seg += 1

                # Last time around
                if seg == 4:
                    # Wildcard blocked
                    return True

        # Not blocked
        return False

    def getIpPort(self, address):
        ip = port = None

        if type(address) is tuple:
            ip, port = address

        return ip, port

    def parseFileReq(self, conn, msgBuffer):
        msg = None

        # File Request messages are 4 bytes or greater in length
        if len(msgBuffer) >= 4:
            reqnum = struct.unpack("<i", msgBuffer[:4])[0]
            msg = FileRequest(conn.conn, reqnum)
            msgBuffer = msgBuffer[4:]

        return msg, msgBuffer

    def parseOffset(self, conn, msgBuffer):
        offset = None

        if len(msgBuffer) >= 8:
            offset = struct.unpack("<Q", msgBuffer[:8])[0]
            msgBuffer = msgBuffer[8:]

        return offset, msgBuffer

    def process_server_input(self, msgBuffer):
        """ Server has sent us something, this function retrieves messages
        from the msgBuffer, creates message objects and returns them and the rest
        of the msgBuffer.
        """
        msgs = []

        # Server messages are 8 bytes or greater in length
        while len(msgBuffer) >= 8:
            msgsize, msgtype = struct.unpack("<ii", msgBuffer[:8])

            if msgsize + 4 > len(msgBuffer):
                break

            elif msgtype in self.serverclasses:
                msg = self.serverclasses[msgtype]()
                msg.parseNetworkMessage(msgBuffer[8:msgsize + 4])
                msgs.append(msg)

            else:
                msgs.append(_("Server message type %(type)i size %(size)i contents %(msgBuffer)s unknown") % {'type': msgtype, 'size': msgsize - 4, 'msgBuffer': msgBuffer[8:msgsize + 4].__repr__()})

            msgBuffer = msgBuffer[msgsize + 4:]

        return msgs, msgBuffer

    def process_file_input(self, conn, msgBuffer):
        """ We have a "F" connection (filetransfer), peer has sent us
        something, this function retrieves messages
        from the msgBuffer, creates message objects and returns them
        and the rest of the msgBuffer.
        """
        msgs = []

        if conn.filereq is None:
            filereq, msgBuffer = self.parseFileReq(conn, msgBuffer)

            if filereq is not None:
                msgs.append(filereq)
                conn.filereq = filereq

        elif conn.filedown is not None:
            leftbytes = conn.bytestoread - conn.filereadbytes
            addedbytes = msgBuffer[:leftbytes]

            if leftbytes > 0:
                try:
                    conn.filedown.file.write(addedbytes)
                except IOError as strerror:
                    self._ui_callback([FileError(conn, conn.filedown.file, strerror)])
                except ValueError:
                    pass

            addedbyteslen = len(addedbytes)

            if (leftbytes - addedbyteslen) == 0 or \
                    (time.time() - self.last_file_update) > 1:

                """ We save resources by not sending data back to the UI every time
                a part of a file is transferred """

                print("callback")
                self._ui_callback([DownloadFile(conn.conn, addedbyteslen, conn.filedown.file)])
                self.last_file_update = time.time()

            conn.filereadbytes += addedbyteslen
            msgBuffer = msgBuffer[leftbytes:]

        elif conn.fileupl is not None:
            if conn.fileupl.offset is None:
                offset, msgBuffer = self.parseOffset(conn, msgBuffer)

                if offset is not None:
                    try:
                        conn.fileupl.file.seek(offset)
                    except IOError as strerror:
                        self._ui_callback([FileError(conn, conn.fileupl.file, strerror)])
                    except ValueError:
                        pass

                    conn.fileupl.offset = offset
                    self._ui_callback([conn.fileupl])

        conn.ibuf = msgBuffer
        return msgs, conn

    def process_peer_input(self, conn, msgBuffer):
        """ We have a "P" connection (p2p exchange), peer has sent us
        something, this function retrieves messages
        from the msgBuffer, creates message objects and returns them
        and the rest of the msgBuffer.
        """
        msgs = []

        while (conn.init is None or conn.init.type not in ['F', 'D']) and len(msgBuffer) >= 8:
            msgsize = struct.unpack("<i", msgBuffer[:4])[0]

            if len(msgBuffer) >= 8:
                msgtype = struct.unpack("<i", msgBuffer[4:8])[0]
                self._ui_callback([PeerTransfer(conn, msgsize, len(msgBuffer) - 4, self.peerclasses.get(msgtype, None))])

            if msgsize + 4 > len(msgBuffer):
                break

            elif conn.init is None:
                # Unpack Peer Connections
                if msgBuffer[4] == 0:
                    msg = PierceFireWall(conn)

                    try:
                        msg.parseNetworkMessage(msgBuffer[5:msgsize + 4])
                    except Exception as error:
                        print(error)
                    else:
                        conn.piercefw = msg
                        msgs.append(msg)

                elif msgBuffer[4] == 1:
                    msg = PeerInit(conn)

                    try:
                        msg.parseNetworkMessage(msgBuffer[5:msgsize + 4])
                    except Exception as error:
                        print(error)
                    else:
                        conn.init = msg
                        msgs.append(msg)

                elif conn.piercefw is None:
                    msgs.append(_(
                        "Unknown peer init code: {}, message contents ".format(msgBuffer[4]) +
                        "{}".format(msgBuffer[5:msgsize + 4].__repr__())
                    ))

                    conn.conn.close()
                    self._ui_callback([ConnClose(conn.conn, conn.addr)])
                    conn.conn = None
                    break

                else:
                    break

            elif conn.init.type == 'P':
                # Unpack Peer Messages
                msgtype = struct.unpack("<i", msgBuffer[4:8])[0]

                if msgtype in self.peerclasses:
                    try:
                        msg = self.peerclasses[msgtype](conn)

                        # Parse Peer Message and handle exceptions
                        try:
                            msg.parseNetworkMessage(msgBuffer[8:msgsize + 4])

                        except Exception as error:
                            host = port = _("unknown")
                            msgname = str(self.peerclasses[msgtype]).split(".")[-1]
                            print("Error parsing %s:" % msgname, error)

                            import traceback
                            for line in traceback.format_tb(error.__traceback__):
                                print(line)

                            if "addr" in conn.__dict__:
                                if conn.addr is not None:
                                    host = conn.addr[0]
                                    port = conn.addr[1]
                            debugmessage = _("There was an error while unpacking Peer message type %(type)s size %(size)i contents %(msgBuffer)s from user: %(user)s, %(host)s:%(port)s") % {'type': msgname, 'size': msgsize - 4, 'msgBuffer': msgBuffer[8:msgsize + 4].__repr__(), 'user': conn.init.user, 'host': host, 'port': port}
                            msgs.append(debugmessage)

                            del msg

                        else:
                            msgs.append(msg)

                    except Exception as error:
                        debugmessage = "Error in message function:", error, msgtype, conn
                        msgs.append(debugmessage)

                else:
                    host = port = _("unknown")

                    if conn.init.conn is not None and conn.addr is not None:
                        host = conn.addr[0]
                        port = conn.addr[1]

                    # Unknown Peer Message
                    x = 0
                    newbuf = ""

                    # massive speedup in the status log with the newline
                    # wrapping is incredibly slow
                    for char in msgBuffer[8:msgsize + 4].__repr__():
                        if x % 80 == 0:
                            newbuf += "\n"
                        newbuf += char
                        x += 1

                    debugmessage = _("Peer message type %(type)s size %(size)i contents %(msgBuffer)s unknown, from user: %(user)s, %(host)s:%(port)s") % {'type': msgtype, 'size': msgsize - 4, 'msgBuffer': newbuf, 'user': conn.init.user, 'host': host, 'port': port}
                    msgs.append(debugmessage)

            else:
                # Unknown Message type
                msgs.append(_("Can't handle connection type %s") % (conn.init.type))

            if msgsize >= 0:
                msgBuffer = msgBuffer[msgsize + 4:]
            else:
                msgBuffer = bytearray()

        conn.ibuf = msgBuffer
        return msgs, conn

    def process_distrib_input(self, conn, msgBuffer):
        """ We have a distributed network connection, parent has sent us
        something, this function retrieves messages
        from the msgBuffer, creates message objects and returns them
        and the rest of the msgBuffer.
        """
        msgs = []

        while len(msgBuffer) >= 5:
            msgsize = struct.unpack("<i", msgBuffer[:4])[0]

            if msgsize + 4 > len(msgBuffer):
                break

            msgtype = msgBuffer[4]

            if msgtype in self.distribclasses:
                msg = self.distribclasses[msgtype](conn)
                msg.parseNetworkMessage(msgBuffer[5:msgsize + 4])
                msgs.append(msg)

            else:
                msgs.append(_("Distrib message type %(type)i size %(size)i contents %(msgBuffer)s unknown") % {'type': msgtype, 'size': msgsize - 1, 'msgBuffer': msgBuffer[5:msgsize + 4].__repr__()})
                conn.conn.close()
                self._ui_callback([ConnClose(conn.conn, conn.addr)])
                conn.conn = None
                break

            if msgsize >= 0:
                msgBuffer = msgBuffer[msgsize + 4:]
            else:
                msgBuffer = bytearray()

        conn.ibuf = msgBuffer
        return msgs, conn

    def _resetCounters(self, conns):
        curtime = time.time()

        for i in conns.values():
            if self._isUpload(i):
                i.starttime = curtime
                i.sentbytes2 = 0

            if self._isDownload(i):
                i.starttime = curtime
                i.sentbytes2 = 0

    def process_queue(self, queue, conns, connsinprogress, server_socket, maxsockets=MAXFILELIMIT):
        """ Processes messages sent by UI thread. server_socket is a server connection
        socket object, queue holds the messages, conns and connsinprogress
        are dictionaries holding Connection and PeerConnectionInProgress
        messages."""

        msgList = []
        needsleep = False
        numsockets = len(conns) + len(connsinprogress)

        while not queue.empty():
            msgList.append(queue.get())

        for msgObj in msgList:
            if issubclass(msgObj.__class__, ServerMessage):
                try:
                    msg = msgObj.makeNetworkMessage()

                    if server_socket in conns:
                        conns[server_socket].obuf.extend(struct.pack("<ii", len(msg) + 4, self.servercodes[msgObj.__class__]))
                        conns[server_socket].obuf.extend(msg)
                    else:
                        queue.put(msgObj)
                        needsleep = True

                except Exception as error:
                    print(_("Error packaging message: %(type)s %(msg_obj)s, %(error)s") % {'type': msgObj.__class__, 'msg_obj': vars(msgObj), 'error': str(error)})
                    self._ui_callback([_("Error packaging message: %(type)s %(msg_obj)s, %(error)s") % {'type': msgObj.__class__, 'msg_obj': vars(msgObj), 'error': str(error)}])

            elif issubclass(msgObj.__class__, PeerMessage):
                if msgObj.conn in conns:

                    # Pack Peer and File and Search Messages
                    if msgObj.__class__ is PierceFireWall:
                        conns[msgObj.conn].piercefw = msgObj

                        msg = msgObj.makeNetworkMessage()

                        conns[msgObj.conn].obuf.extend(struct.pack("<i", len(msg) + 1))
                        conns[msgObj.conn].obuf.extend(bytes([0]))
                        conns[msgObj.conn].obuf.extend(msg)

                    elif msgObj.__class__ is PeerInit:
                        conns[msgObj.conn].init = msgObj
                        msg = msgObj.makeNetworkMessage()

                        if conns[msgObj.conn].piercefw is None:
                            conns[msgObj.conn].obuf.extend(struct.pack("<i", len(msg) + 1))
                            conns[msgObj.conn].obuf.extend(bytes([1]))
                            conns[msgObj.conn].obuf.extend(msg)

                    elif msgObj.__class__ is FileRequest:
                        conns[msgObj.conn].filereq = msgObj

                        msg = msgObj.makeNetworkMessage()
                        conns[msgObj.conn].obuf.extend(msg)

                        self._ui_callback([msgObj])

                    else:
                        checkuser = 1

                        if msgObj.__class__ is FileSearchResult and msgObj.geoip and self.geoip and self._geoip:
                            cc = self.geoip.get_all(conns[msgObj.conn].addr[0]).country_short

                            if cc == "-" and self._geoip[0]:
                                checkuser = 0
                            elif cc != "-" and self._geoip[1][0].find(cc) >= 0:
                                checkuser = 0

                        if checkuser:
                            msg = msgObj.makeNetworkMessage()
                            conns[msgObj.conn].obuf.extend(struct.pack("<ii", len(msg) + 4, self.peercodes[msgObj.__class__]))
                            conns[msgObj.conn].obuf.extend(msg)

                else:
                    if msgObj.__class__ not in [PeerInit, PierceFireWall, FileSearchResult]:
                        message = _("Can't send the message over the closed connection: %(type)s %(msg_obj)s") % {'type': msgObj.__class__, 'msg_obj': vars(msgObj)}
                        log.add(message, 3)

            elif issubclass(msgObj.__class__, InternalMessage):
                if msgObj.__class__ is ServerConn:
                    if maxsockets == -1 or numsockets < maxsockets:
                        try:
                            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                            if self._bindip:
                                server_socket.bind((self._bindip, 0))

                            server_socket.setblocking(0)
                            server_socket.connect_ex(msgObj.addr)
                            server_socket.setblocking(1)

                            connsinprogress[server_socket] = PeerConnectionInProgress(server_socket, msgObj)
                            numsockets += 1

                        except socket.error as err:
                            self._ui_callback([ConnectError(msgObj, err)])

                elif msgObj.__class__ is ConnClose and msgObj.conn in conns:
                    msgObj.conn.close()
                    self._ui_callback([ConnClose(msgObj.conn, conns[msgObj.conn].addr)])
                    del conns[msgObj.conn]

                elif msgObj.__class__ is OutConn:
                    if msgObj.addr[1] == 0:
                        self._ui_callback([ConnectError(msgObj, (0, "Port cannot be zero"))])

                    elif maxsockets == -1 or numsockets < maxsockets:
                        try:
                            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                            if self._bindip:
                                conn.bind((self._bindip, 0))

                            conn.setblocking(0)
                            conn.connect_ex(msgObj.addr)
                            conn.setblocking(1)

                            connsinprogress[conn] = PeerConnectionInProgress(conn, msgObj)
                            numsockets += 1

                        except socket.error as err:
                            self._ui_callback([ConnectError(msgObj, err)])

                elif msgObj.__class__ is DownloadFile and msgObj.conn in conns:
                    conns[msgObj.conn].filedown = msgObj

                    conns[msgObj.conn].obuf.extend(struct.pack("<Q", msgObj.offset))
                    conns[msgObj.conn].obuf.extend(struct.pack("<i", 0))

                    conns[msgObj.conn].bytestoread = msgObj.filesize - msgObj.offset

                    self._ui_callback([DownloadFile(msgObj.conn, 0, msgObj.file)])

                elif msgObj.__class__ is UploadFile and msgObj.conn in conns:
                    conns[msgObj.conn].fileupl = msgObj
                    self._resetCounters(conns)

                elif msgObj.__class__ is SetGeoBlock:
                    self._geoip = msgObj.config

                elif msgObj.__class__ is SetUploadLimit:
                    if msgObj.uselimit:
                        if msgObj.limitby:
                            cb = self._calcUploadLimitByTotal
                        else:
                            cb = self._calcUploadLimitByTransfer

                    else:
                        cb = self._calcLimitNone

                    self._resetCounters(conns)
                    self._uploadlimit = (cb, msgObj.limit)

                elif msgObj.__class__ is SetDownloadLimit:
                    self._downloadlimit = (self._calcDownloadLimitByTotal, msgObj.limit)

        if needsleep:
            time.sleep(1)

        return conns, connsinprogress, server_socket

    def writeData(self, server_socket, conns, i):
        if i in self._limits:
            limit = self._limits[i]
        else:
            limit = None

        conns[i].lastactive = time.time()
        i.setblocking(0)

        if limit is None:
            bytes_send = i.send(conns[i].obuf)
        else:
            bytes_send = i.send(conns[i].obuf[:limit])

        i.setblocking(1)
        conns[i].obuf = conns[i].obuf[bytes_send:]

        if i is not server_socket:
            if conns[i].fileupl is not None and conns[i].fileupl.offset is not None:
                conns[i].fileupl.sentbytes += bytes_send
                conns[i].sentbytes2 += bytes_send

                try:
                    if conns[i].fileupl.offset + conns[i].fileupl.sentbytes + len(conns[i].obuf) < conns[i].fileupl.size:
                        bytestoread = bytes_send * 2 - len(conns[i].obuf) + 10 * 1024
                        if bytestoread > 0:
                            read = conns[i].fileupl.file.read(bytestoread)
                            conns[i].obuf.extend(read)

                except IOError as strerror:
                    self._ui_callback([FileError(conns[i], conns[i].fileupl.file, strerror)])

                except ValueError:
                    pass

                if bytes_send > 0:
                    self._ui_callback([conns[i].fileupl])

    def readData(self, conns, i):
        # Check for a download limit
        if i in self._dlimits:
            limit = self._dlimits[i]
        else:
            limit = None

        conns[i].lastactive = time.time()

        if limit is None:
            # Unlimited download data
            data = i.recv(conns[i].lastreadlength)
            conns[i].ibuf.extend(data)

            if len(data) >= conns[i].lastreadlength // 2:
                conns[i].lastreadlength = conns[i].lastreadlength * 2

        else:
            # Speed Limited Download data (transfers)
            data = i.recv(conns[i].lastreadlength)
            conns[i].ibuf.extend(data)
            conns[i].lastreadlength = limit
            conns[i].readbytes2 += len(data)

        if not data:
            self._ui_callback([ConnClose(i, conns[i].addr)])
            i.close()
            del conns[i]

    def select(self, input_list, output_list, selector):
        # Select Networking Input and Output sockets
        timeout = 0.5

        try:
            if sys.platform == "win32":
                input, output, exc = multiselect(input_list, output_list, [], timeout)
            else:
                event_masks = defaultdict(int)

                for fileobj in input_list:
                    event_masks[fileobj] |= selectors.EVENT_READ
                for fileobj in output_list:
                    event_masks[fileobj] |= selectors.EVENT_WRITE

                for fileobj, event_masks in event_masks.items():
                    selector.register(fileobj, event_masks)

                key_events = selector.select(timeout)
                input = [key.fileobj for key, event in key_events if event & selectors.EVENT_READ]
                output = [key.fileobj for key, event in key_events if event & selectors.EVENT_WRITE]
        except Exception:
            # The selector chosen by the selectors module didn't work? Fall back to the select() syscall
            input, output, exc = select.select(input_list, output_list, [], timeout)

        return input, output

    def run(self):
        """ Actual networking loop is here."""

        # @var p Peer / Listen Port
        p = self._p

        # @var s Server Port
        self._server_socket = server_socket = None

        conns = self._conns
        connsinprogress = self._connsinprogress
        queue = self._queue

        while not self._want_abort:

            if not queue.empty():
                conns, connsinprogress, server_socket = self.process_queue(queue, conns, connsinprogress, server_socket)
                self._server_socket = server_socket

            outsock = []

            self._limits = {}
            self._dlimits = {}

            for i in conns:
                if len(conns[i].obuf) > 0 or (i is not server_socket and conns[i].fileupl is not None and conns[i].fileupl.offset is not None):
                    if self._isUpload(conns[i]):
                        limit = self._uploadlimit[0](conns, conns[i])

                        if limit is None or limit > 0:
                            self._limits[i] = limit
                            outsock.append(i)

                    else:
                        outsock.append(i)

            try:
                # Select Networking Input and Output sockets
                input_list = list(conns.keys()) + list(connsinprogress.keys()) + [p]
                output_list = list(connsinprogress.keys()) + outsock
                input, output = self.select(input_list, output_list, selectors.DefaultSelector())

            except OSError as error:
                if len(error.args) == 2 and error.args[0] == EINTR:
                    # Error recieved; but we don't care :)
                    continue

                # Error recieved; terminate networking loop
                print(time.strftime("%H:%M:%S"), "select OSError:", error)
                self._want_abort = 1

                message = _("Major Socket Error: Networking terminated! %s" % str(error))
                log.addwarning(message)

            except ValueError as error:
                # Possibly opened too many sockets
                print(time.strftime("%H:%M:%S"), "select ValueError:", error)

                if not self.killOverflowConnection(connsinprogress):
                    self.killOverflowConnection(conns)

                continue

            # Update UI connection count
            numsockets = len(conns) + len(connsinprogress)
            curtime = time.time()

            if (curtime - self.last_conncount_ui_update) > self.CONNCOUNT_UI_INTERVAL:
                # Avoid sending too many updates to the UI at once, if there are a lot of connections
                self._ui_callback([SetCurrentConnectionCount(numsockets)])
                self.last_conncount_ui_update = time.time()

            # Write Output
            for conn in conns:
                if conn in output:
                    try:
                        self.writeData(server_socket, conns, conn)
                    except socket.error as err:
                        self._ui_callback([ConnectError(conns[conn], err)])

            # Listen / Peer Port
            if p in input:
                try:
                    incconn, incaddr = p.accept()
                except Exception:
                    time.sleep(0.01)
                else:
                    ip, port = self.getIpPort(incaddr)

                    if self.ipBlocked(ip):
                        message = _("Ignoring connection request from blocked IP Address %(ip)s:%(port)s" % {
                            'ip': ip,
                            'port': port
                        })
                        log.add(message, 3)
                    else:
                        conns[incconn] = PeerConnection(conn=incconn, addr=incaddr)
                        self._ui_callback([IncConn(incconn, incaddr)])

            # Manage Connections
            curtime = time.time()

            for connection_in_progress in connsinprogress.copy():
                if (curtime - connsinprogress[connection_in_progress].lastactive) > self.IN_PROGRESS_STALE_AFTER:
                    connection_in_progress.close()
                    del connsinprogress[connection_in_progress]
                    continue

                try:
                    msgObj = connsinprogress[connection_in_progress].msgObj
                    if connection_in_progress in input:
                        connection_in_progress.recv(0)

                except socket.error as err:
                    self._ui_callback([ConnectError(msgObj, err)])
                    connection_in_progress.close()
                    del connsinprogress[connection_in_progress]

                else:
                    if connection_in_progress in output:
                        if connection_in_progress is server_socket:
                            conns[server_socket] = ServerConnection(conn=server_socket, addr=msgObj.addr)

                            self._ui_callback([ServerConn(server_socket, msgObj.addr)])

                        else:
                            ip, port = self.getIpPort(msgObj.addr)

                            if self.ipBlocked(ip):
                                message = "Blocking peer connection in progress to IP: %(ip)s Port: %(port)s" % {"ip": ip, "port": port}
                                log.add(message, 3)
                                connection_in_progress.close()
                            else:
                                conns[connection_in_progress] = PeerConnection(conn=connection_in_progress, addr=msgObj.addr, init=msgObj.init)
                                self._ui_callback([OutConn(connection_in_progress, msgObj.addr)])

                        del connsinprogress[connection_in_progress]

            # Process Data
            curtime = time.time()

            for connection in conns.copy():
                if connection is not server_socket:
                    if connection is not p:
                        # Timeout Connections

                        if curtime - conns[connection].lastactive > self.CONNECTION_MAX_IDLE:
                            self._ui_callback([ConnClose(connection, conns[connection].addr)])

                            connection.close()
                            del conns[connection]
                            continue

                    ip, port = self.getIpPort(conns[connection].addr)

                    if self.ipBlocked(ip):
                        message = "Blocking peer connection to IP: %(ip)s Port: %(port)s" % {"ip": ip, "port": port}
                        log.add(message, 3)
                        connection.close()
                        del conns[connection]
                        continue

                if connection is server_socket:
                    # ---------------------------
                    # Server Pings used to get us banned
                    # ---------------------------
                    # Was 30 seconds

                    if curtime - conns[server_socket].lastping > 120:
                        conns[server_socket].lastping = curtime
                        queue.put(ServerPing())

                if connection in input:
                    if self._isDownload(conns[connection]):
                        limit = self._downloadlimit[0](conns, connection)

                        if limit is None or limit > 0:
                            self._dlimits[connection] = limit

                    try:
                        self.readData(conns, connection)

                    except socket.error as err:
                        self._ui_callback([ConnectError(conns[connection], err)])

                try:
                    if len(conns[connection].ibuf) > 0:
                        if connection is server_socket:
                            msgs, conns[server_socket].ibuf = self.process_server_input(conns[server_socket].ibuf)
                            self._ui_callback(msgs)

                        else:
                            if conns[connection].init is None or conns[connection].init.type not in ['F', 'D']:
                                msgs, conns[connection] = self.process_peer_input(conns[connection], conns[connection].ibuf)
                                self._ui_callback(msgs)

                            if conns[connection].init is not None and conns[connection].init.type == 'F':
                                msgs, conns[connection] = self.process_file_input(conns[connection], conns[connection].ibuf)
                                self._ui_callback(msgs)

                            if conns[connection].init is not None and conns[connection].init.type == 'D':
                                msgs, conns[connection] = self.process_distrib_input(conns[connection], conns[connection].ibuf)
                                self._ui_callback(msgs)

                            if conns[connection].conn is None:
                                del conns[connection]
                except KeyError:
                    pass

        # Close Server Port
        if server_socket is not None:
            server_socket.close()

        # Networking thread aborted

    def abort(self):
        """ Call this to abort the thread """
        self._want_abort = 1
