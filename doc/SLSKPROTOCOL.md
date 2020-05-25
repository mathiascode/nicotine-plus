# The Soulseek Protocol

- [Packing](#packing)
- [Server Messages](#server-messages)
- [Peer Messages](#peer-messages)
- [Distributed Messages](#distributed-messages)
- [Museek Data Types](#museek-data-types)

## Packing

String

| Length of String | String |
| ---------------- | ------ |
| 4 Byte           | String |

Integer (unsigned)

| Number |
| ------ |
| 4 Byte |

Large Integer (64bits for file sizes)

| Number |
| ------ |
| 8 Byte |

Bool

| Character |
| --------- |
| 1 Byte    |

# Server Messages

| Send           | Receive             |
| -------------- | ------------------- |
| Send to Server | Receive from Server |

These messages are used by clients to interface with the server.
Internal Server messages are spooky and not understood, since the OSS
crowd doesn't have access to its source code. If you want a Soulseek
server, check out
[Soulfind](https://github.com/seeschloss/soulfind).
Soulfind is obviously not the exact same the official Soulseek server,
but it handles the protocol well enough (and can be modified).

In museekd 0.1.13, these messages are sent and received in
Museek/ServerConnection.cc and defined in Museek/ServerMessages.hh

In Nicotine, these messages are matched to their message number in
slskproto.py in the SlskProtoThread function, defined in slskmessages.py
and callbacks for the messages are set in pynicotine.py.

#### The Server Message format

| Message Length | Code    | Message Contents |
| -------------- | ------- | ---------------- |
| 4 Bytes        | 4 Bytes | ...              |

#### Message Index

| Code | Message                                           |
| ---- | ------------------------------------------------- |
| 1    | [Login](#server-code-1)                           |
| 2    | [Set Listen Port](#server-code-2)                 |
| 3    | [Get Peer Address](#server-code-3)                |
| 5    | [Add User](#server-code-5)                        |
| 6    | [Unknown](#server-code-6)                         |
| 7    | [Get Status](#server-code-7)                      |
| 13   | [Say in Chat Room](#server-code-13)               |
| 14   | [Join Room](#server-code-14)                      |
| 15   | [Leave Room](#server-code-15)                     |
| 16   | [User Joined Room](#server-code-16)               |
| 17   | [User Left Room](#server-code-17)                 |
| 18   | [Connect To Peer](#server-code-18)                |
| 22   | [Private Messages](#server-code-22)               |
| 23   | [Acknowledge Private Message](#server-code-23)    |
| 26   | [File Search](#server-code-26)                    |
| 28   | [Set Online Status](#server-code-28)              |
| 32   | [Ping](#server-code-32)                           |
| 34   | [Send Speed](#server-code-34)                     |
| 35   | [Shared Folders & Files](#server-code-35)         |
| 36   | [Get User Stats](#server-code-36)                 |
| 40   | [Queued Downloads](#server-code-40)               |
| 41   | [Kicked from Server](#server-code-41)             |
| 42   | [User Search](#server-code-42)                    |
| 51   | [Interest Add](#server-code-51)                   |
| 52   | [Interest Remove](#server-code-52)                |
| 54   | [Get Recommendations](#server-code-54)            |
| 56   | [Get Global Recommendations](#server-code-56)     |
| 57   | [Get User Interests](#server-code-57)             |
| 64   | [Room List](#server-code-64)                      |
| 65   | [Exact File Search](#server-code-65)              |
| 66   | [Global/Admin Message](#server-code-66)           |
| 69   | [Privileged Users](#server-code-69)               |
| 71   | [Have No Parents](#server-code-71)                |
| 73   | [Parent's IP](#server-code-73)                    |
| 83   | [ParentMinSpeed](#server-code-83)                 |
| 84   | [ParentSpeedRatio](#server-code-84)               |
| 86   | [Parent Inactivity Timeout](#server-code-86)      |
| 87   | [Search Inactivity Timeout](#server-code-87)      |
| 88   | [Minimum Parents In Cache](#server-code-88)       |
| 90   | [Distributed Alive Interval](#server-code-90)     |
| 91   | [Add Privileged User](#server-code-91)            |
| 92   | [Check Privileges](#server-code-92)               |
| 93   | [Search Request](#server-code-93)                 |
| 100  | [Accept Children](#server-code-100)               |
| 102  | [Net Info](#server-code-102)                      |
| 103  | [Wishlist Search](#server-code-103)               |
| 104  | [Wishlist Interval](#server-code-104)             |
| 110  | [Get Similar Users](#server-code-110)             |
| 111  | [Get Item Recommendations](#server-code-111)      |
| 112  | [Get Item Similar Users](#server-code-112)        |
| 113  | [Room Tickers](#server-code-113)                  |
| 114  | [Room Ticker Add](#server-code-114)               |
| 115  | [Room Ticker Remove](#server-code-115)            |
| 116  | [Set Room Ticker](#server-code-116)               |
| 117  | [Hated Interest Add](#server-code-117)            |
| 118  | [Hated Interest Remove](#server-code-118)         |
| 120  | [Room Search](#server-code-120)                   |
| 121  | [Send Upload Speed](#server-code-121)             |
| 122  | [User Privileges](#server-code-122)               |
| 123  | [Give Privileges](#server-code-123)               |
| 124  | [Notify Privileges](#server-code-124)             |
| 125  | [Acknowledge Notify Privileges](#server-code-125) |
| 126  | [Branch Level](#server-code-126)                  |
| 127  | [Branch Root](#server-code-127)                   |
| 129  | [Child Depth](#server-code-129)                   |
| 133  | [Private Room Users](#server-code-133)            |
| 134  | [Private Room Add User](#server-code-134)         |
| 135  | [Private Room Remove User](#server-code-135)      |
| 136  | [Private Room Drop Membership](#server-code-136)  |
| 137  | [Private Room Drop Ownership](#server-code-137)   |
| 138  | [Private Room Unknown](#server-code-138)          |
| 139  | [Private Room Added](#server-code-139)            |
| 140  | [Private Room Removed](#server-code-140)          |
| 141  | [Private Room Toggle](#server-code-141)           |
| 143  | [Private Room Add Operator](#server-code-143)     |
| 144  | [Private Room Remove Operator](#server-code-144)  |
| 145  | [Private Room Operator Added](#server-code-145)   |
| 146  | [Private Room Operator Removed](#server-code-146) |
| 148  | [Private Room Owned](#server-code-148)            |
| 1001 | [Cannot Connect](#server-code-1001)               |

### Server Code 1

**Login**

#### Function Names

Museekd: SLogin  
Nicotine: **Login**

#### Description

Send your username, password, and client version.

##### Sending Login Example

| Description | Message Length | Message Code | Username Length | Username                | Password Length | Password                |
| ----------- | -------------- | ------------ | --------------- | ----------------------- | --------------- | ----------------------- |
| Human       | 72             | 1            | 8               | username                | 8               | password                |
| Hex         | 48 00 00 00    | 01 00 00 00  | 08 00 00 00     | 75 73 65 72 6e 61 6d 65 | 08 00 00 00     | 70 61 73 73 77 6f 72 64 |

*Message, continued*

| Description | Version     | Length      | Hash                                                                                            | Number      |
| ----------- | ----------- | ----------- | ----------------------------------------------------------------------------------------------- | ----------- |
| Human       | 181         | 32          | d51c9a7e9353746a6020f9602d452929                                                                | 1           |
| Hex         | b5 00 00 00 | 20 00 00 00 | 64 35 31 63 39 61 37 65 39 33 35 33 37 34 36 61 36 30 32 30 66 39 36 30 32 64 34 35 32 39 32 39 | 01 00 00 00 |

*Message as a Hex Stream* **48 00 00 00 01 00 00 00 08 00 00 00 75 73 65
72 6e 61 6d 65 08 00 00 00 70 61 73 73 77 6f 72 64 b5 00 00 00 20 00 00
00 64 35 31 63 39 61 37 65 39 33 35 33 37 34 36 61 36 30 32 30 66 39 36
30 32 64 34 35 32 39 32 39 01 00 00 00**

#### Data Order

  - Send Login
    1.  **string** <ins>username</ins>
    2.  **string** <ins>password</ins> **A non-empty
        string is required**
    3.  **uint32** <ins>version number</ins> *182*
        for Museek+ *181* for Nicotine+
    4.  **string** <ins>MD5 hex digest of
        concatenated username & password</ins>
    5.  **uint32** <ins>1</ins> ??? No idea what
        exactly this is.
    6.  **string** <ins>Unknown string</ins> *In 157
        and up*

<!-- end list -->

  - Receive Login Success
    1.  **uchar** <ins>success</ins> 1
    2.  **string** <ins>greet</ins> A MOTD string
    3.  **uint32** <ins>Your IP Address</ins>
    4.  **string** <ins>MD5 hex digest of the
        password string</ins> *Windows Soulseek uses this hash to
        determine if it's connected to the official server*

<!-- end list -->

  - Receive Login Failure
    1.  **uchar** <ins>failure</ins> *0*
    2.  **string** <ins>reason</ins> Almost always:
        *Bad Password*; sometimes it's a banned message or another
        error.

### Server Code 2

**Set Listen Port**

#### Function Names

Museekd: SSetListenPort  
Nicotine: SetWaitPort

#### Description

The port you listen for connections on (2234 by default)

#### Data Order

  - Send
    1.  **uint32** <ins>port</ins>
  - Receive
      - *No Message*

### Server Code 3

**Get Peer Address**

#### Function Names

Museekd: SGetPeerAddress  
Nicotine: GetPeerAddress

#### Description

A server for a user's IP Address and port

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
  - Receive
    1.  **string** <ins>username</ins>
    2.  **ip** <ins>ip</ins>
    3.  **int** <ins>port</ins>

### Server Code 5

**Add User**

#### Function Names

Museekd: SAddUser  
Nicotine: AddUser

#### Description

Watch this user's status

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
  - Receive
    1.  **string** <ins>username</ins>
    2.  **char** <ins>exists</ins> *converted to
        Boolean*
    <!-- end list -->
      - If <ins>exists</ins> is 1/True (may not be
        implemented)
        1.  **int** <ins>status</ins> *0 == Offline,
            1 == Away; 2 == Online*
        2.  **int** <ins>avgspeed</ins>
        3.  **off\_t** <ins>downloadnum</ins>
        4.  **int** <ins>files</ins>
        5.  **int** <ins>dirs</ins>
        6.  **string** <ins>Country Code</ins> (may
            not be implemented)

### Server Code 6

**Unknown**

#### Function Names

Museekd: Not implemented  
Nicotine: **Not implemented**

#### Description

Something to do with user status. Usually sent just after SAddUser

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
  - Receive
      - *No Message*

### Server Code 7

**Get Status**

#### Function Names

Museekd: SGetStatus  
Nicotine: GetUserStatus

#### Description

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
  - Receive
    1.  **string** <ins>username</ins>
    2.  **int** <ins>status</ins> *0 == Offline, 1
        == Away; 2 == Online*

### Server Code 13

**Say in Chat Room**

#### Function Names

Museekd: SSayChatroom  
Nicotine: SayChatroom

#### Description

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
    2.  **string** <ins>message</ins>
  - Receive
    1.  **string** <ins>room</ins>
    2.  **string** <ins>username</ins>
    3.  **string** <ins>message</ins>

### Server Code 14

**Join a Room**

#### Function Names

Museekd: SJoinRoom  
Nicotine: JoinRoom

#### Description

#### Data Order

  - Send
    1.  **string** <ins>room</ins>

<!-- end list -->

  - Receive
    1.  **string** <ins>room</ins>
    2.  **int** <ins>number of users in room</ins>
    3.  Iterate the <ins>number of users</ins>
        **museekd uses a vector of strings**
        1.  **string** <ins>user</ins>
    4.  **int** <ins>number of userdata</ins>
    5.  Iterate the <ins>number of users</ins>
        **museekd uses a vector of userdata**
        1.  **int** <ins>status</ins>
    6.  **int** <ins>number of userdata</ins>
    7.  Iterate the userdata **vector of userdata** (and add unpacked
        data to [User Data](#user-data))
        1.  **int** <ins>avgspeed</ins>
        2.  **off\_t** <ins>downloadnum</ins>
        3.  **int** <ins>files</ins>
        4.  **int** <ins>dirs</ins>
    8.  **int** <ins>number of slotsfree</ins>
    9.  Iterate thru number of slotsfree
        1.  **int** <ins>slotsfree</ins>
    10. **int** <ins>number of usercountries</ins>
        (may not be implemented)
    11. Iterate thru number of usercountries
        1.  **string** <ins>countrycode</ins>
            **Uppercase country code**

ServerMessages.hh then Iterates thru
<ins>userdata</ins> and
<ins>users</ins> (For passing message to daemon)

  - Add data to [RoomData](#room-data)
    users\[**string** username \] = **data**

### Server Code 15

**Leave Room**

#### Function Names

Museekd: SLeaveRoom  
Nicotine: LeaveRoom

#### Description

#### Data Order

  - Send (leave room)
    1.  **string** <ins>room</ins>
  - Receive (left room)
    1.  **string** <ins>room</ins>

### Server Code 16

**A User Joined a Room**

#### Function Names

Museekd: SUserJoinedRoom  
Nicotine: UserJoinedRoom

#### Description

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>
    2.  **string** <ins>username</ins>
    3.  **int** <ins>status</ins>
    4.  **int** <ins>avgspeed</ins>
    5.  **off\_t** <ins>downloadnum</ins>
    6.  **int** <ins>files</ins>
    7.  **int** <ins>dirs</ins>
    8.  **int** <ins>slotsfree</ins>
    9.  **string** <ins>countrycode</ins>\_
        **Uppercase country code**

### Server Code 17

**A User Left a Room**

#### Function Names

Museekd: SUserLeftRoom  
Nicotine: UserLeftRoom

#### Description

A user (not you) left a room you are in.

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>
    2.  **string** <ins>username</ins>

### Server Code 18

**Connect To Peer**

#### Function Names

Museekd: SConnectToPeer  
Nicotine: ConnectToPeer

#### Description

A message you send to the server to notify a client that you want to
connect to it, after direct connection has failed. See also: [Peer
Connection Message
Order](#peer-connection-message-order)

#### Data Order

  - Send
    1.  **uint32** <ins>token</ins>
    2.  **string** <ins>username</ins>
    3.  **string** <ins>type</ins> *Connection Type
        (P, F or D)*
  - Receive
    1.  **string** <ins>username</ins>
    2.  **string** <ins>type</ins> *Connection Type
        (P, F or D)*
    3.  **ip** <ins>ip</ins>
    4.  **int** <ins>port</ins>
    5.  **uint32** <ins>token</ins> *Use this token
        for [Pierce Firewall](#peer-code-0)*

### Server Code 22

**Private Messages**

#### Function Names

Museekd: SPrivateMessage  
Nicotine: MessageUser

#### Description

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
    2.  **string** <ins>message</ins>
  - Receive
    1.  **int** <ins>ID</ins>
    2.  **int** <ins>timestamp</ins>
    3.  **string** <ins>username</ins>
    4.  **string** <ins>message</ins>

### Server Code 23

**Acknowledge Private Message**

#### Function Names

Museekd: SAckPrivateMessage  
Nicotine: MessageAcked

#### Description

Acknowledge that you received a Private message. If we do not send it,
the server will keep sending the chat phrase to us. (Museekd also Reset
timestamps to account for server-time bugginess)

#### Data Order

  - Send
    1.  **int** <ins>message ID</ins>
  - Receive
      - *No Message*

### Server Code 26

**File Search** Museekd: SFileSearch  
Nicotine: FileSearch

#### Description

The ticket is a random number generated by the client and used to track
the search results.

#### Data Order

  - Send
    1.  **int** <ins>ticket</ins>
    2.  **string** <ins>search query</ins>
  - Receive *search request from another user*
    1.  **string** <ins>username</ins>
    2.  **int** <ins>ticket</ins>
    3.  **string** <ins>search query</ins>

### Server Code 28

**Set Online Status**

#### Function Names

Museekd: SSetStatus  
Nicotine: SetStatus

#### Description

Status is a way to define whether you're available or busy. *1 = Away
and 2 = Online*

#### Data Order

  - Send
    1.  **int** <ins>status</ins>
  - Receive
      - *No Message*

### Server Code 32

**Ping**

#### Function Names

Museekd: SPing  
Nicotine: ServerPing

#### Description

Test if server responds

#### Data Order

  - Send
      - Empty Message
  - Receive
      - Empty Message

### Server Code 34

**Send Speed**

#### Function Names

Museekd: SSendSpeed  
Nicotine: SendSpeed

#### Description

**DEPRECIATED**

#### Data Order

  - Send *average transfer speed*
    1.  **string** <ins>username</ins>
    2.  **int** <ins>speed</ins>
  - Receive
      - *No Message*

### Server Code 35

**Shared Folders & Files**

#### Function Names

Museekd: SSharedFoldersFiles  
Nicotine: SharedFoldersFiles

#### Description

#### Data Order

  - Send
    1.  **int** <ins>dirs</ins>
    2.  **int** <ins>files</ins>
  - Receive
      - *No Message*

### Server Code 36

**Get User Stats** Museekd: SGetUserStats  
Nicotine: GetUserStats

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
  - Receive
    1.  **string** <ins>username</ins>
    2.  **int** <ins>avgspeed</ins>
    3.  **off\_t** <ins>downloadnum</ins>
    4.  **int** <ins>files</ins>
    5.  **int** <ins>dirs</ins>

### Server Code 40

**Queued Downloads**

#### Function Names

Museekd: **Not implemented**  
Nicotine: QueuedDownloads

#### Description

**DEPRECIATED**

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>username</ins>
    2.  **bool** <ins>slotsfree</ins> *Can
        immediately download*

### Server Code 41

**Kicked from Server**

#### Function Names

Museekd: SKicked  
Nicotine: \!Relogged

#### Description

You were disconnected (probably by another user with your name
connecting to the Server) so don't try to reconnect automatically.

#### Data Order

  - Send
      - Empty Message

<!-- end list -->

  - Receive
      - Empty Message

### Server Code 42

**User Search**

#### Function Names

Museekd: SUserSearch  
Nicotine: UserSearch

#### Description

Search a specific user's shares

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
    2.  **int** <ins>ticket</ins>
    3.  **string** <ins>search query</ins>
  - Receive
      - *No Message*

### Server Code 51

**Add Liked Interest**

#### Function Names

Museekd: SInterestAdd  
Nicotine: **AddThingILike**

#### Description

#### Data Order

  - Send
    1.  **string** <ins>item</ins>
  - Receive
      - *No Message*

### Server Code 52

**Remove Liked Interest**

#### Function Names

Museekd: SInterestRemove  
Nicotine: **RemoveThingILike**

#### Description

#### Data Order

  - Send
    1.  **string** <ins>item</ins>
  - Receive
      - *No Message*

### Server Code 54

**Get Recommendations**

#### Function Names

Museekd: SGetRecommendations  
Nicotine: **Recommendations**

#### Description

List of recommendations and a number for each

#### Data Order

  - Send
      - Empty Message
  - Receive
    1.  **int** <ins>number of total
        recommendations</ins>
    2.  Iterate for <ins>number of total
        recommendations</ins>
        1.  **string** <ins>recommendation</ins>
        2.  **int** <ins>number of recommendations
            this recommendation has</ins>
    3.  **int** <ins>number of total
        unrecommendations</ins>
    4.  Iterate for <ins>number of total
        unrecommendations</ins>
        1.  **string** <ins>unrecommendation</ins>
        2.  **int** <ins>number of unrecommendations
            this unrecommendation has (negative)</ins>

### Server Code 56

**Get Global Recommendations**

#### Function Names

Museekd: SGetGlobalRecommendations  
Nicotine: GlobalRecommendations

#### Description

List of recommendations and a number for each

#### Data Order

  - Send
      - Empty Message
  - Receive
    1.  **int** <ins>number of total
        recommendations</ins>
    2.  Iterate for <ins>number of total
        recommendations</ins>
        1.  **string** <ins>recommendation</ins>
        2.  **int** <ins>number of recommendations
            this recommendation has</ins>
    3.  **int** <ins>number of total
        unrecommendations</ins>
    4.  Iterate for <ins>number of total
        unrecommendations</ins>
        1.  **string** <ins>unrecommendation</ins>
        2.  **int** <ins>number of unrecommendations
            this unrecommendation has (negative)</ins>

### Server Code 57

**Get User Interests**

#### Function Names

Museekd:  
Nicotine: UserInterests

#### Description

Get a User's Liked and Hated Interests

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
  - Receive
    1.  **string** <ins>username</ins>
    2.  **int** <ins>number of liked interests</ins>
    3.  Iterate for <ins>number of liked
        interests</ins>
        1.  **string** <ins>interest</ins>
    4.  **int** <ins>number of hated interests</ins>
    5.  Iterate for <ins>number of hated
        interests</ins>
        1.  **string** <ins>interest</ins>

### Server Code 64

**Room List**

#### Function Names

Museekd: SRoomList  
Nicotine: RoomList

#### Description

List of rooms and the number of users in them. Soulseek has a room size
requirement of about 50 users when first connecting. Refreshing the list
will download all rooms.

#### Data Order

  - Send
      - Empty Message
  - Receive
    1.  **int** <ins>number of rooms</ins>
    2.  Iterate for <ins>number of rooms</ins>
        1.  **string** <ins>room</ins>
    3.  **int** <ins>number of rooms</ins> (unused
        in museekd)
    4.  Iterate for <ins>number of rooms</ins>
        1.  **int** <ins>number of users in
            room</ins>

### Server Code 65

**Exact File Search**

#### Function Names

Museekd: SExactFileSearch  
Nicotine: ExactFileSearch

#### Description

SEEMS BROKEN (no results even with official client)

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>username</ins>
    2.  **uint32** <ins>ticket</ins>
    3.  **string** <ins>filename</ins>
    4.  **string** <ins>path</ins>
    5.  **off\_t** <ins>filesize</ins>
    6.  **uint32** <ins>checkum</ins>

### Server Code 66

**Global / Admin Message**

#### Function Names

Museekd: SGlobalMessage  
Nicotine: AdminMessage

#### Description

Admins send this message to all users

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>message</ins>

### Server Code 69

**Privileged Users**

#### Function Names

Museekd: SPrivilegedUsers  
Nicotine: PrivilegedUsers

#### Description

List of privileged users

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **int** <ins>number of users</ins>
    2.  Iterate <ins>number of users</ins>
        1.  **string** <ins>user</ins>

### Server Code 71

**Have No Parents**

#### Function Names

Museekd: SHaveNoParents  
Nicotine: HaveNoParent

#### Description

#### Data Order

  - Send
    1.  **bool** <ins>have\_parents</ins> (is a
        boolean internal to museekd)
  - Receive
      - *No Message*

### Server Code 73

**Parent's IP**

#### Function Names

Museekd: SParentIP

#### Description

Send our parent's IP to the server

#### Data Order

  - Send
    1.  **ip** <ins>ip</ins>
  - Receive
      - *No Message*

### Server Code 83

ParentMinSpeed

#### Description

Unknown Purpose

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **int** <ins>number</ins>

### Server Code 84

ParentSpeedRatio

#### Description

Unknown Purpose. Number was 0x0a before 157c. Now 0x64 since 157 NS 13c.

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **int** <ins>number</ins>

### Server Code 86

**Parent Inactivity Timeout**

#### Description

**DEPRECIATED**

#### Function Names

Museekd: SParentInactivityTimeout  
Nicotine: ParentInactivityTimeout

#### Description

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **int** <ins>number</ins>

### Server Code 87

**Search Inactivity Timeout**

#### Description

**DEPRECIATED**

#### Function Names

Museekd: SSearchInactivityTimeout  
Nicotine: SearchInactivityTimeout

#### Description

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **int** <ins>number</ins>

### Server Code 88

**Minimum Parents In Cache**

#### Description

**DEPRECIATED**

#### Function Names

Museekd: SMinParentsInCache  
Nicotine: MinParentsInCache

#### Description

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **int** <ins>number</ins>

### Server Code 90

**Distributed Alive Interval**

#### Description

**DEPRECIATED**

#### Function Names

Museekd: SDistribAliveInterval  
Nicotine: DistribAliveInterval

#### Description

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **int** <ins>number</ins>

### Server Code 91

**Add Privileged User**

#### Function Names

Museekd: SAddPrivileged  
Nicotine: AddToPrivileged

#### Description

Add a new privileged user to your list of global privileged users

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>user</ins>

### Server Code 92

**Check Privileges**

#### Function Names

Museekd: SCheckPrivileges  
Nicotine: CheckPrivileges

#### Description

#### Data Order

  - Send
      - Empty Message
  - Receive
    1.  **int** <ins>time\_left</ins>

### Server Code 93

**Search Request**

#### Description

The server sends us search requests from other users

#### Function Names

Museekd: SSearchRequest

#### Data Order

  - Send
      - No Message
  - Receive
    1.  **uint8** <ins>distributed code
        (DSearchRequest)</ins>
    2.  **int** <ins>unknown</ins>
    3.  **string** <ins>username</ins>
    4.  **int** <ins>token</ins>
    5.  **string** <ins>query</ins>

### Server Code 100

**Accept Children**

#### Description

Tell the server if we want to have some children

#### Function Names

Museekd: SAcceptChildren

#### Data Order

  - Send
    1.  **bool** <ins>accept</ins>
  - Receive
      - No Message

### Server Code 102

**Net Info**

#### Description

#### Function Names

Museekd: SNetInfo  
Nicotine: NetInfo

#### Data Order

  - Send
      - Empty Message
  - Receive *list of search parents*
    1.  **int** <ins>number of parents</ins>
    2.  Iterate for <ins>number of parents</ins>
        1.  **string** <ins>user</ins>
        2.  **IP** <ins>IP address</ins>
        3.  **int** <ins>port</ins>

### Server Code 103

**Wishlist Search**

#### Function Names

Museekd: SWishlistSearch  
Nicotine: WishlistSearch

#### Description

#### Data Order

  - Send
    1.  **int** <ins>ticket</ins>
    2.  **string** <ins>search query</ins>
  - Receive
      - *No Message*

### Server Code 104

**Wishlist Interval**

#### Function Names

Museekd: SWishlistInterval  
Nicotine: WishlistInterval

#### Description

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **int** <ins>interval</ins>

### Server Code 110

**Get Similar Users**

#### Function Names

Museekd: SGetSimilarUsers  
Nicotine: SimilarUsers

#### Description

#### Data Order

  - Send
      - Empty Message
  - Receive
    1.  **int** <ins>number of users</ins>
    2.  Iterate for <ins>number of user</ins>
        1.  **string** <ins>user</ins>
        2.  **int** <ins>status</ins>

### Server Code 111

**Get Item Recommendations**

#### Function Names

Museekd: SGetItemRecommendations  
Nicotine: ItemRecommendations

#### Description

#### Data Order

  - Send
    1.  **string** <ins>item</ins>
  - Receive
    1.  **string** <ins>item</ins>
    2.  **int** <ins>number of
        recommendations</ins><ins> </ins>
    3.  Iterate for <ins>number of
        recommendations</ins><ins> </ins>
        1.  **string** <ins>recommendation</ins>
        2.  **int** <ins>number of recommendations
            for this recommendation (can be negative)</ins>

### Server Code 112

**Get Item Similar Users**

#### Function Names

Museekd: SGetItemSimilarUsers  
Nicotine: ItemSimilarUsers

#### Description

#### Data Order

  - Send
    1.  **string** <ins>item</ins>
  - Receive
    1.  **string** <ins>item</ins>
    2.  **int** <ins>number of users</ins>
    3.  Iterate for <ins>number of user</ins>
        1.  **string** <ins>user</ins>
        2.  **int** 0

### Server Code 113

**Room Tickers**

#### Function Names

Museekd: SRoomTickers  
Nicotine: RoomTickerState

#### Description

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>
    2.  **int** <ins>number of users</ins>
    3.  Iterate for <ins>number of user</ins>
        1.  **string** <ins>user</ins>
        2.  **string** <ins>tickers</ins>

### Server Code 114

**Room Ticker Add**

#### Function Names

Museekd: SRoomTickerAdd  
Nicotine: RoomTickerAdd

#### Description

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>
    2.  **string** <ins>user</ins>
    3.  **string** <ins>ticker</ins>

### Server Code 115

**Room Ticker Remove**

#### Function Names

Museekd: SRoomTickerRemove  
Nicotine: RoomTickerRemove

#### Description

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>
    2.  **string** <ins>user</ins>

### Server Code 116

**Set Room Ticker**

#### Function Names

Museekd: SSetRoomTicker  
Nicotine: RoomTickerSet

#### Description

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
    2.  **string** <ins>ticker</ins>
  - Receive
      - *No Message*

### Server Code 117

**Add Hated Interest**

#### Function Names

Museekd: SInterestHatedAdd  
Nicotine: AddThingIHate

#### Description

#### Data Order

  - Send
    1.  **string** <ins>item</ins>
  - Receive
      - *No Message*

### Server Code 118

**Remove Hated Interest**

#### Function Names

Museekd: SInterestHatedRemove  
Nicotine: RemoveThingIHate

#### Description

#### Data Order

  - Send
    1.  **string** <ins>item</ins>
  - Receive
      - *No Message*

### Server Code 120

**Room Search**

#### Function Names

Museekd: SRoomSearch  
Nicotine: RoomSearch

#### Description

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
    2.  **string** <ins>ticket</ins>
    3.  **string** <ins>search query</ins>
  - Receive
      - *No Message*

### Server Code 121

**Send Upload Speed**

#### Function Names

Museekd: **SSendUploadSpeed**  
Nicotine: SendUploadSpeed

#### Description

#### Data Order

  - Send *average upload transfer speed*
    1.  **int** <ins>speed</ins>
  - Receive
      - *No Message*

### Server Code 122

**A user's Soulseek Privileges**

#### Function Names

Museekd: **SUserPrivileges**  
Nicotine: Not implemented

#### Description

#### Data Order

  - Send
    1.  **string** <ins>user</ins>
  - Receive
    1.  **string** <ins>user</ins>
    2.  **char** <ins>privileged</ins> (boolean
        internal to museekd)

### Server Code 123

**Give Soulseek Privileges to user**

#### Function Names

Museekd: SGivePrivileges  
Nicotine: GivePrivileges

#### Description

#### Data Order

  - Send
    1.  **string** <ins>user</ins>
    2.  **int** <ins>days</ins>
  - Receive
      - *No Message*

### Server Code 124

**Server sends us a Notification about our privileges**

#### Function Names

Nicotine: NotifyPrivileges

#### Description

#### Data Order

  - Send
    1.  **int** <ins>token</ins>
    2.  **string** <ins>user</ins>
  - Receive
      - *No Message*

### Server Code 125

**Acknowledge Privilege Notification**

#### Function Names

Nicotine: AckNotifyPrivileges

#### Description

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **int** <ins>token</ins>

### Server Code 126

**Branch Level**

#### Description

Tell the server what is our position in our branch (xth generation)

#### Function Names

Museekd: **SBranchLevel**

#### Data Order

  - Send
    1.  **int** <ins>branch\_level</ins>
  - Receive
      - *No Message*

### Server Code 127

**Branch Root**

#### Description

Tell the server the username of the root of the branch we're in

#### Function Names

Museekd: **SBranchRoot**

#### Data Order

  - Send
    1.  **string** <ins>branch\_root</ins>
  - Receive
      - *No Message*

### Server Code 129

**Child depth**

#### Description

Tell the server the maximum number of generation of children we have.

#### Function Names

Museekd: **SChildDepth**

#### Data Order

  - Send
    1.  **int** <ins>child\_depth</ins>
  - Receive
      - *No Message*

### Server Code 133

**Private Room Users**

#### Description

We get this when we've created a private room

#### Function Names

Museekd: Unimplemented  
Nicotine: PrivateRoomUsers

#### Data Order

  - Send
    1.  *No Message*
  - Receive
    1.  **string** <ins>room</ins>
    2.  **int** <ins>number of users</ins>
    3.  Iterate for <ins>number of users</ins>
        1.  **string** <ins>users</ins>

### Server Code 134

**Private Room Add User**

#### Description

We get / receive this when we add a user to a private room.

#### Function Names

Museekd: Unimplemented  
Nicotine: PrivateRoomAddUser

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
    2.  **string** <ins>user</ins>
  - Receive
    1.  **string** <ins>room</ins>
    2.  **string** <ins>user</ins>

### Server Code 135

**Private Room Remove User**

#### Description

We get / send this when we remove a user from a private room

#### Function Names

Museekd: Unimplemented  
Nicotine: PrivateRoomRemoveUser

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
    2.  **string** <ins>user</ins>
  - Receive
    1.  **string** <ins>room</ins>
    2.  **string** <ins>user</ins>

### Server Code 136

**Private Room Drop Membership**

#### Description

We do this to remove our own membership of a private room.

#### Function Names

Museekd: Unimplemented  
Nicotine: PrivateRoomDismember

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 137

**Private Room Drop Ownership**

#### Description

We do this to stop owning a private room.

#### Function Names

Museekd: Unimplemented  
Nicotine: PrivateRoomDisown

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 138

**Private Room Unknown**

#### Description

Undocumented

#### Function Names

Museekd: Unimplemented  
Nicotine: PrivateRoomSomething

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 139

**Private Room Added**

#### Description

We are sent this when we are added to a private room.

#### Function Names

Museekd: Unimplemented  
Nicotine: PrivateRoomAdded

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 140

**Private Room Removed**

#### Description

We are sent this when we are removed from a private room.

#### Function Names

Museekd: Unimplemented  
Nicotine: PrivateRoomRemoved

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 141

**Private Room Toggle**

#### Description

We send this when we want to enable or disable invitations to private
rooms

#### Function Names

Museekd: Unimplemented  
Nicotine: PrivateRoomToggle

#### Data Order

  - Send
    1.  **bool** <ins>enable</ins>
  - Receive
    1.  **bool** <ins>enable</ins>

### Server Code 143

**Private Room Add Operator**

#### Description

We send this to add private room operator abilities to a user

#### Function Names

Museekd: Unimplemented  
Nicotine: PrivateRoomAddOperator

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 144

**Private Room Remove Operator**

#### Description

We send this to remove privateroom operator abilities from a user

#### Function Names

Museekd: Unimplemented  
Nicotine: PrivateRoomRemoveOperator

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 145

**Private Room Operator Added**

#### Description

> We receive this when given privateroom operator abilities

#### Function Names

Museekd: Unimplemented  
Nicotine: PrivateRoomOperatorAdded

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 146

**Private Room Operator Removed**

#### Description

We receive this when privateroom operator abilities are removed

#### Function Names

Museekd: Unimplemented  
Nicotine: PrivateRoomOperatorRemoved

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 148

**Private Room Owned**

#### Description

Undocumented

#### Function Names

Museekd: Unimplemented  
Nicotine: PrivateRoomOwned

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 1001

**Cannot Connect**

#### Function Names

Museekd: **SCannotConnect**  
Nicotine: CantConnectToPeer

#### Description

See also: [Peer Connection Message
Order](#peer-connection-message-order)

#### Data Order

  - Send *to the Server if we cannot connect to a peer.*
    1.  **int** <ins>token</ins>
    2.  **string** <ins>user</ins>
  - Receive *this response means we are both firewalled or otherwise
    unable to connect to each other.*
    1.  **int** <ins>token</ins>
    2.  **string** <ins>user</ins>

# Peer Messages

| Send         | Receive           |
| ------------ | ----------------- |
| Send to Peer | Receive from Peer |

In museekd 0.1.13, these messages are sent and received in
Museek/PeerConnection.cc and defined in Museek/PeerMessages.hh

#### The Peer Init Message format

| Message Length | Code   | Message Contents |
| -------------- | ------ | ---------------- |
| 4 Bytes        | 1 Byte | ...              |

#### Peer Init Message Index

| Code | Message                         |
| ---- | ------------------------------- |
| 0    | [Pierce Firewall](#peer-code-0) |
| 1    | [Peer Init](#peer-code-1)       |

### Peer Connection Message Order

1.  User A sends a [Peer Init](#peer-code-1) to User
    B (Fails: socket cannot connect)
2.  User A sends [ConnectToPeer](#server-code-18) to
    the Server with a unique token
3.  The Server sends a
    [ConnectToPeer](#server-code-18) response to
    User B with the same token
4.  User B sends a [Pierce Firewall](#peer-code-0)
    to User A with the same token (if this fails connections are doomed)
5.  User B sends a [Cannot
    Connect](#server-code-1001) to the Server
6.  The Server sends a [Cannot
    Connect](#server-code-1001) response to User A

### Peer Code 0

**Pierce Firewall**

#### Function Names

#### Description

See also: [Peer Connection Message
Order](#peer-connection-message-order)

#### Data Order

  - Send
      - **uint32** <ins>token</ins> *Unique Number*
  - Receive
      - **uint32** <ins>token</ins> *Unique Number*

### Peer Code 1

**Peer Init**

#### Function Names

#### Description

See also: [Peer Connection Message
Order](#peer-connection-message-order)

#### Data Order

  - Send
      - **string** <ins>user</ins> *Local Username*
      - **string** <ins>type</ins> *Connection Type
        (P, F or D)*
      - **uint32** <ins>token</ins> *Unique Number*
  - Receive
      - **string** <ins>user</ins> *Remote Username*
      - **string** <ins>type</ins> *Connection Type
        (P, F or D)*
      - **uint32** <ins>token</ins> *Unique Number*

#### The Message format

| Message Length | Code    | Message Contents |
| -------------- | ------- | ---------------- |
| 4 Bytes        | 4 Bytes | ...              |

#### Message Index

| Code | Message                                    |
| ---- | ------------------------------------------ |
| 4    | [Shares Request](#peer-code-4)             |
| 5    | [Shares Reply](#peer-code-5)               |
| 8    | [Search Request](#peer-code-8)             |
| 9    | [Search Reply](#peer-code-9)               |
| 15   | [Info Request](#peer-code-15)              |
| 16   | [Info Reply](#peer-code-16)                |
| 36   | [Folder Contents Request](#peer-code-36)   |
| 37   | [Folder Contents Reply](#peer-code-37)     |
| 40   | [Transfer Request](#peer-code-40)          |
| 41   | [Upload Reply](#peer-code-41a)             |
| 41   | [Download Reply](#peer-code-41b)           |
| 41   | [Transfer Reply](#peer-code-41c)           |
| 42   | [Upload Placehold](#peer-code-42)          |
| 43   | [Queue Download](#peer-code-43)            |
| 44   | [Upload Queue Notification](#peer-code-44) |
| 46   | [Upload Failed](#peer-code-46)             |
| 50   | [Queue Failed](#peer-code-50)              |
| 51   | [Place In Queue Request](#peer-code-51)    |
| 52   | [Upload Queue Notification](#peer-code-52) |

### Peer Code 4

**Shares Request**

#### Function Names

Museekd: PSharesRequest  
Nicotine: GetShareFileList

#### Description

#### Data Order

  - Send
      - Empty Message
  - Receive
      - Empty Message

### Peer Code 5

**Shares Reply**

#### Function Names

Museekd: PSharesReply  
Nicotine: SharedFileList

#### Description

#### Data Order

  - Send *shares database*
    1.  Iterate thru shares database
        1.  **data**
  - Receive *shares database*
    1.  decompress
    2.  **int** <ins>number of directories</ins>
    3.  Iterate <ins>number of directories</ins>
        1.  **string** <ins>directory</ins>
        2.  **int** <ins>number of files</ins>
        3.  Iterate <ins>number of files</ins>
            1.  **char** ??? (unused)
            2.  **string** <ins>filename</ins>
            3.  **off\_t** <ins>size</ins> *File
                size*
            4.  **string** <ins>ext</ins>
                *Extentsion*
            5.  **int** <ins>number of
                attributes</ins>
            6.  Iterate <ins>number of
                attributes</ins>
                1.  **int** <ins>place in
                    attributes</ins> (unused by museekd)
                2.  **int** <ins>attribute</ins>

### Peer Code 8

**Search Request**

#### Function Names

Museekd: PSearchRequest  
Nicotine: FileSearchRequest

#### Description

#### Data Order

  - Send
    1.  **int** <ins>ticket</ins>
    2.  **string** <ins>query</ins>
  - Receive
    1.  **int** <ins>ticket</ins>
    2.  **string** <ins>query</ins>

### Peer Code 9

**Search Reply**

#### Function Names

Museekd: PSearchReply  
Nicotine: FileSearchResult

#### Description

#### Data Order

  - Send
    1.  **string** <ins>user</ins>
    2.  **int** <ins>ticket</ins>
    3.  **int** <ins>results size</ins> *number of
        results*
    4.  Iterate for number of results
        1.  **uchar** 1
        2.  **string** <ins>filename</ins>
        3.  **int** <ins>size</ins>
        4.  **string** <ins>ext</ins>
        5.  **int** <ins>attribute size</ins>
        6.  Iterate <ins>number of attributes</ins>
            1.  **int** <ins>place in
                attributes</ins>
            2.  **int** <ins>attribute</ins>
  - Receive
    1.  **string** <ins>user</ins>
    2.  **int** <ins>ticket</ins>
    3.  **int** <ins>results size</ins>
        <ins>number of results</ins>
    4.  Iterate for <ins>number of results</ins>
        museekd pop buffer
        1.  **string** <ins>filename</ins>
        2.  **off\_t** <ins>size</ins>
        3.  **string** <ins>ext</ins>
        4.  **int** <ins>number of attributes</ins>
        5.  Iterate <ins>number of attributes</ins>
            1.  **int** <ins>place in
                attributes</ins>
            2.  **int** <ins>attribute</ins>

### Peer Code 15

**Info Request**

#### Function Names

Museekd: PInfoRequest  
Nicotine: UserInfoRequest

#### Description

#### Data Order

  - Send
      - Empty Message
  - Receive
      - Empty Message

### Peer Code 16

**Info Reply**

#### Function Names

Museekd: PInfoReply  
Nicotine: UserInfoReply

#### Description

#### Data Order

  - Send description, picture, totalupl, queuesize, slotfree
    1.  **string** <ins>description</ins>
    2.  Check contents of <ins>picture</ins>
          - If <ins>picture</ins> is not empty
            1.  **bool** <ins>has\_picture</ins> 1
            2.  **string** <ins>picture</ins>
          - If <ins>picture</ins> is empty
            1.  **bool** <ins>has\_picture</ins> 0
    3.  **uint** <ins>totalupl</ins>
    4.  **uint** <ins>queuesize</ins>
    5.  **bool** <ins>slotsfree</ins> *Can
        immediately upload*
  - Receive
    1.  **string** <ins>description</ins>
    2.  **char** <ins>has\_picture</ins>
    3.  Check contents of <ins>has\_picture</ins>
        1.  If <ins>has\_picture</ins> is not empty
            1.  **string** <ins>picture</ins>
    4.  **int** <ins>totalupl</ins>
    5.  **int** <ins>queuesize</ins>
    6.  **bool** <ins>slotsfree</ins> *Can
        immediately download*

### Peer Code 36

**Folder Contents Request**

#### Function Names

Museekd: PFolderContentsRequest  
Nicotine: FolderContentsRequest

#### Description

#### Data Order

  - Send
    1.  **int** <ins>number of files in
        directory</ins>
    2.  Iterate <ins>number of files in
        directory</ins>
        1.  **string** <ins>file</ins>
  - Receive
    1.  **int** <ins>number of files in
        directory</ins>
    2.  Iterate <ins>number of files in
        directory</ins>
        1.  **string** <ins>file</ins>

### Peer Code 37

**Folder Contents Reply**

#### Function Names

Museekd: PFolderContentsReply  
Nicotine: FolderContentsResponse

#### Description

#### Data Order

  - Send
    1.  **int** <ins>number of folders</ins>
    2.  Iterate for <ins>number of folders</ins>
        1.  **string** <ins>dir</ins>
        2.  **int** <ins>number of files</ins>
        3.  Iterate <ins>number of files</ins>
            1.  **char** <ins>true</ins>
            2.  **string** <ins>file</ins>
            3.  **off\_t** <ins>size</ins>
            4.  **string** <ins>ext</ins> Extension
            5.  **int** <ins>number of
                attributes</ins>
                1.  **int** <ins>attribute
                    number</ins>
                2.  **int** <ins>attribute</ins>
  - Receive
    1.  **int** <ins>number of folders</ins>
    2.  Iterate for <ins>number of folders</ins>
        1.  **string** <ins>dir</ins>
        2.  **int** <ins>number of files</ins>
        3.  Iterate <ins>number of files</ins>
            1.  **char** <ins>???</ins> (unused)
            2.  **string** <ins>file</ins>
            3.  **off\_t** <ins>size</ins>
            4.  **string** <ins>ext</ins> Extension
            5.  **int** <ins>number of
                attributes</ins>
                1.  **int** <ins>attribute
                    number</ins>
                2.  **int** <ins>attribute</ins>

### Peer Code 40

**Transfer Request**

#### Function Names

Museekd: PTransferRequest  
Nicotine: TransferRequest

#### Description

#### Data Order

  - Send
    1.  **int** <ins>direction</ins>
    2.  **int** <ins>ticket</ins>
    3.  **string** <ins>filename</ins>
    4.  Check contents of <ins>direction</ins>
          - **off\_t** <ins>filesize</ins> *if
            direction == 1*
  - Receive
    1.  **int** <ins>direction</ins>
    2.  **int** <ins>ticket</ins>
    3.  **string** <ins>filename</ins>
    4.  Check contents of <ins>direction</ins>
          - **off\_t** <ins>filesize</ins> *if
            direction == 1*

### Peer Code 41 a

**Upload Reply**

#### Function Names

Museekd: PUploadReply  
Nicotine: TransferResponse

#### Description

#### Data Order

  - Send
    1.  **string** <ins>ticket</ins>
    2.  **uchar** <ins>allowed</ins>
    3.  Check contents of <ins>allowed</ins>
          - **off\_t** <ins>filesize</ins> *if
            allowed == 1*
          - **string** <ins>reason</ins> *if allowed
            == 0*
  - Receive
      - *No Message*

### Peer Code 41 b

**Download Reply**

#### Function Names

Museekd: PDownloadReply  
Nicotine: TransferResponse

#### Description

#### Data Order

  - Send
    1.  **string** <ins>ticket</ins>
    2.  **uchar** <ins>allowed</ins>
    3.  Check contents of <ins>allowed</ins>
          - **string** <ins>reason</ins> *if allowed
            == 0*
  - Receive
      - *No Message*

### Peer Code 41 c

**Transfer Reply**

#### Function Names

Museekd: PTransferReply  
Nicotine: TransferResponse

#### Description

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>ticket</ins>
    2.  **char** <ins>allowed</ins> == 1
    3.  Check contents of <ins>allowed</ins>
          - **off\_t** <ins>filesize</ins> *if
            allowed == 1*
          - **string** <ins>reason</ins> *if allowed
            == 0*

### Peer Code 42

**Upload Placehold**

#### Function Names

Museekd: PUploadPlacehold  
Nicotine: PlaceholdUpload

#### Description

**DEPRECIATED**

#### Data Order

  - Send
    1.  **string** <ins>filename</ins>
  - Receive
    1.  **string** <ins>filename</ins>

### Peer Code 43

**Queue Upload or Download**

#### Function Names

Museekd: PQueueDownload  
Nicotine: QueueUpload

#### Description

#### Data Order

  - Send
    1.  **string** <ins>filename</ins>
  - Receive
    1.  **string** <ins>filename</ins>

### Peer Code 44

**Place In Queue Reply**

#### Function Names

Museekd: PPlaceInQueueReply  
Nicotine: PlaceInQueue

#### Description

#### Data Order

  - Send
    1.  **string** <ins>filename</ins>
    2.  **string** <ins>place</ins>
  - Receive
    1.  **string** <ins>filename</ins>
    2.  **string** <ins>place</ins>

### Peer Code 46

**Upload Failed**

#### Function Names

Museekd: PUploadFailed  
Nicotine: UploadFailed

#### Description

#### Data Order

  - Send
    1.  **string** <ins>filename</ins>
  - Receive
    1.  **string** <ins>filename</ins>

### Peer Code 50

**Queue Failed**

#### Function Names

Museekd: PQueueFailed  
Nicotine: QueueFailed

#### Description

#### Data Order

  - Send
    1.  **string** <ins>filename</ins>
    2.  **string** <ins>reason</ins>
  - Receive
    1.  **string** <ins>filename</ins>
    2.  **string** <ins>reason</ins>

### Peer Code 51

**Place In Queue Request**

#### Function Names

Museekd: PPlaceInQueueRequest  
Nicotine: PlaceInQueueRequest

#### Description

#### Data Order

  - Send
    1.  **string** <ins>filename</ins>
  - Receive
    1.  **string** <ins>filename</ins>

### Peer Code 52

**Upload Queue Notification**

#### Function Names

Museekd: PUploadQueueNotification  
Nicotine: **Not implemented**

#### Description

#### Data Order

  - Send
      - *Empty Message*
  - Receive
      - *Empty Message*

## Distributed Messages

| Send    | Send to Node      |
| ------- | ----------------- |
| Receive | Receive from Node |

In museekd 0.1.13, these messages are sent and received in
Museek/DistribConnection.cc and defined in Museek/DistribMessages.hh

#### The Message format

| Message Length | Code   | Message Contents |
| -------------- | ------ | ---------------- |
| 4 Bytes        | 1 Byte | ...              |

#### Message Index

| Code | Message                               |
| ---- | ------------------------------------- |
| 0    | [Ping](#distributed-code-0)           |
| 3    | [Search Request](#distributed-code-3) |
| 4    | [Branch Level](#distributed-code-4)   |
| 5    | [Branch Root](#distributed-code-5)    |
| 7    | [Child Depth](#distributed-code-7)    |

### Distributed Code 0

**Ping**

#### Description

Send it every 60 sec.

#### Function Names

Museekd: **DPing**  
Nicotine: DistribAlive

#### Data Order

  - Send
      - *Empty Message*
  - Receive
    1.  **uint32** <ins>unknown</ins>

### Distributed Code 3

**Search Request**

#### Description

Transmit the search requests to our children. (Search requests are sent
to us by the server using SSearchRequest if we're a branch root, or by
our parent using DSearchRequest)

#### Function Names

Museekd: **DSearchRequest**  
Nicotine: DistribSearch

#### Data Order

  - Send
    1.  **uint32** <ins>unknown</ins>
    2.  **string** <ins>user</ins>
    3.  **uint32** <ins>ticket</ins>
    4.  **string** <ins>query</ins>
  - Receive
    1.  **uint32** <ins>unknown</ins>
    2.  **string** <ins>user</ins>
    3.  **uint32** <ins>ticket</ins>
    4.  **string** <ins>query</ins>

### Distributed Code 4

**Branch Level**

#### Description

See SBranchLevel

#### Function Names

Museekd: **DBranchLevel**  
Nicotine: DistribUnknown

#### Data Order

  - Send
    1.  **uint32** <ins>branch\_level</ins>
  - Receive
    1.  **uint32** <ins>branch\_level</ins>

### Distributed Code 5

**Branch Root**

#### Description

See SBranchRoot

#### Function Names

Museekd: **DBranchRoot**

#### Data Order

  - Send
    1.  **string** <ins>branch\_root</ins>
  - Receive
    1.  **string** <ins>branch\_root</ins>

### Distributed Code 7

**Branch Level**

#### Description

See SChildDepth

#### Function Names

Museekd: **DChildDepth**

#### Data Order

  - Send
    1.  **uint32** <ins>child\_depth</ins>
  - Receive
    1.  **uint32** <ins>child\_depth</ins>

## Museek Data Types

### StringMap

  - std::map\<std::string, std::string\>

### StringList

  - std::vector\<std::string\>

### WStringList

  - std::vector\<std::wstring\> WStringList

### WTickers

  - std::map\<std::string, std::wstring\>

### Recommendations, SimilarUsers, RoomList

  - std::map\<std::string, uint32\>

### NetInfo

  - std::map\<std::string, std::pair\<std::string, uint32\> \>

### UserData

1.  **uint32** <ins>status</ins> *Online Status*
2.  **uint32** <ins>avgspeed</ins> *Average Speed*
3.  **uint32** <ins>downloadnum</ins> *Number of
    downloaded files*
4.  **uint32** <ins>files</ins> *Files shared*
5.  **uint32** <ins>dirs</ins> *Directories shared*
6.  **bool** <ins>slotsfree</ins> *Slots free*

### RoomData

  - std::map\<std::string, UserData\>

### Folder

  - std::map\<std::string, FileEntry\>

### Shares

  - std::map\<std::string, Folder\>

### WFolder

  - std::map\<std::wstring, FileEntry\>

### Folders

  - std::map\<std::string, Shares\>

### WShares

  - std::map\<std::wstring, WFolder\>

### WFolders

  - std::map\<std::wstring, WShares\>

### off\_t

  - Packed as a 64bit Integer
