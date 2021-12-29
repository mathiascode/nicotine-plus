# COPYRIGHT (C) 2020-2021 Nicotine+ Team
# COPYRIGHT (C) 2008-2012 Quinox <quinox@users.sf.net>
# COPYRIGHT (C) 2007-2009 Daelstorm <daelstorm@gmail.com>
# COPYRIGHT (C) 2003-2004 Hyriand <hyriand@thegraveyard.org>
# COPYRIGHT (C) 2001-2003 Alexander Kanavin
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

import selectors
import socket
import struct
import sys
import threading
import time

from collections import defaultdict

from pynicotine.logfacility import log
from pynicotine.slskmessages import AcceptChildren
from pynicotine.slskmessages import AckNotifyPrivileges
from pynicotine.slskmessages import AddThingIHate
from pynicotine.slskmessages import AddThingILike
from pynicotine.slskmessages import AddToPrivileged
from pynicotine.slskmessages import AddUser
from pynicotine.slskmessages import AdminCommand
from pynicotine.slskmessages import AdminMessage
from pynicotine.slskmessages import BranchLevel
from pynicotine.slskmessages import BranchRoot
from pynicotine.slskmessages import CantConnectToPeer
from pynicotine.slskmessages import CantCreateRoom
from pynicotine.slskmessages import ChangePassword
from pynicotine.slskmessages import CheckPrivileges
from pynicotine.slskmessages import ChildDepth
from pynicotine.slskmessages import ConnClose
from pynicotine.slskmessages import ConnCloseIP
from pynicotine.slskmessages import ConnectToPeer
from pynicotine.slskmessages import DistribAlive
from pynicotine.slskmessages import DistribAliveInterval
from pynicotine.slskmessages import DistribBranchLevel
from pynicotine.slskmessages import DistribBranchRoot
from pynicotine.slskmessages import DistribChildDepth
from pynicotine.slskmessages import DistribEmbeddedMessage
from pynicotine.slskmessages import DistribMessage
from pynicotine.slskmessages import DistribRequest
from pynicotine.slskmessages import DistribSearch
from pynicotine.slskmessages import DownloadFile
from pynicotine.slskmessages import EmbeddedMessage
from pynicotine.slskmessages import ExactFileSearch
from pynicotine.slskmessages import FileError
from pynicotine.slskmessages import FileMessage
from pynicotine.slskmessages import FileOffset
from pynicotine.slskmessages import FileRequest
from pynicotine.slskmessages import FileSearch
from pynicotine.slskmessages import FileSearchRoom
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
from pynicotine.slskmessages import InitPeerConn
from pynicotine.slskmessages import InitServerConn
from pynicotine.slskmessages import ItemRecommendations
from pynicotine.slskmessages import ItemSimilarUsers
from pynicotine.slskmessages import JoinPublicRoom
from pynicotine.slskmessages import JoinRoom
from pynicotine.slskmessages import LeavePublicRoom
from pynicotine.slskmessages import LeaveRoom
from pynicotine.slskmessages import Login
from pynicotine.slskmessages import MessageAcked
from pynicotine.slskmessages import MessageProgress
from pynicotine.slskmessages import MessageUser
from pynicotine.slskmessages import MessageUsers
from pynicotine.slskmessages import MinParentsInCache
from pynicotine.slskmessages import PossibleParents
from pynicotine.slskmessages import NotifyPrivileges
from pynicotine.slskmessages import ParentInactivityTimeout
from pynicotine.slskmessages import ParentMinSpeed
from pynicotine.slskmessages import ParentSpeedRatio
from pynicotine.slskmessages import PeerInit
from pynicotine.slskmessages import PeerInitMessage
from pynicotine.slskmessages import PeerMessage
from pynicotine.slskmessages import PierceFireWall
from pynicotine.slskmessages import PlaceholdUpload
from pynicotine.slskmessages import PlaceInLineResponse
from pynicotine.slskmessages import PlaceInQueue
from pynicotine.slskmessages import PlaceInQueueRequest
from pynicotine.slskmessages import PMessageUser
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
from pynicotine.slskmessages import UploadDenied
from pynicotine.slskmessages import QueueUpload
from pynicotine.slskmessages import Recommendations
from pynicotine.slskmessages import RelatedSearch
from pynicotine.slskmessages import Relogged
from pynicotine.slskmessages import RemoveThingIHate
from pynicotine.slskmessages import RemoveThingILike
from pynicotine.slskmessages import RemoveUser
from pynicotine.slskmessages import ResetDistributed
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
from pynicotine.slskmessages import SendConnectToken
from pynicotine.slskmessages import SendDownloadSpeed
from pynicotine.slskmessages import SendNetworkMessage
from pynicotine.slskmessages import SendUploadSpeed
from pynicotine.slskmessages import ServerMessage
from pynicotine.slskmessages import ServerPing
from pynicotine.slskmessages import ServerTimeout
from pynicotine.slskmessages import SetCurrentConnectionCount
from pynicotine.slskmessages import SetDownloadLimit
from pynicotine.slskmessages import SetStatus
from pynicotine.slskmessages import SetUploadLimit
from pynicotine.slskmessages import SetWaitPort
from pynicotine.slskmessages import SharedFileList
from pynicotine.slskmessages import SharedFoldersFiles
from pynicotine.slskmessages import ShowConnectionErrorMessage
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


""" Set the maximum number of open files to the hard limit reported by the OS.
Our MAXSOCKETS value needs to be lower than the file limit, otherwise our open
sockets in combination with other file activity can exceed the file limit,
effectively halting the program. """

if sys.platform == "win32":

    """ For Windows, FD_SETSIZE is set to 512 in the Python source.
    This limit is hardcoded, so we'll have to live with it for now. """

    MAXSOCKETS = 512
else:
    import resource  # pylint: disable=import-error

    if sys.platform == "darwin":

        """ Maximum number of files a process can open is 10240 on macOS.
        macOS reports INFINITE as hard limit, so we need this special case. """

        MAXFILELIMIT = 10240
    else:
        _SOFTLIMIT, MAXFILELIMIT = resource.getrlimit(resource.RLIMIT_NOFILE)

    try:
        resource.setrlimit(resource.RLIMIT_NOFILE, (MAXFILELIMIT, MAXFILELIMIT))

    except Exception as rlimit_error:
        log.add("Failed to set RLIMIT_NOFILE: %s", rlimit_error)

    """ Set the maximum number of open sockets to a lower value than the hard limit,
    otherwise we just waste resources.
    The maximum is 1024, but can be lower if the file limit is too low. """

    MAXSOCKETS = min(max(int(MAXFILELIMIT * 0.75), 50), 1024)

UINT_UNPACK = struct.Struct("<I").unpack
DOUBLE_UINT_UNPACK = struct.Struct("<II").unpack

UINT_PACK = struct.Struct("<I").pack


class Connection:
    """
    Holds data about a connection. conn is a socket object,
    addr is (ip, port) pair, ibuf and obuf are input and output msgBuffer,
    init is a PeerInit object (see slskmessages docstrings).
    """

    __slots__ = ("conn", "addr", "ibuf", "obuf", "events", "init", "lastactive", "lastreadlength")

    def __init__(self, conn=None, addr=None, events=None):
        self.conn = conn
        self.addr = addr
        self.events = events
        self.ibuf = bytearray()
        self.obuf = bytearray()
        self.init = None
        self.lastactive = time.time()
        self.lastreadlength = 100 * 1024


class PeerConnection(Connection):

    __slots__ = ("filereq", "filedown", "fileupl", "filereadbytes", "bytestoread", "piercefw", "lastcallback")

    def __init__(self, conn=None, addr=None, events=None, init=None):
        Connection.__init__(self, conn, addr, events)
        self.filereq = None
        self.filedown = None
        self.fileupl = None
        self.filereadbytes = 0
        self.bytestoread = 0
        self.init = init
        self.piercefw = None
        self.lastcallback = time.time()


class PeerConnectionInProgress:
    """ As all p2p connect()s are non-blocking, this class is used to
    hold data about a connection that is not yet established """

    __slots__ = ("conn", "addr", "lastactive", "init", "login")

    def __init__(self, conn=None, addr=None, init=None, login=None):
        self.conn = conn
        self.addr = addr
        self.init = init
        self.login = login
        self.lastactive = time.time()


class SlskProtoThread(threading.Thread):
    """ This is a networking thread that actually does all the communication.
    It sends data to the NicotineCore via a callback function and receives
    data via a deque object. """

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
        FileSearchRoom: 25,           # Obsolete
        FileSearch: 26,
        SetStatus: 28,
        ServerPing: 32,               # Deprecated
        SendConnectToken: 33,         # Obsolete
        SendDownloadSpeed: 34,        # Obsolete
        SharedFoldersFiles: 35,
        GetUserStats: 36,
        QueuedDownloads: 40,          # Obsolete
        Relogged: 41,
        UserSearch: 42,
        AddThingILike: 51,            # Deprecated
        RemoveThingILike: 52,         # Deprecated
        Recommendations: 54,          # Deprecated
        GlobalRecommendations: 56,    # Deprecated
        UserInterests: 57,            # Deprecated
        AdminCommand: 58,             # Obsolete
        PlaceInLineResponse: 60,      # Obsolete
        RoomAdded: 62,                # Obsolete
        RoomRemoved: 63,              # Obsolete
        RoomList: 64,
        ExactFileSearch: 65,          # Obsolete
        AdminMessage: 66,
        GlobalUserList: 67,           # Obsolete
        TunneledMessage: 68,          # Obsolete
        PrivilegedUsers: 69,
        HaveNoParent: 71,
        SearchParent: 73,             # Deprecated
        ParentMinSpeed: 83,
        ParentSpeedRatio: 84,
        ParentInactivityTimeout: 86,  # Obsolete
        SearchInactivityTimeout: 87,  # Obsolete
        MinParentsInCache: 88,        # Obsolete
        DistribAliveInterval: 90,     # Obsolete
        AddToPrivileged: 91,          # Obsolete
        CheckPrivileges: 92,
        EmbeddedMessage: 93,
        AcceptChildren: 100,
        PossibleParents: 102,
        WishlistSearch: 103,
        WishlistInterval: 104,
        SimilarUsers: 110,            # Deprecated
        ItemRecommendations: 111,     # Deprecated
        ItemSimilarUsers: 112,        # Deprecated
        RoomTickerState: 113,
        RoomTickerAdd: 114,
        RoomTickerRemove: 115,
        RoomTickerSet: 116,
        AddThingIHate: 117,           # Deprecated
        RemoveThingIHate: 118,        # Deprecated
        RoomSearch: 120,
        SendUploadSpeed: 121,
        UserPrivileged: 122,          # Deprecated
        GivePrivileges: 123,
        NotifyPrivileges: 124,        # Deprecated
        AckNotifyPrivileges: 125,     # Deprecated
        BranchLevel: 126,
        BranchRoot: 127,
        ChildDepth: 129,              # Deprecated
        ResetDistributed: 130,
        PrivateRoomUsers: 133,
        PrivateRoomAddUser: 134,
        PrivateRoomRemoveUser: 135,
        PrivateRoomDismember: 136,
        PrivateRoomDisown: 137,
        PrivateRoomSomething: 138,    # Obsolete
        PrivateRoomAdded: 139,
        PrivateRoomRemoved: 140,
        PrivateRoomToggle: 141,
        ChangePassword: 142,
        PrivateRoomAddOperator: 143,
        PrivateRoomRemoveOperator: 144,
        PrivateRoomOperatorAdded: 145,
        PrivateRoomOperatorRemoved: 146,
        PrivateRoomOwned: 148,
        MessageUsers: 149,
        JoinPublicRoom: 150,          # Deprecated
        LeavePublicRoom: 151,         # Deprecated
        PublicRoomMessage: 152,       # Deprecated
        RelatedSearch: 153,           # Obsolete
        CantConnectToPeer: 1001,
        CantCreateRoom: 1003
    }

    peerinitcodes = {
        PierceFireWall: 0,
        PeerInit: 1
    }

    peercodes = {
        GetSharedFileList: 4,
        SharedFileList: 5,
        FileSearchRequest: 8,         # Obsolete
        FileSearchResult: 9,
        UserInfoRequest: 15,
        UserInfoReply: 16,
        PMessageUser: 22,             # Deprecated
        FolderContentsRequest: 36,
        FolderContentsResponse: 37,
        TransferRequest: 40,
        TransferResponse: 41,
        PlaceholdUpload: 42,          # Obsolete
        QueueUpload: 43,
        PlaceInQueue: 44,
        UploadFailed: 46,
        UploadDenied: 50,
        PlaceInQueueRequest: 51,
        UploadQueueNotification: 52,  # Deprecated
        UnknownPeerMessage: 12547
    }

    distribcodes = {
        DistribAlive: 0,
        DistribSearch: 3,
        DistribBranchLevel: 4,
        DistribBranchRoot: 5,
        DistribChildDepth: 7,         # Deprecated
        DistribEmbeddedMessage: 93
    }

    IN_PROGRESS_STALE_AFTER = 2
    CONNECTION_MAX_IDLE = 60
    CONNCOUNT_CALLBACK_INTERVAL = 0.5

    def __init__(self, core_callback, queue, bindip, interface, port, port_range, network_filter, eventprocessor):
        """ core_callback is a NicotineCore callback function to be called with messages
        list as a parameter. queue is deque object that holds network messages from
        NicotineCore. """

        threading.Thread.__init__(self)

        self.name = "NetworkThread"

        if sys.platform not in ("linux", "darwin"):
            # TODO: support custom network interface for other systems than Linux and macOS
            interface = None

        self._core_callback = core_callback
        self._queue = queue
        self._callback_msgs = []
        self._init_msgs = {}
        self._out_msgs = defaultdict(list)
        self._want_abort = False
        self.server_disconnected = True
        self.bindip = bindip
        self.listenport = None
        self.portrange = (port, port) if port else port_range
        self.interface = interface
        self._network_filter = network_filter
        self._eventprocessor = eventprocessor

        self.serverclasses = {}
        for code_class, code_id in self.servercodes.items():
            self.serverclasses[code_id] = code_class

        self.peerinitclasses = {}
        for code_class, code_id in self.peerinitcodes.items():
            self.peerinitclasses[code_id] = code_class

        self.peerclasses = {}
        for code_class, code_id in self.peercodes.items():
            self.peerclasses[code_id] = code_class

        self.distribclasses = {}
        for code_class, code_id in self.distribcodes.items():
            self.distribclasses[code_id] = code_class

        # Select Networking Input and Output sockets
        self.selector = selectors.DefaultSelector()

        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.setblocking(0)

        self.server_socket = None
        self.server_address = None
        self.server_timer = None
        self.server_timeout_value = -1

        self._numsockets = 1

        self._conns = {}
        self._connsinprogress = {}
        self.user_addresses = {}
        self._token = 100
        self.exit = threading.Event()
        self.out_indirect_conn_request_times = {}

        self._calc_upload_limit_function = self._calc_upload_limit_none
        self._upload_limit = 0
        self._download_limit = 0
        self._upload_limit_split = 0
        self._download_limit_split = 0
        self._ulimits = {}
        self._dlimits = {}
        self.total_uploads = 0
        self.total_downloads = 0
        self.last_conncount_callback = time.time()
        self.last_cycle_time = time.time()
        self.current_cycle_loop_count = 0
        self.last_cycle_loop_count = 0
        self.loops_per_second = 0

        self.bind_listen_port()

        self.daemon = True
        self.start()

    """ General """

    def validate_listen_port(self):

        if self.listenport is not None:
            return True

        return False

    def validate_network_interface(self):

        try:
            if self.interface and self.interface not in (name for _i, name in socket.if_nameindex()):
                return False

        except AttributeError:
            pass

        return True

    @staticmethod
    def get_interface_ip_address(if_name):

        try:
            import fcntl
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            ip_if = fcntl.ioctl(sock.fileno(),
                                0x8915,  # SIOCGIFADDR
                                struct.pack('256s', if_name.encode()[:15]))

            ip_address = socket.inet_ntoa(ip_if[20:24])

        except ImportError:
            ip_address = None

        return ip_address

    def bind_to_network_interface(self, sock, if_name):

        try:
            if sys.platform == "linux":
                sock.setsockopt(socket.SOL_SOCKET, 25, if_name.encode())
                self.bindip = None
                return

            if sys.platform == "darwin":
                sock.setsockopt(socket.IPPROTO_IP, 25, socket.if_nametoindex(if_name))
                self.bindip = None
                return

        except PermissionError:
            pass

        # System does not support changing the network interface
        # Retrieve the IP address of the interface, and bind to it instead
        self.bindip = self.get_interface_ip_address(if_name)

    def bind_listen_port(self):

        if not self.validate_network_interface():
            return

        if self.interface and not self.bindip:
            self.bind_to_network_interface(self.listen_socket, self.interface)

        ip_address = self.bindip or ''

        for listenport in range(int(self.portrange[0]), int(self.portrange[1]) + 1):
            try:
                self.listen_socket.bind((ip_address, listenport))
                self.listen_socket.listen()
                self.listenport = listenport
                log.add(_("Listening on port: %i"), listenport)
                log.add_debug("Maximum number of concurrent connections (sockets): %i", MAXSOCKETS)
                break

            except socket.error as error:
                log.add_debug("Cannot listen on port %(port)s: %(error)s", {"port": listenport, "error": error})
                continue

    def server_connect(self):
        """ We've connected to the server """
        self.server_disconnected = False

        if self.server_timer is not None:
            self.server_timer.cancel()
            self.server_timer = None

    def server_disconnect(self):
        """ We've disconnected from the server, clean up """

        self.server_disconnected = True
        self.server_socket = None

        if self.server_timer is not None:
            self.server_timer.cancel()
            self.server_timer = None

        for connection in self._conns.copy():
            self.close_connection(self._conns, connection)

        for connection in self._connsinprogress.copy():
            self.close_connection(self._connsinprogress, connection)

        self._queue.clear()
        self._init_msgs.clear()
        self._out_msgs.clear()

        # Inform threads we've disconnected
        self.exit.set()

        self.out_indirect_conn_request_times.clear()

        if not self._want_abort:
            self._callback_msgs.append(SetCurrentConnectionCount(0))

    def abort(self):
        """ Call this to abort the thread """
        self._want_abort = True

        self.selector.close()
        self.server_disconnect()

    """ File Transfers """

    @staticmethod
    def _is_upload(conn):
        return conn.__class__ is PeerConnection and conn.fileupl is not None

    @staticmethod
    def _is_download(conn):
        return conn.__class__ is PeerConnection and conn.filedown is not None

    def _calc_upload_limit(self, limit_disabled=False, limit_per_transfer=False):

        limit = self._upload_limit
        loop_limit = 1024  # 1 KB/s is the minimum upload speed per transfer

        if limit_disabled or limit < loop_limit:
            self._upload_limit_split = 0
            return

        if not limit_per_transfer and self.total_uploads > 1:
            limit = limit // self.total_uploads

        self._upload_limit_split = int(limit)

    def _calc_upload_limit_by_transfer(self):
        return self._calc_upload_limit(limit_per_transfer=True)

    def _calc_upload_limit_none(self):
        return self._calc_upload_limit(limit_disabled=True)

    def _calc_download_limit(self):

        limit = self._download_limit
        loop_limit = 1024  # 1 KB/s is the minimum download speed per transfer

        if limit < loop_limit:
            # Download limit disabled
            self._download_limit_split = 0
            return

        if self.total_downloads > 1:
            limit = limit // self.total_downloads

        self._download_limit_split = int(limit)

    def _calc_loops_per_second(self):
        """ Calculate number of loops per second. This value is used to split the
        per-second transfer speed limit evenly for each loop. """

        current_time = time.time()

        if current_time - self.last_cycle_time >= 1:
            self.loops_per_second = (self.last_cycle_loop_count + self.current_cycle_loop_count) // 2

            self.last_cycle_loop_count = self.current_cycle_loop_count
            self.last_cycle_time = current_time
            self.current_cycle_loop_count = 0
        else:
            self.current_cycle_loop_count = self.current_cycle_loop_count + 1

    def set_conn_speed_limit(self, connection, limit, limits):

        limit = limit // (self.loops_per_second or 1)

        if limit > 0:
            limits[connection] = limit

    """ Connections """

    def _check_indirect_connection_timeouts(self):

        while True:
            curtime = time.time()

            if self.out_indirect_conn_request_times:
                for conn, request_time in list(self.out_indirect_conn_request_times.items()):
                    username = conn.init.target_user

                    if (curtime - request_time) >= 20:
                        log.add_conn(
                            "Indirect connect request of type %(type)s to user %(user)s expired, giving up", {
                                'type': conn.init.conn_type,
                                'user': username
                            }
                        )

                        self._callback_msgs.append(ShowConnectionErrorMessage(username, self._out_msgs[conn.init]))
                        self._init_msgs.pop(conn.init.token, None)
                        self._out_msgs.pop(conn.init, None)
                        del self.out_indirect_conn_request_times[conn]

            if self.exit.wait(1):
                # Event set, we're exiting
                return

    def server_timeout(self):
        self._core_callback([ServerTimeout()])

    def set_server_timer(self):

        if self.server_timeout_value == -1:
            self.server_timeout_value = 15

        elif 0 < self.server_timeout_value < 600:
            self.server_timeout_value = self.server_timeout_value * 2

        self.server_timer = threading.Timer(self.server_timeout_value, self.server_timeout)
        self.server_timer.name = "ServerTimer"
        self.server_timer.daemon = True
        self.server_timer.start()

        log.add(_("The server seems to be down or not responding, retrying in %i seconds"),
                self.server_timeout_value)

    def socket_still_active(self, conn):

        try:
            connection = self._conns[conn]

        except KeyError:
            return False

        return len(connection.obuf) > 0 or len(connection.ibuf) > 0

    @staticmethod
    def pack_network_message(msg_obj):

        try:
            return msg_obj.make_network_message()

        except Exception:
            from traceback import format_exc
            log.add(("Unable to pack message type %(msg_type)s. %(error)s"),
                    {'msg_type': msg_obj.__class__, 'error': format_exc()})

        return None

    @staticmethod
    def unpack_network_message(msg_class, msg_buffer, msg_size, conn_type, conn=None):

        try:
            if conn is not None:
                msg = msg_class(conn)
            else:
                msg = msg_class()

            msg.parse_network_message(msg_buffer)
            return msg

        except Exception as error:
            log.add(("Unable to parse %(conn_type)s message type %(msg_type)s size %(size)i "
                    "contents %(msg_buffer)s: %(error)s"),
                    {'conn_type': conn_type, 'msg_type': msg_class, 'size': msg_size,
                     'msg_buffer': msg_buffer, 'error': error})

        return None

    def modify_connection_events(self, conn_obj, events):

        if conn_obj.events != events:
            self.selector.modify(conn_obj.conn, events)
            conn_obj.events = events

    def process_conn_messages(self, conn):
        """ A connection is established with the peer, time to queue up our peer
        messages for delivery """

        username = conn.init.target_user

        msgs = self._out_msgs.get(conn.init)

        if msgs is None:
            return

        log.add_conn("List of outgoing messages for user %(user)s: %(messages)s", {
                     'user': username,
                     'messages': msgs})

        for j in msgs:
            j.conn = conn.conn
            self._queue.append(j)

        msgs.clear()

    def send_message_to_peer(self, user, message, login, address=None):
        """ Sends message to a peer. Used primarily when we know the username of a peer,
        but don't have an active connection. """

        conn = None

        if message.__class__ is not FileRequest:
            # Check if there's already a connection object for the specified username

            for _, i in self._conns.items():
                if i.init is not None and i.init.target_user == user and i.init.conn_type == 'P':
                    conn = i
                    log.add_conn("Found existing connection of type %(type)s for user %(user)s, using it.", {
                        'type': i.init.conn_type,
                        'user': user
                    })
                    break

        if conn is not None and conn.conn is not None:
            # We have initiated a connection previously, and it's ready

            self._out_msgs[conn.init].append(message)
            self.process_conn_messages(conn)

        elif conn is not None:
            # Connection exists but is not ready yet, add new messages to it

            self._out_msgs[conn.init].append(message)

        else:
            # This is a new peer, initiate a connection

            self.initiate_connection_to_peer(user, message, login, address)

        log.add_conn("Sending message of type %(type)s to user %(user)s", {
            'type': message.__class__,
            'user': user
        })

    def initiate_connection_to_peer(self, user, message, login, address=None):
        """ Prepare to initiate a connection with a peer """

        if message.__class__ is FileRequest:
            message_type = 'F'

        elif message.__class__ is DistribRequest:
            message_type = 'D'

        else:
            message_type = 'P'

        init = PeerInit(init_user=login, target_user=user, conn_type=message_type)
        addr = None

        if user == login:
            # Bypass public IP address request if we connect to ourselves
            addr = (self.bindip or '127.0.0.1', self.listenport)

        elif user in self.user_addresses:
            addr = self.user_addresses[user]

        elif address is not None:
            self.user_addresses[user] = addr = address

        if addr is None:
            self._init_msgs[user] = init
            self._queue.append(GetPeerAddress(user))

            log.add_conn("Requesting address for user %(user)s", {
                'user': user
            })

        else:
            self.connect_to_peer_direct(user, addr, init)

        self._out_msgs[init].append(message)

    def connect_to_peer_direct(self, user, addr, init):
        """ Initiate a connection with a peer directly """

        self._queue.append(InitPeerConn(addr, init))

        log.add_conn("Initialising direct connection of type %(type)s to user %(user)s", {
            'type': init.conn_type,
            'user': user
        })

    def connect_error(self, error, conn_obj):

        if conn_obj.login:
            log.add(
                _("Cannot connect to server %(host)s:%(port)s: %(error)s"), {
                    'host': conn_obj.addr[0],
                    'port': conn_obj.addr[1],
                    'error': error
                }
            )
            self.set_server_timer()
            return

        if not conn_obj.init.token:
            # We can't correct to peer directly, request indirect connection
            self.connect_to_peer_indirect(conn_obj, error)
            return

        if conn_obj in self.out_indirect_conn_request_times:
            return

        log.add_conn(
            "Can't respond to indirect connection request from user %(user)s. Error: %(error)s", {
                'user': conn_obj.init.target_user,
                'error': error
            })

    def connect_to_peer_indirect(self, conn, error):
        """ Send a message to the server to ask the peer to connect to us instead (indirect connection) """

        self._token += 1

        username = conn.init.target_user
        conn_type = conn.init.conn_type
        conn.init.token = self._token

        self._init_msgs[self._token] = conn.init
        self._queue.append(ConnectToPeer(self._token, username, conn_type))

        if conn in self.out_indirect_conn_request_times:
            del self.out_indirect_conn_request_times[conn]

        self.out_indirect_conn_request_times[conn] = time.time()

        log.add_conn(
            """Direct connection of type %(type)s to user %(user)s failed, attempting indirect connection.
Error: %(error)s""", {
                "type": conn_type,
                "user": username,
                "error": error
            }
        )

    def close_connection(self, connection_list, connection):

        if connection not in connection_list:
            # Already removed
            return

        conn_obj = connection_list[connection]

        if self._is_download(conn_obj):
            self.total_downloads -= 1
            self._calc_download_limit()

        elif self._is_upload(conn_obj):
            self.total_uploads -= 1
            self._calc_upload_limit_function()

        # If we're shutting down, we've already closed the selector in abort()
        if not self._want_abort:
            self.selector.unregister(connection)

        connection.close()
        del connection_list[connection]
        self._numsockets -= 1

        if connection is self.server_socket:
            # Disconnected from server, clean up connections and queue
            self.server_disconnect()

    def close_connection_by_ip(self, ip_address):

        for connection in self._conns.copy():
            conn_obj = self._conns.get(connection)

            if not conn_obj or connection is self.server_socket:
                continue

            addr = conn_obj.addr

            if ip_address == addr[0]:
                log.add_conn("Blocking peer connection to IP address %(ip)s:%(port)s", {
                    "ip": addr[0],
                    "port": addr[1]
                })
                self._callback_msgs.append(ConnClose(connection, addr))
                self.close_connection(self._conns, connection)

    """ Server Connection """

    @staticmethod
    def set_server_socket_keepalive(server_socket, idle=10, interval=4, count=10):
        """ Ensure we are disconnected from the server in case of connectivity issues,
        by sending TCP keepalive pings. Assuming default values are used, once we reach
        10 seconds of idle time, we start sending keepalive pings once every 4 seconds.
        If 10 failed pings have been sent in a row (40 seconds), the connection is presumed
        dead. """

        if hasattr(socket, 'SO_KEEPALIVE'):
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)  # pylint: disable=maybe-no-member

        if hasattr(socket, 'TCP_KEEPINTVL'):
            server_socket.setsockopt(socket.IPPROTO_TCP,
                                     socket.TCP_KEEPINTVL, interval)  # pylint: disable=maybe-no-member

        if hasattr(socket, 'TCP_KEEPCNT'):
            server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, count)  # pylint: disable=maybe-no-member

        if hasattr(socket, 'TCP_KEEPIDLE'):
            server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, idle)  # pylint: disable=maybe-no-member

        elif hasattr(socket, 'TCP_KEEPALIVE'):
            # macOS fallback

            server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPALIVE, idle)  # pylint: disable=maybe-no-member

        elif hasattr(socket, 'SIO_KEEPALIVE_VALS'):
            """ Windows fallback
            Probe count is set to 10 on a system level, and can't be modified.
            https://docs.microsoft.com/en-us/windows/win32/winsock/so-keepalive """

            server_socket.ioctl(
                socket.SIO_KEEPALIVE_VALS,  # pylint: disable=maybe-no-member
                (
                    1,
                    idle * 1000,
                    interval * 1000
                )
            )

    def init_server_conn(self, msg_obj):

        try:
            self.server_socket = server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn_obj = PeerConnectionInProgress(server_socket, msg_obj.addr, login=msg_obj.login)

            server_socket.setblocking(0)

            # Detect if our connection to the server is still alive
            self.set_server_socket_keepalive(server_socket)

            if self.bindip:
                server_socket.bind((self.bindip, 0))

            elif self.interface:
                self.bind_to_network_interface(server_socket, self.interface)

            server_socket.connect_ex(msg_obj.addr)

            self.selector.register(server_socket, selectors.EVENT_READ | selectors.EVENT_WRITE)
            self._connsinprogress[server_socket] = conn_obj
            self._numsockets += 1

        except socket.error as err:
            self.connect_error(err, conn_obj)
            server_socket.close()
            self.server_disconnect()

    def process_server_input(self, conn, msg_buffer):
        """ Server has sent us something, this function retrieves messages
        from the msg_buffer, creates message objects and returns them and the rest
        of the msg_buffer.
        """

        msg_buffer_mem = memoryview(msg_buffer)
        buffer_len = len(msg_buffer_mem)
        idx = 0

        # Server messages are 8 bytes or greater in length
        while buffer_len >= 8:
            msgsize, msgtype = DOUBLE_UINT_UNPACK(msg_buffer_mem[idx:idx + 8])
            msgsize_total = msgsize + 4

            if msgsize_total > buffer_len or msgsize < 0:
                # Invalid message size or buffer is being filled
                break

            # Unpack server messages
            if msgtype in self.serverclasses:
                msg = self.unpack_network_message(
                    self.serverclasses[msgtype], msg_buffer_mem[idx + 8:idx + msgsize_total], msgsize - 4, "server")

                if self.serverclasses[msgtype] is Login and msg.success:
                    # Check for indirect connection timeouts
                    self.exit.clear()

                    thread = threading.Thread(target=self._check_indirect_connection_timeouts)
                    thread.name = "IndirectConnectionTimeoutTimer"
                    thread.daemon = True
                    thread.start()

                if self.serverclasses[msgtype] is ConnectToPeer:
                    user = msg.user
                    addr = (msg.ip_address, msg.port)
                    conn_type = msg.conn_type
                    token = msg.token

                    init = PeerInit(init_user=user, target_user=user, conn_type=conn_type, token=token)
                    self.connect_to_peer_direct(user, addr, init)

                if self.serverclasses[msgtype] is GetUserStatus:
                    if msg.status <= 0:
                        # User went offline, reset stored IP address
                        if msg.user in self.user_addresses:
                            del self.user_addresses[msg.user]

                if self.serverclasses[msgtype] is GetPeerAddress:
                    init = self._init_msgs.pop(msg.user, None)

                    if msg.port == 0:
                        log.add_conn(
                            "Server reported port 0 for user %(user)s, giving up", {
                                'user': msg.user
                            }
                        )
                    else:
                        addr = (msg.ip_address, msg.port)

                        if init is not None:
                            # We now have the IP address for a user we previously didn't know,
                            # attempt a direct connection to the peer/user
                            self.connect_to_peer_direct(msg.user, addr, init)

                    self.user_addresses[msg.user] = (msg.ip_address, msg.port)

                if msg is not None:
                    self._callback_msgs.append(msg)

            else:
                log.add("Server message type %(type)i size %(size)i contents %(msg_buffer)s unknown",
                        {'type': msgtype, 'size': msgsize - 4, 'msg_buffer': msg_buffer[idx + 8:idx + msgsize_total]})

            idx += msgsize_total
            buffer_len -= msgsize_total

        conn.ibuf = msg_buffer[idx:]

    def process_server_output(self, msg_obj):

        if self.server_socket not in self._conns:
            log.add_conn("Can't send the message over the closed connection: %(type)s %(msg_obj)s", {
                'type': msg_obj.__class__,
                'msg_obj': vars(msg_obj)
            })
            return

        msg = self.pack_network_message(msg_obj)

        if msg is None:
            return

        conn_obj = self._conns[self.server_socket]
        conn_obj.obuf.extend(UINT_PACK(len(msg) + 4))
        conn_obj.obuf.extend(UINT_PACK(self.servercodes[msg_obj.__class__]))
        conn_obj.obuf.extend(msg)

        self.modify_connection_events(conn_obj, selectors.EVENT_READ | selectors.EVENT_WRITE)

    """ Peer Init """

    def process_peer_init_input(self, conn, msg_buffer):

        msg_buffer_mem = memoryview(msg_buffer)
        buffer_len = len(msg_buffer_mem)
        idx = 0

        # Peer init messages are 8 bytes or greater in length
        while buffer_len >= 8 and conn.init is None:
            msgsize = UINT_UNPACK(msg_buffer_mem[idx:idx + 4])[0]
            msgsize_total = msgsize + 4

            if msgsize_total > buffer_len or msgsize < 0:
                # Invalid message size or buffer is being filled
                break

            msgtype = msg_buffer_mem[idx + 4]

            # Unpack peer init messages
            if msgtype in self.peerinitclasses:
                msg = self.unpack_network_message(
                    self.peerinitclasses[msgtype], msg_buffer_mem[idx + 5:idx + msgsize_total], msgsize - 1,
                    "peer init", conn)

                if msg is not None:
                    if self.peerinitclasses[msgtype] is PierceFireWall:
                        conn.piercefw = msg

                        if conn in self.out_indirect_conn_request_times:
                            del self.out_indirect_conn_request_times[conn]

                        conn.init = self._init_msgs.pop(msg.token, None)
                        conn.init.conn = conn.conn
                        self._queue.append(conn.init)

                        self.process_conn_messages(conn)

                        log.add_conn("User %s managed to connect to us indirectly, connection is established.",
                                     conn.init.target_user)

                    elif self.peerinitclasses[msgtype] is PeerInit:
                        conn.init = msg

                        if conn in self.out_indirect_conn_request_times:
                            del self.out_indirect_conn_request_times[conn]

                        self.process_conn_messages(conn)

                        log.add_conn("Received incoming direct connection of type %(type)s from user %(user)s", {
                            'type': conn.init.conn_type,
                            'user': conn.init.target_user
                        })

                    self._callback_msgs.append(msg)

            else:
                if conn.piercefw is None:
                    log.add("Peer init message type %(type)i size %(size)i contents %(msg_buffer)s unknown",
                            {'type': msgtype, 'size': msgsize - 1,
                             'msg_buffer': msg_buffer[idx + 5:idx + msgsize_total]})

                    self._callback_msgs.append(ConnClose(conn))
                    self.close_connection(self._conns, conn)

                break

            idx += msgsize_total
            buffer_len -= msgsize_total

        conn.ibuf = msg_buffer[idx:]

    def process_peer_init_output(self, msg_obj):

        if msg_obj.conn not in self._conns:
            log.add_conn("Can't send the message over the closed connection: %(type)s %(msg_obj)s", {
                'type': msg_obj.__class__,
                'msg_obj': vars(msg_obj)
            })
            return

        # Pack peer init messages
        if msg_obj.__class__ is PierceFireWall:
            conn_obj = self._conns[msg_obj.conn]
            msg = self.pack_network_message(msg_obj)

            if msg is None:
                return

            conn_obj.piercefw = msg_obj

            conn_obj.obuf.extend(UINT_PACK(len(msg) + 1))
            conn_obj.obuf.extend(bytes([self.peerinitcodes[msg_obj.__class__]]))
            conn_obj.obuf.extend(msg)

        elif msg_obj.__class__ is PeerInit:
            conn_obj = self._conns[msg_obj.conn]
            msg = self.pack_network_message(msg_obj)

            if msg is None:
                return

            conn_obj.init = msg_obj

            if conn_obj.piercefw is not None:
                return

            conn_obj.obuf.extend(UINT_PACK(len(msg) + 1))
            conn_obj.obuf.extend(bytes([self.peerinitcodes[msg_obj.__class__]]))
            conn_obj.obuf.extend(msg)

        self.modify_connection_events(conn_obj, selectors.EVENT_READ | selectors.EVENT_WRITE)

    """ Peer Connection """

    def init_peer_conn(self, msg_obj):

        conn_obj = None

        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn_obj = PeerConnectionInProgress(conn, msg_obj.addr, msg_obj.init)

            conn.setblocking(0)

            if self.bindip:
                conn.bind((self.bindip, 0))

            elif self.interface:
                self.bind_to_network_interface(conn, self.interface)

            conn.connect_ex(msg_obj.addr)

            self.selector.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE)
            self._connsinprogress[conn] = conn_obj
            self._numsockets += 1

        except socket.error as err:
            self.connect_error(err, conn_obj)
            conn.close()

    def process_peer_input(self, conn, msg_buffer):
        """ We have a "P" connection (p2p exchange), peer has sent us
        something, this function retrieves messages
        from the msg_buffer, creates message objects and returns them
        and the rest of the msg_buffer.
        """

        msg_buffer_mem = memoryview(msg_buffer)
        buffer_len = len(msg_buffer_mem)
        idx = 0
        search_result_received = False

        # Peer messages are 8 bytes or greater in length
        while buffer_len >= 8:
            msgsize, msgtype = DOUBLE_UINT_UNPACK(msg_buffer_mem[idx:idx + 8])
            msgsize_total = msgsize + 4

            try:
                peer_class = self.peerclasses[msgtype]

                if peer_class in (SharedFileList, UserInfoReply):
                    # Send progress to the main thread
                    self._callback_msgs.append(
                        MessageProgress(conn.init.target_user, peer_class, buffer_len, msgsize_total))

            except KeyError:
                pass

            if msgsize_total > buffer_len or msgsize < 0:
                # Invalid message size or buffer is being filled
                break

            # Unpack peer messages
            if msgtype in self.peerclasses:
                msg = self.unpack_network_message(
                    self.peerclasses[msgtype], msg_buffer_mem[idx + 8:idx + msgsize_total], msgsize - 4, "peer", conn)

                if msg.__class__ is FileSearchResult:
                    search_result_received = True

                if msg is not None:
                    self._callback_msgs.append(msg)

            else:
                host = port = "unknown"

                if conn.init.conn is not None and conn.addr is not None:
                    host = conn.addr[0]
                    port = conn.addr[1]

                log.add(("Peer message type %(type)s size %(size)i contents %(msg_buffer)s unknown, "
                         "from user: %(user)s, %(host)s:%(port)s"),
                        {'type': msgtype, 'size': msgsize - 4, 'msg_buffer': msg_buffer[idx + 8:idx + msgsize_total],
                         'user': conn.init.target_user, 'host': host, 'port': port})

            idx += msgsize_total
            buffer_len -= msgsize_total

        conn.ibuf = msg_buffer[idx:]

        if search_result_received and not self.socket_still_active(conn.conn):
            # Forcibly close peer connection. Only used after receiving a search result,
            # as we need to get rid of peer connections before they pile up.

            self._callback_msgs.append(ConnClose(conn))
            self.close_connection(self._conns, conn.conn)

    def process_peer_output(self, msg_obj):

        if msg_obj.conn not in self._conns:
            log.add_conn("Can't send the message over the closed connection: %(type)s %(msg_obj)s", {
                'type': msg_obj.__class__,
                'msg_obj': vars(msg_obj)
            })
            return

        # Pack peer messages
        msg = self.pack_network_message(msg_obj)

        if msg is None:
            return

        conn_obj = self._conns[msg_obj.conn]
        conn_obj.obuf.extend(UINT_PACK(len(msg) + 4))
        conn_obj.obuf.extend(UINT_PACK(self.peercodes[msg_obj.__class__]))
        conn_obj.obuf.extend(msg)

        self.modify_connection_events(conn_obj, selectors.EVENT_READ | selectors.EVENT_WRITE)

    """ File Connection """

    def process_file_input(self, conn, msg_buffer):
        """ We have a "F" connection (filetransfer), peer has sent us
        something, this function retrieves messages
        from the msg_buffer, creates message objects and returns them
        and the rest of the msg_buffer.
        """

        if conn.filereq is None:
            msgsize = 4
            msg = self.unpack_network_message(FileRequest, msg_buffer[:msgsize], msgsize, "file", conn.conn)

            if msg is not None and msg.req is not None:
                self._callback_msgs.append(msg)
                conn.filereq = msg

            msg_buffer = msg_buffer[msgsize:]

        elif conn.filedown is not None:
            leftbytes = conn.bytestoread - conn.filereadbytes
            addedbytes = msg_buffer[:leftbytes]

            if leftbytes > 0:
                try:
                    conn.filedown.file.write(addedbytes)

                except IOError as strerror:
                    self._callback_msgs.append(FileError(conn, conn.filedown.file, strerror))
                    self._callback_msgs.append(ConnClose(conn))
                    self.close_connection(self._conns, conn.conn)

                except ValueError:
                    pass

            addedbyteslen = len(addedbytes)
            current_time = time.time()
            finished = ((leftbytes - addedbyteslen) == 0)

            if finished or (current_time - conn.lastcallback) > 1:
                # We save resources by not sending data back to the NicotineCore
                # every time a part of a file is downloaded

                self._callback_msgs.append(DownloadFile(conn.conn, conn.filedown.file))
                conn.lastcallback = current_time

            if finished:
                self._callback_msgs.append(ConnClose(conn))
                self.close_connection(self._conns, conn.conn)

            conn.filereadbytes += addedbyteslen
            msg_buffer = msg_buffer[leftbytes:]

        elif conn.fileupl is not None and conn.fileupl.offset is None:
            msgsize = 8
            msg = self.unpack_network_message(FileOffset, msg_buffer[:msgsize], msgsize, "file", conn)

            if msg is not None and msg.offset is not None:
                try:
                    conn.fileupl.file.seek(msg.offset)
                    self.modify_connection_events(conn, selectors.EVENT_READ | selectors.EVENT_WRITE)

                except IOError as strerror:
                    self._callback_msgs.append(FileError(conn, conn.fileupl.file, strerror))
                    self._callback_msgs.append(ConnClose(conn))
                    self.close_connection(self._conns, conn.conn)

                except ValueError:
                    pass

                conn.fileupl.offset = msg.offset
                self._callback_msgs.append(conn.fileupl)

            msg_buffer = msg_buffer[msgsize:]

        conn.ibuf = msg_buffer

    def process_file_output(self, msg_obj):

        if msg_obj.conn not in self._conns:
            log.add_conn("Can't send the message over the closed connection: %(type)s %(msg_obj)s", {
                'type': msg_obj.__class__,
                'msg_obj': vars(msg_obj)
            })
            return

        # Pack file messages
        if msg_obj.__class__ is FileRequest:
            msg = self.pack_network_message(msg_obj)

            if msg is None:
                return

            conn_obj = self._conns[msg_obj.conn]
            conn_obj.filereq = msg_obj
            conn_obj.obuf.extend(msg)

            self._callback_msgs.append(msg_obj)

        elif msg_obj.__class__ is FileOffset:
            msg = self.pack_network_message(msg_obj)

            if msg is None:
                return

            conn_obj = self._conns[msg_obj.conn]
            conn_obj.bytestoread = msg_obj.filesize - msg_obj.offset
            conn_obj.obuf.extend(msg)

        self.modify_connection_events(conn_obj, selectors.EVENT_READ | selectors.EVENT_WRITE)

    """ Distributed Connection """

    def process_distrib_input(self, conn, msg_buffer):
        """ We have a distributed network connection, parent has sent us
        something, this function retrieves messages
        from the msg_buffer, creates message objects and returns them
        and the rest of the msg_buffer.
        """

        msg_buffer_mem = memoryview(msg_buffer)
        buffer_len = len(msg_buffer_mem)
        idx = 0

        # Distributed messages are 5 bytes or greater in length
        while buffer_len >= 5:
            msgsize = UINT_UNPACK(msg_buffer_mem[idx:idx + 4])[0]
            msgsize_total = msgsize + 4

            if msgsize_total > buffer_len or msgsize < 0:
                # Invalid message size or buffer is being filled
                break

            msgtype = msg_buffer_mem[idx + 4]

            # Unpack distributed messages
            if msgtype in self.distribclasses:
                msg = self.unpack_network_message(
                    self.distribclasses[msgtype], msg_buffer_mem[idx + 5:idx + msgsize_total], msgsize - 1,
                    "distrib", conn)

                if msg is not None:
                    self._callback_msgs.append(msg)

            else:
                log.add("Distrib message type %(type)i size %(size)i contents %(msg_buffer)s unknown",
                        {'type': msgtype, 'size': msgsize - 1, 'msg_buffer': msg_buffer[idx + 5:idx + msgsize_total]})
                self._callback_msgs.append(ConnClose(conn))
                self.close_connection(self._conns, conn)
                break

            idx += msgsize_total
            buffer_len -= msgsize_total

        conn.ibuf = msg_buffer[idx:]

    def process_distrib_output(self, msg_obj):

        if msg_obj.conn not in self._conns:
            log.add_conn("Can't send the message over the closed connection: %(type)s %(msg_obj)s", {
                'type': msg_obj.__class__,
                'msg_obj': vars(msg_obj)
            })
            return

        # Pack distributed messages
        msg = self.pack_network_message(msg_obj)

        if msg is None:
            return

        conn_obj = self._conns[msg_obj.conn]
        conn_obj.obuf.extend(UINT_PACK(len(msg) + 1))
        conn_obj.obuf.extend(bytes([self.distribcodes[msg_obj.__class__]]))
        conn_obj.obuf.extend(msg)

        self.modify_connection_events(conn_obj, selectors.EVENT_READ | selectors.EVENT_WRITE)

    """ Connection I/O """

    def process_conn_input(self, connection, conn_obj):

        if connection is self.server_socket:
            self.process_server_input(conn_obj, conn_obj.ibuf)

        elif conn_obj.init is None:
            self.process_peer_init_input(conn_obj, conn_obj.ibuf)

        elif conn_obj.init is not None and conn_obj.init.conn_type == 'P':
            self.process_peer_input(conn_obj, conn_obj.ibuf)

        elif conn_obj.init is not None and conn_obj.init.conn_type == 'F':
            self.process_file_input(conn_obj, conn_obj.ibuf)

        elif conn_obj.init is not None and conn_obj.init.conn_type == 'D':
            self.process_distrib_input(conn_obj, conn_obj.ibuf)

        else:
            # Unknown message type
            log.add("Can't handle connection type %s", conn_obj.init.conn_type)

    def process_conn_output(self):
        """ Processes messages sent by the main thread. queue holds the messages,
        conns and connsinprogress are dictionaries holding Connection and
        PeerConnectionInProgress messages. """

        msg_list = self._queue.copy()
        self._queue.clear()

        for msg_obj in msg_list:
            if self.server_disconnected:
                # Disconnected from server, stop processing queue
                return

            msg_class = msg_obj.__class__

            if issubclass(msg_class, PeerInitMessage):
                self.process_peer_init_output(msg_obj)

            elif issubclass(msg_class, PeerMessage):
                self.process_peer_output(msg_obj)

            elif msg_class is InitPeerConn:
                if self._numsockets < MAXSOCKETS:
                    self.init_peer_conn(msg_obj)
                else:
                    # Connection limit reached, re-queue
                    self._queue.append(msg_obj)

            elif issubclass(msg_class, DistribMessage):
                self.process_distrib_output(msg_obj)

            elif issubclass(msg_class, FileMessage):
                self.process_file_output(msg_obj)

            elif issubclass(msg_class, ServerMessage):
                self.process_server_output(msg_obj)

            elif msg_class is ConnClose and msg_obj.conn in self._conns:
                conn = msg_obj.conn

                self._callback_msgs.append(ConnClose(self._conns[conn]))
                self.close_connection(self._conns, conn)

            elif msg_class is ConnCloseIP:
                self.close_connection_by_ip(msg_obj.addr)

            elif msg_class is InitServerConn:
                if self._numsockets < MAXSOCKETS:
                    self.init_server_conn(msg_obj)

            elif msg_class is DownloadFile and msg_obj.conn in self._conns:
                self._conns[msg_obj.conn].filedown = msg_obj
                self.total_downloads += 1
                self._calc_download_limit()

            elif msg_class is UploadFile and msg_obj.conn in self._conns:
                self._conns[msg_obj.conn].fileupl = msg_obj
                self.total_uploads += 1
                self._calc_upload_limit_function()

            elif msg_class is SetDownloadLimit:
                self._download_limit = msg_obj.limit * 1024
                self._calc_download_limit()

            elif msg_class is SetUploadLimit:
                if msg_obj.uselimit:
                    if msg_obj.limitby:
                        self._calc_upload_limit_function = self._calc_upload_limit
                    else:
                        self._calc_upload_limit_function = self._calc_upload_limit_by_transfer

                else:
                    self._calc_upload_limit_function = self._calc_upload_limit_none

                self._upload_limit = msg_obj.limit * 1024
                self._calc_upload_limit_function()

            elif msg_obj.__class__ is SendNetworkMessage:
                self.send_message_to_peer(msg_obj.user, msg_obj.message, msg_obj.login, msg_obj.addr)

    def read_data(self, conn_obj):

        connection = conn_obj.conn

        # Check for a download limit
        if connection in self._dlimits:
            limit = self._dlimits[connection]
        else:
            limit = None

        conn_obj.lastactive = time.time()
        data = connection.recv(conn_obj.lastreadlength)
        conn_obj.ibuf.extend(data)

        if limit is None:
            # Unlimited download data
            if len(data) >= conn_obj.lastreadlength // 2:
                conn_obj.lastreadlength = conn_obj.lastreadlength * 2

        else:
            # Speed Limited Download data (transfers)
            conn_obj.lastreadlength = limit

        if not data:
            return False

        return True

    def write_data(self, conn_obj):

        connection = conn_obj.conn

        if connection in self._ulimits:
            limit = self._ulimits[connection]
        else:
            limit = None

        conn_obj.lastactive = time.time()

        if conn_obj.obuf:
            if limit is None:
                bytes_send = connection.send(conn_obj.obuf)
            else:
                bytes_send = connection.send(conn_obj.obuf[:limit])

            conn_obj.obuf = conn_obj.obuf[bytes_send:]
        else:
            bytes_send = 0

        if connection is self.server_socket:
            return

        if conn_obj.fileupl is not None and conn_obj.fileupl.offset is not None:
            conn_obj.fileupl.sentbytes += bytes_send

            totalsentbytes = conn_obj.fileupl.offset + conn_obj.fileupl.sentbytes + len(conn_obj.obuf)

            try:
                size = conn_obj.fileupl.size

                if totalsentbytes < size:
                    bytestoread = bytes_send * 2 - len(conn_obj.obuf) + 10 * 4024

                    if bytestoread > 0:
                        read = conn_obj.fileupl.file.read(bytestoread)
                        conn_obj.obuf.extend(read)

                        self.modify_connection_events(conn_obj, selectors.EVENT_READ | selectors.EVENT_WRITE)

            except IOError as strerror:
                self._callback_msgs.append(FileError(conn_obj, conn_obj.fileupl.file, strerror))
                self._callback_msgs.append(ConnClose(conn_obj))
                self.close_connection(self._conns, connection)

            except ValueError:
                pass

            if bytes_send <= 0:
                return

            current_time = time.time()
            finished = (conn_obj.fileupl.offset + conn_obj.fileupl.sentbytes == size)

            if finished or (current_time - conn_obj.lastcallback) > 1:
                # We save resources by not sending data back to the NicotineCore
                # every time a part of a file is uploaded

                self._callback_msgs.append(conn_obj.fileupl)
                conn_obj.lastcallback = current_time

        if not conn_obj.obuf:
            # Nothing else to send, stop watching connection for writes
            self.modify_connection_events(conn_obj, selectors.EVENT_READ)

    """ Networking Loop """

    def run(self):

        # Listen socket needs to be registered for selection here instead of __init__,
        # otherwise connections break on certain systems (OpenBSD confirmed)
        self.selector.register(self.listen_socket, selectors.EVENT_READ)

        while not self._want_abort:

            if self.server_disconnected:
                # We're not connected to the server at the moment
                time.sleep(0.1)
                continue

            current_time = time.time()

            # Send updated connection count to NicotineCore. Avoid sending too many
            # updates at once, if there are a lot of connections.
            if (current_time - self.last_conncount_callback) > self.CONNCOUNT_CALLBACK_INTERVAL:
                self._callback_msgs.append(SetCurrentConnectionCount(self._numsockets))
                self.last_conncount_callback = current_time

            # Process outgoing messages
            if self._queue:
                self.process_conn_output()

            # Check which connections are ready to send/receive data
            try:
                key_events = self.selector.select(timeout=-1)
                input_list = set(key.fileobj for key, event in key_events if event & selectors.EVENT_READ)
                output_list = set(key.fileobj for key, event in key_events if event & selectors.EVENT_WRITE)

            except OSError as error:
                # Error recieved; terminate networking loop

                log.add("Major Socket Error: Networking terminated! %s", error)
                self._want_abort = True

            except ValueError as error:
                # Possibly opened too many sockets

                log.add("select ValueError: %s", error)
                time.sleep(0.1)

                self._callback_msgs.clear()
                continue

            # Manage incoming connections to listen socket
            if self._numsockets < MAXSOCKETS and not self.server_disconnected and self.listen_socket in input_list:
                try:
                    incconn, incaddr = self.listen_socket.accept()
                except Exception:
                    time.sleep(0.01)
                else:
                    if self._network_filter.is_ip_blocked(incaddr[0]):
                        log.add_conn("Ignoring connection request from blocked IP address %(ip)s:%(port)s", {
                            'ip': incaddr[0],
                            'port': incaddr[1]
                        })
                        incconn.close()

                    else:
                        events = selectors.EVENT_READ
                        incconn.setblocking(0)

                        self._conns[incconn] = PeerConnection(conn=incconn, addr=incaddr, events=events)
                        self._numsockets += 1
                        log.add_conn("Incoming connection")

                        # Event flags are modified to include 'write' in subsequent loops, if necessary.
                        # Don't do it here, otherwise connections may break.
                        self.selector.register(incconn, events)

            # Manage outgoing connections in progress
            for connection_in_progress in self._connsinprogress.copy():
                try:
                    conn_obj = self._connsinprogress[connection_in_progress]

                except KeyError:
                    # Connection was removed, possibly disconnecting from the server
                    continue

                if (current_time - conn_obj.lastactive) > self.IN_PROGRESS_STALE_AFTER:
                    # Connection failed

                    self.connect_error("Timed out", conn_obj)
                    self.close_connection(self._connsinprogress, connection_in_progress)
                    continue

                try:
                    if connection_in_progress in input_list:
                        # Check if the socket has any data for us
                        connection_in_progress.recv(1, socket.MSG_PEEK)

                except socket.error as err:
                    self.connect_error(err, conn_obj)
                    self.close_connection(self._connsinprogress, connection_in_progress)

                else:
                    if connection_in_progress in output_list:
                        # Connection has been established

                        addr = conn_obj.addr
                        events = selectors.EVENT_READ | selectors.EVENT_WRITE

                        if connection_in_progress is self.server_socket:
                            self._conns[self.server_socket] = Connection(
                                conn=self.server_socket, addr=addr, events=events)

                            log.add(
                                _("Connected to server %(host)s:%(port)s, logging in…"), {
                                    'host': addr[0],
                                    'port': addr[1]
                                }
                            )

                            self.server_address = addr
                            self.server_timeout_value = -1
                            login, password = conn_obj.login
                            conn_obj.login = True

                            self._queue.append(
                                Login(
                                    login, password,
                                    # Soulseek client version
                                    # NS and SoulseekQt use 157
                                    # We use a custom version number for Nicotine+
                                    160,

                                    # Soulseek client minor version
                                    # 17 stands for 157 ns 13c, 19 for 157 ns 13e
                                    # SoulseekQt seems to go higher than this
                                    # We use a custom minor version for Nicotine+
                                    1
                                )
                            )

                            if self.listenport is not None:
                                self._queue.append(SetWaitPort(self.listenport))
                        else:
                            if self._network_filter.is_ip_blocked(addr[0]):
                                log.add_conn("Ignoring connection request from blocked IP address %(ip)s:%(port)s", {
                                    "ip": addr[0],
                                    "port": addr[1]
                                })
                                self.close_connection(self._connsinprogress, connection_in_progress)
                                continue

                            self._conns[connection_in_progress] = conn_obj = PeerConnection(
                                conn=connection_in_progress, addr=addr, events=events, init=conn_obj.init)

                            if not conn_obj.init.token:
                                conn_obj.init.conn = connection_in_progress
                                self._queue.append(conn_obj.init)
                            else:
                                self._queue.append(PierceFireWall(conn_obj.conn, conn_obj.init.token))

                            log.add_conn("Connection established with user %s", conn_obj.init.target_user)
                            self.process_conn_messages(conn_obj)

                        del self._connsinprogress[connection_in_progress]

            # Process read/write for active connections
            for connection in self._conns.copy():
                try:
                    conn_obj = self._conns[connection]

                except KeyError:
                    # Connection was removed, possibly disconnecting from the server
                    continue

                if (connection is not self.server_socket
                        and (current_time - conn_obj.lastactive) > self.CONNECTION_MAX_IDLE):
                    # No recent activity, peer connection is stale

                    self._callback_msgs.append(ConnClose(conn_obj))
                    self.close_connection(self._conns, connection)
                    continue

                if connection in input_list:
                    if self._is_download(conn_obj):
                        self.set_conn_speed_limit(connection, self._download_limit_split, self._dlimits)

                    try:
                        if not self.read_data(conn_obj):
                            # No data received, socket was likely closed remotely
                            self._callback_msgs.append(ConnClose(conn_obj))
                            self.close_connection(self._conns, connection)
                            continue

                    except socket.error as err:
                        log.add_conn(("Cannot read data from connection %(addr)s, closing connection. "
                                      "Error: %(error)s"), {
                            "addr": conn_obj.addr,
                            "error": err
                        })
                        self._callback_msgs.append(ConnClose(conn_obj))
                        self.close_connection(self._conns, connection)
                        continue

                if conn_obj.ibuf:
                    self.process_conn_input(connection, conn_obj)

                if connection in output_list:
                    if self._is_upload(conn_obj):
                        self.set_conn_speed_limit(connection, self._upload_limit_split, self._ulimits)

                    try:
                        self.write_data(conn_obj)

                    except Exception as err:
                        log.add_conn("Cannot write data to connection %(addr)s, closing connection. Error: %(error)s", {
                            "addr": conn_obj.addr,
                            "error": err
                        })
                        self._callback_msgs.append(ConnClose(connection, conn_obj.addr))
                        self.close_connection(self._conns, connection)
                        continue

            # Inform the main thread
            if self._callback_msgs:
                self._core_callback(list(self._callback_msgs))
                self._callback_msgs.clear()

            # Reset transfer speed limits
            self._ulimits = {}
            self._dlimits = {}

            self._calc_loops_per_second()

            # Don't exhaust the CPU
            time.sleep(1 / 60)

        # Networking thread aborted
