# COPYRIGHT (C) 2020-2023 Nicotine+ Contributors COPYRIGHT (C) 2020 Lene Preuss
# <lene.preuss@gmail.com> COPYRIGHT (C) 2016-2017 Michael Labouebe
# <gfarmerfr@free.fr> COPYRIGHT (C) 2007 daelstorm <daelstorm@gmail.com>
# COPYRIGHT (C) 2003-2004 Hyriand <hyriand@thegraveyard.org> COPYRIGHT (C)
# 2001-2003 Alexander Kanavin
#
# GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import os
import sys

UINT32_LIMIT = 4294967295
UINT64_LIMIT = 18446744073709551615
FILE_SIZE_SUFFIXES = [
    "B",
    "KiB",
    "MiB",
    "GiB",
    "TiB",
    "PiB",
    "EiB",
    "ZiB",
    "YiB",
]
PUNCTUATION = [
    # ASCII and Unicode punctuation
    "!",
    '"',
    "#",
    "$",
    "%",
    "&",
    "'",
    "(",
    ")",
    "*",
    "+",
    ",",
    "-",
    ".",
    "/",
    ":",
    ";",
    "<",
    "=",
    ">",
    "?",
    "@",
    "[",
    "\\",
    "]",
    "^",
    "_",
    "`",
    "{",
    "|",
    "}",
    "~",
    "\u00a1",
    "\u00a7",
    "\u00ab",
    "\u00b6",
    "\u00b7",
    "\u00bb",
    "\u00bf",
    "\u037e",
    "\u0387",
    "\u055a",
    "\u055b",
    "\u055c",
    "\u055d",
    "\u055e",
    "\u055f",
    "\u0589",
    "\u058a",
    "\u05be",
    "\u05c0",
    "\u05c3",
    "\u05c6",
    "\u05f3",
    "\u05f4",
    "\u0609",
    "\u060a",
    "\u060c",
    "\u060d",
    "\u061b",
    "\u061d",
    "\u061e",
    "\u061f",
    "\u066a",
    "\u066b",
    "\u066c",
    "\u066d",
    "\u06d4",
    "\u0700",
    "\u0701",
    "\u0702",
    "\u0703",
    "\u0704",
    "\u0705",
    "\u0706",
    "\u0707",
    "\u0708",
    "\u0709",
    "\u070a",
    "\u070b",
    "\u070c",
    "\u070d",
    "\u07f7",
    "\u07f8",
    "\u07f9",
    "\u0830",
    "\u0831",
    "\u0832",
    "\u0833",
    "\u0834",
    "\u0835",
    "\u0836",
    "\u0837",
    "\u0838",
    "\u0839",
    "\u083a",
    "\u083b",
    "\u083c",
    "\u083d",
    "\u083e",
    "\u085e",
    "\u0964",
    "\u0965",
    "\u0970",
    "\u09fd",
    "\u0a76",
    "\u0af0",
    "\u0c77",
    "\u0c84",
    "\u0df4",
    "\u0e4f",
    "\u0e5a",
    "\u0e5b",
    "\u0f04",
    "\u0f05",
    "\u0f06",
    "\u0f07",
    "\u0f08",
    "\u0f09",
    "\u0f0a",
    "\u0f0b",
    "\u0f0c",
    "\u0f0d",
    "\u0f0e",
    "\u0f0f",
    "\u0f10",
    "\u0f11",
    "\u0f12",
    "\u0f14",
    "\u0f3a",
    "\u0f3b",
    "\u0f3c",
    "\u0f3d",
    "\u0f85",
    "\u0fd0",
    "\u0fd1",
    "\u0fd2",
    "\u0fd3",
    "\u0fd4",
    "\u0fd9",
    "\u0fda",
    "\u104a",
    "\u104b",
    "\u104c",
    "\u104d",
    "\u104e",
    "\u104f",
    "\u10fb",
    "\u1360",
    "\u1361",
    "\u1362",
    "\u1363",
    "\u1364",
    "\u1365",
    "\u1366",
    "\u1367",
    "\u1368",
    "\u1400",
    "\u166e",
    "\u169b",
    "\u169c",
    "\u16eb",
    "\u16ec",
    "\u16ed",
    "\u1735",
    "\u1736",
    "\u17d4",
    "\u17d5",
    "\u17d6",
    "\u17d8",
    "\u17d9",
    "\u17da",
    "\u1800",
    "\u1801",
    "\u1802",
    "\u1803",
    "\u1804",
    "\u1805",
    "\u1806",
    "\u1807",
    "\u1808",
    "\u1809",
    "\u180a",
    "\u1944",
    "\u1945",
    "\u1a1e",
    "\u1a1f",
    "\u1aa0",
    "\u1aa1",
    "\u1aa2",
    "\u1aa3",
    "\u1aa4",
    "\u1aa5",
    "\u1aa6",
    "\u1aa8",
    "\u1aa9",
    "\u1aaa",
    "\u1aab",
    "\u1aac",
    "\u1aad",
    "\u1b5a",
    "\u1b5b",
    "\u1b5c",
    "\u1b5d",
    "\u1b5e",
    "\u1b5f",
    "\u1b60",
    "\u1b7d",
    "\u1b7e",
    "\u1bfc",
    "\u1bfd",
    "\u1bfe",
    "\u1bff",
    "\u1c3b",
    "\u1c3c",
    "\u1c3d",
    "\u1c3e",
    "\u1c3f",
    "\u1c7e",
    "\u1c7f",
    "\u1cc0",
    "\u1cc1",
    "\u1cc2",
    "\u1cc3",
    "\u1cc4",
    "\u1cc5",
    "\u1cc6",
    "\u1cc7",
    "\u1cd3",
    "\u2010",
    "\u2011",
    "\u2012",
    "\u2013",
    "\u2014",
    "\u2015",
    "\u2016",
    "\u2017",
    "\u2018",
    "\u2019",
    "\u201a",
    "\u201b",
    "\u201c",
    "\u201d",
    "\u201e",
    "\u201f",
    "\u2020",
    "\u2021",
    "\u2022",
    "\u2023",
    "\u2024",
    "\u2025",
    "\u2026",
    "\u2027",
    "\u2030",
    "\u2031",
    "\u2032",
    "\u2033",
    "\u2034",
    "\u2035",
    "\u2036",
    "\u2037",
    "\u2038",
    "\u2039",
    "\u203a",
    "\u203b",
    "\u203c",
    "\u203d",
    "\u203e",
    "\u203f",
    "\u2040",
    "\u2041",
    "\u2042",
    "\u2043",
    "\u2045",
    "\u2046",
    "\u2047",
    "\u2048",
    "\u2049",
    "\u204a",
    "\u204b",
    "\u204c",
    "\u204d",
    "\u204e",
    "\u204f",
    "\u2050",
    "\u2051",
    "\u2053",
    "\u2054",
    "\u2055",
    "\u2056",
    "\u2057",
    "\u2058",
    "\u2059",
    "\u205a",
    "\u205b",
    "\u205c",
    "\u205d",
    "\u205e",
    "\u207d",
    "\u207e",
    "\u208d",
    "\u208e",
    "\u2308",
    "\u2309",
    "\u230a",
    "\u230b",
    "\u2329",
    "\u232a",
    "\u2768",
    "\u2769",
    "\u276a",
    "\u276b",
    "\u276c",
    "\u276d",
    "\u276e",
    "\u276f",
    "\u2770",
    "\u2771",
    "\u2772",
    "\u2773",
    "\u2774",
    "\u2775",
    "\u27c5",
    "\u27c6",
    "\u27e6",
    "\u27e7",
    "\u27e8",
    "\u27e9",
    "\u27ea",
    "\u27eb",
    "\u27ec",
    "\u27ed",
    "\u27ee",
    "\u27ef",
    "\u2983",
    "\u2984",
    "\u2985",
    "\u2986",
    "\u2987",
    "\u2988",
    "\u2989",
    "\u298a",
    "\u298b",
    "\u298c",
    "\u298d",
    "\u298e",
    "\u298f",
    "\u2990",
    "\u2991",
    "\u2992",
    "\u2993",
    "\u2994",
    "\u2995",
    "\u2996",
    "\u2997",
    "\u2998",
    "\u29d8",
    "\u29d9",
    "\u29da",
    "\u29db",
    "\u29fc",
    "\u29fd",
    "\u2cf9",
    "\u2cfa",
    "\u2cfb",
    "\u2cfc",
    "\u2cfe",
    "\u2cff",
    "\u2d70",
    "\u2e00",
    "\u2e01",
    "\u2e02",
    "\u2e03",
    "\u2e04",
    "\u2e05",
    "\u2e06",
    "\u2e07",
    "\u2e08",
    "\u2e09",
    "\u2e0a",
    "\u2e0b",
    "\u2e0c",
    "\u2e0d",
    "\u2e0e",
    "\u2e0f",
    "\u2e10",
    "\u2e11",
    "\u2e12",
    "\u2e13",
    "\u2e14",
    "\u2e15",
    "\u2e16",
    "\u2e17",
    "\u2e18",
    "\u2e19",
    "\u2e1a",
    "\u2e1b",
    "\u2e1c",
    "\u2e1d",
    "\u2e1e",
    "\u2e1f",
    "\u2e20",
    "\u2e21",
    "\u2e22",
    "\u2e23",
    "\u2e24",
    "\u2e25",
    "\u2e26",
    "\u2e27",
    "\u2e28",
    "\u2e29",
    "\u2e2a",
    "\u2e2b",
    "\u2e2c",
    "\u2e2d",
    "\u2e2e",
    "\u2e30",
    "\u2e31",
    "\u2e32",
    "\u2e33",
    "\u2e34",
    "\u2e35",
    "\u2e36",
    "\u2e37",
    "\u2e38",
    "\u2e39",
    "\u2e3a",
    "\u2e3b",
    "\u2e3c",
    "\u2e3d",
    "\u2e3e",
    "\u2e3f",
    "\u2e40",
    "\u2e41",
    "\u2e42",
    "\u2e43",
    "\u2e44",
    "\u2e45",
    "\u2e46",
    "\u2e47",
    "\u2e48",
    "\u2e49",
    "\u2e4a",
    "\u2e4b",
    "\u2e4c",
    "\u2e4d",
    "\u2e4e",
    "\u2e4f",
    "\u2e52",
    "\u2e53",
    "\u2e54",
    "\u2e55",
    "\u2e56",
    "\u2e57",
    "\u2e58",
    "\u2e59",
    "\u2e5a",
    "\u2e5b",
    "\u2e5c",
    "\u2e5d",
    "\u3001",
    "\u3002",
    "\u3003",
    "\u3008",
    "\u3009",
    "\u300a",
    "\u300b",
    "\u300c",
    "\u300d",
    "\u300e",
    "\u300f",
    "\u3010",
    "\u3011",
    "\u3014",
    "\u3015",
    "\u3016",
    "\u3017",
    "\u3018",
    "\u3019",
    "\u301a",
    "\u301b",
    "\u301c",
    "\u301d",
    "\u301e",
    "\u301f",
    "\u3030",
    "\u303d",
    "\u30a0",
    "\u30fb",
    "\ua4fe",
    "\ua4ff",
    "\ua60d",
    "\ua60e",
    "\ua60f",
    "\ua673",
    "\ua67e",
    "\ua6f2",
    "\ua6f3",
    "\ua6f4",
    "\ua6f5",
    "\ua6f6",
    "\ua6f7",
    "\ua874",
    "\ua875",
    "\ua876",
    "\ua877",
    "\ua8ce",
    "\ua8cf",
    "\ua8f8",
    "\ua8f9",
    "\ua8fa",
    "\ua8fc",
    "\ua92e",
    "\ua92f",
    "\ua95f",
    "\ua9c1",
    "\ua9c2",
    "\ua9c3",
    "\ua9c4",
    "\ua9c5",
    "\ua9c6",
    "\ua9c7",
    "\ua9c8",
    "\ua9c9",
    "\ua9ca",
    "\ua9cb",
    "\ua9cc",
    "\ua9cd",
    "\ua9de",
    "\ua9df",
    "\uaa5c",
    "\uaa5d",
    "\uaa5e",
    "\uaa5f",
    "\uaade",
    "\uaadf",
    "\uaaf0",
    "\uaaf1",
    "\uabeb",
    "\ufd3e",
    "\ufd3f",
    "\ufe10",
    "\ufe11",
    "\ufe12",
    "\ufe13",
    "\ufe14",
    "\ufe15",
    "\ufe16",
    "\ufe17",
    "\ufe18",
    "\ufe19",
    "\ufe30",
    "\ufe31",
    "\ufe32",
    "\ufe33",
    "\ufe34",
    "\ufe35",
    "\ufe36",
    "\ufe37",
    "\ufe38",
    "\ufe39",
    "\ufe3a",
    "\ufe3b",
    "\ufe3c",
    "\ufe3d",
    "\ufe3e",
    "\ufe3f",
    "\ufe40",
    "\ufe41",
    "\ufe42",
    "\ufe43",
    "\ufe44",
    "\ufe45",
    "\ufe46",
    "\ufe47",
    "\ufe48",
    "\ufe49",
    "\ufe4a",
    "\ufe4b",
    "\ufe4c",
    "\ufe4d",
    "\ufe4e",
    "\ufe4f",
    "\ufe50",
    "\ufe51",
    "\ufe52",
    "\ufe54",
    "\ufe55",
    "\ufe56",
    "\ufe57",
    "\ufe58",
    "\ufe59",
    "\ufe5a",
    "\ufe5b",
    "\ufe5c",
    "\ufe5d",
    "\ufe5e",
    "\ufe5f",
    "\ufe60",
    "\ufe61",
    "\ufe62",
    "\ufe63",
    "\ufe64",
    "\ufe65",
    "\ufe66",
    "\ufe68",
    "\ufe6a",
    "\ufe6b",
    "\uff01",
    "\uff02",
    "\uff03",
    "\uff05",
    "\uff06",
    "\uff07",
    "\uff08",
    "\uff09",
    "\uff0a",
    "\uff0b",
    "\uff0c",
    "\uff0d",
    "\uff0e",
    "\uff0f",
    "\uff1a",
    "\uff1b",
    "\uff1c",
    "\uff1d",
    "\uff1e",
    "\uff1f",
    "\uff20",
    "\uff3b",
    "\uff3c",
    "\uff3d",
    "\uff3f",
    "\uff5b",
    "\uff5c",
    "\uff5d",
    "\uff5e",
    "\uff5f",
    "\uff60",
    "\uff61",
    "\uff62",
    "\uff63",
    "\uff64",
    "\uff65",
    "\U00010100",
    "\U00010101",
    "\U00010102",
    "\U0001039f",
    "\U000103d0",
    "\U0001056f",
    "\U00010857",
    "\U0001091f",
    "\U0001093f",
    "\U00010a50",
    "\U00010a51",
    "\U00010a52",
    "\U00010a53",
    "\U00010a54",
    "\U00010a55",
    "\U00010a56",
    "\U00010a57",
    "\U00010a58",
    "\U00010a7f",
    "\U00010af0",
    "\U00010af1",
    "\U00010af2",
    "\U00010af3",
    "\U00010af4",
    "\U00010af5",
    "\U00010af6",
    "\U00010b39",
    "\U00010b3a",
    "\U00010b3b",
    "\U00010b3c",
    "\U00010b3d",
    "\U00010b3e",
    "\U00010b3f",
    "\U00010b99",
    "\U00010b9a",
    "\U00010b9b",
    "\U00010b9c",
    "\U00010ead",
    "\U00010f55",
    "\U00010f56",
    "\U00010f57",
    "\U00010f58",
    "\U00010f59",
    "\U00010f86",
    "\U00010f87",
    "\U00010f88",
    "\U00010f89",
    "\U00011047",
    "\U00011048",
    "\U00011049",
    "\U0001104a",
    "\U0001104b",
    "\U0001104c",
    "\U0001104d",
    "\U000110bb",
    "\U000110bc",
    "\U000110be",
    "\U000110bf",
    "\U000110c0",
    "\U000110c1",
    "\U00011140",
    "\U00011141",
    "\U00011142",
    "\U00011143",
    "\U00011174",
    "\U00011175",
    "\U000111c5",
    "\U000111c6",
    "\U000111c7",
    "\U000111c8",
    "\U000111cd",
    "\U000111db",
    "\U000111dd",
    "\U000111de",
    "\U000111df",
    "\U00011238",
    "\U00011239",
    "\U0001123a",
    "\U0001123b",
    "\U0001123c",
    "\U0001123d",
    "\U000112a9",
    "\U0001144b",
    "\U0001144c",
    "\U0001144d",
    "\U0001144e",
    "\U0001144f",
    "\U0001145a",
    "\U0001145b",
    "\U0001145d",
    "\U000114c6",
    "\U000115c1",
    "\U000115c2",
    "\U000115c3",
    "\U000115c4",
    "\U000115c5",
    "\U000115c6",
    "\U000115c7",
    "\U000115c8",
    "\U000115c9",
    "\U000115ca",
    "\U000115cb",
    "\U000115cc",
    "\U000115cd",
    "\U000115ce",
    "\U000115cf",
    "\U000115d0",
    "\U000115d1",
    "\U000115d2",
    "\U000115d3",
    "\U000115d4",
    "\U000115d5",
    "\U000115d6",
    "\U000115d7",
    "\U00011641",
    "\U00011642",
    "\U00011643",
    "\U00011660",
    "\U00011661",
    "\U00011662",
    "\U00011663",
    "\U00011664",
    "\U00011665",
    "\U00011666",
    "\U00011667",
    "\U00011668",
    "\U00011669",
    "\U0001166a",
    "\U0001166b",
    "\U0001166c",
    "\U000116b9",
    "\U0001173c",
    "\U0001173d",
    "\U0001173e",
    "\U0001183b",
    "\U00011944",
    "\U00011945",
    "\U00011946",
    "\U000119e2",
    "\U00011a3f",
    "\U00011a40",
    "\U00011a41",
    "\U00011a42",
    "\U00011a43",
    "\U00011a44",
    "\U00011a45",
    "\U00011a46",
    "\U00011a9a",
    "\U00011a9b",
    "\U00011a9c",
    "\U00011a9e",
    "\U00011a9f",
    "\U00011aa0",
    "\U00011aa1",
    "\U00011aa2",
    "\U00011b00",
    "\U00011b01",
    "\U00011b02",
    "\U00011b03",
    "\U00011b04",
    "\U00011b05",
    "\U00011b06",
    "\U00011b07",
    "\U00011b08",
    "\U00011b09",
    "\U00011c41",
    "\U00011c42",
    "\U00011c43",
    "\U00011c44",
    "\U00011c45",
    "\U00011c70",
    "\U00011c71",
    "\U00011ef7",
    "\U00011ef8",
    "\U00011f43",
    "\U00011f44",
    "\U00011f45",
    "\U00011f46",
    "\U00011f47",
    "\U00011f48",
    "\U00011f49",
    "\U00011f4a",
    "\U00011f4b",
    "\U00011f4c",
    "\U00011f4d",
    "\U00011f4e",
    "\U00011f4f",
    "\U00011fff",
    "\U00012470",
    "\U00012471",
    "\U00012472",
    "\U00012473",
    "\U00012474",
    "\U00012ff1",
    "\U00012ff2",
    "\U00016a6e",
    "\U00016a6f",
    "\U00016af5",
    "\U00016b37",
    "\U00016b38",
    "\U00016b39",
    "\U00016b3a",
    "\U00016b3b",
    "\U00016b44",
    "\U00016e97",
    "\U00016e98",
    "\U00016e99",
    "\U00016e9a",
    "\U00016fe2",
    "\U0001bc9f",
    "\U0001da87",
    "\U0001da88",
    "\U0001da89",
    "\U0001da8a",
    "\U0001da8b",
    "\U0001e95e",
    "\U0001e95f",
]
ILLEGALPATHCHARS = [
    # ASCII printable characters
    "?",
    ":",
    ">",
    "<",
    "|",
    "*",
    '"',
    # ASCII control characters
    "\u0000",
    "\u0001",
    "\u0002",
    "\u0003",
    "\u0004",
    "\u0005",
    "\u0006",
    "\u0007",
    "\u0008",
    "\u0009",
    "\u000a",
    "\u000b",
    "\u000c",
    "\u000d",
    "\u000e",
    "\u000f",
    "\u0010",
    "\u0011",
    "\u0012",
    "\u0013",
    "\u0014",
    "\u0015",
    "\u0016",
    "\u0017",
    "\u0018",
    "\u0019",
    "\u001a",
    "\u001b",
    "\u001c",
    "\u001d",
    "\u001e",
    "\u001f",
]
ILLEGALFILECHARS = ["\\", "/"] + ILLEGALPATHCHARS
LONG_PATH_PREFIX = "\\\\?\\"
REPLACEMENTCHAR = "_"
TRANSLATE_PUNCTUATION = str.maketrans(dict.fromkeys(PUNCTUATION, " "))


def clean_file(basename):

    for char in ILLEGALFILECHARS:
        if char in basename:
            basename = basename.replace(char, REPLACEMENTCHAR)

    # Filename can never end with a period or space on Windows machines
    basename = basename.rstrip(". ")

    if not basename:
        basename = REPLACEMENTCHAR

    return basename


def clean_path(path):

    path = os.path.normpath(path)

    # Without hacks it is (up to Vista) not possible to have more than 26
    # drives mounted, so we can assume a '\[a-zA-Z\]:' prefix for drives - we
    # shouldn't escape that
    drive = ""

    if len(path) >= 3 and path[1] == ":" and path[2] == os.sep:
        drive = path[:3]
        path = path[3:]

    for char in ILLEGALPATHCHARS:
        if char in path:
            path = path.replace(char, REPLACEMENTCHAR)

    path = "".join([drive, path])

    # Path can never end with a period or space on Windows machines
    path = path.rstrip(". ")

    return path


def encode_path(path, prefix=True):
    """Converts a file path to bytes for processing by the system.

    On Windows, also append prefix to enable extended-length path.
    """

    if sys.platform == "win32" and prefix:
        path = path.replace("/", "\\")

        if path.startswith("\\\\"):
            path = "UNC" + path[1:]

        path = LONG_PATH_PREFIX + path

    return path.encode("utf-8")


def human_length(seconds):

    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    if days > 0:
        return f"{days}:{hours:02d}:{minutes:02d}:{seconds:02d}"

    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    return f"{minutes}:{seconds:02d}"


def _human_speed_or_size(number, unit=None):

    if unit == "B":
        return humanize(number)

    try:
        for suffix in FILE_SIZE_SUFFIXES:
            if number < 1024:
                if number > 999:
                    return f"{number:.4g} {suffix}"

                return f"{number:.3g} {suffix}"

            number /= 1024

    except TypeError:
        pass

    return str(number)


def human_speed(speed):
    return _human_speed_or_size(speed) + "/s"


def human_size(filesize, unit=None):
    return _human_speed_or_size(filesize, unit)


def humanize(number):
    return f"{number:n}"


def factorize(filesize, base=1024):
    """Converts filesize string with a given unit into raw integer size,
    defaults to binary for "k", "m", "g" suffixes (KiB, MiB, GiB)"""

    if not filesize:
        return None, None

    filesize = filesize.lower()

    if filesize.endswith("b"):
        base = 1000  # Byte suffix found, prepare to use decimal if necessary
        filesize = filesize[:-1]

    if filesize.endswith("i"):
        base = 1024  # Binary requested, stop using decimal
        filesize = filesize[:-1]

    if filesize.endswith("g"):
        factor = pow(base, 3)
        filesize = filesize[:-1]

    elif filesize.endswith("m"):
        factor = pow(base, 2)
        filesize = filesize[:-1]

    elif filesize.endswith("k"):
        factor = base
        filesize = filesize[:-1]

    else:
        factor = 1

    try:
        return int(float(filesize) * factor), factor
    except ValueError:
        return None, factor


def truncate_string_byte(
    string, byte_limit, encoding="utf-8", ellipsize=False
):
    """Truncates a string to fit inside a byte limit."""

    string_bytes = string.encode(encoding)

    if len(string_bytes) <= byte_limit:
        # Nothing to do, return original string
        return string

    if ellipsize:
        ellipsis_char = "…".encode(encoding)
        string_bytes = (
            string_bytes[: max(byte_limit - len(ellipsis_char), 0)].rstrip()
            + ellipsis_char
        )
    else:
        string_bytes = string_bytes[:byte_limit]

    return string_bytes.decode(encoding, "ignore")


def unescape(string):
    """Removes quotes from the beginning and end of strings, and unescapes
    it."""

    string = string.encode("latin-1", "backslashreplace").decode(
        "unicode-escape"
    )

    try:
        if (string[0] == string[-1]) and string.startswith(("'", '"')):
            return string[1:-1]
    except IndexError:
        pass

    return string


def find_whole_word(word, text):
    """Returns start position of a whole word that is not in a subword."""

    if word not in text:
        return -1

    word_boundaries = [" "] + PUNCTUATION
    whole = False
    start = after = 0

    while not whole and start > -1:
        start = text.find(word, after)
        after = start + len(word)

        whole = (
            text[after] if after < len(text) else " "
        ) in word_boundaries and (
            text[start - 1] if start > 0 else " "
        ) in word_boundaries

    return start if whole else -1


def censor_text(text, censored_patterns, filler="*"):

    for word in censored_patterns:
        word = str(word)
        text = text.replace(word, filler * len(word))

    return text


def execute_command(
    command,
    replacement=None,
    background=True,
    returnoutput=False,
    hidden=False,
    placeholder="$",
):
    """Executes a string with commands, with partial support for bash-style
    quoting and pipes.

    The different parts of the command should be separated by spaces, a double
    quotation mark can be used to embed spaces in an argument.
    Pipes can be created using the bar symbol (|).

    If background is false the function will wait for all the launched
    processes to end before returning.

    If hidden is true, any window created by the command will be hidden
    (on Windows).

    If the 'replacement' argument is given, every occurrence of 'placeholder'
    will be replaced by 'replacement'.

    If the command ends with the ampersand symbol background
    will be set to True. This should only be done by the request of the user,
    if you want background to be true set the function argument.

    The only expected error to be thrown is the RuntimeError in case something
    goes wrong while executing the command.

    Example commands:
    * "C:\\Program Files\\WinAmp\\WinAmp.exe" --xforce "--title=Window Title"
    * mplayer $
    * echo $ | flite -t
    """

    # pylint: disable=consider-using-with

    from subprocess import PIPE, Popen

    # Example command: "C:\\Program Files\\WinAmp\\WinAmp.exe" --xforce
    # "--title=My Title" $ | flite -t
    if returnoutput:
        background = False

    command = command.strip()
    startupinfo = None

    if hidden and sys.platform == "win32":
        from subprocess import STARTF_USESHOWWINDOW, STARTUPINFO

        # Hide console window on Windows
        startupinfo = STARTUPINFO()
        startupinfo.dwFlags |= STARTF_USESHOWWINDOW

    if command.endswith("&"):
        command = command[:-1]
        if returnoutput:
            from pynicotine.logfacility import log

            log.add(
                "Yikes, I was asked to return output but I'm also asked"
                " to launch the process in the background. returnoutput"
                " gets precedent."
            )
        else:
            background = True

    unparsed = command
    arguments = []

    while unparsed.count('"') > 1:

        (pre, argument, post) = unparsed.split('"', 2)
        if pre:
            arguments += pre.rstrip(" ").split(" ")

        arguments.append(argument)
        unparsed = post.lstrip(" ")

    if unparsed:
        arguments += unparsed.split(" ")

    # arguments is now: \['C:\\Program Files\\WinAmp\\WinAmp.exe', '--xforce',
    # '--title=My Title', '$', '|', 'flite', '-t'\]
    subcommands = []
    current = []

    for argument in arguments:
        if argument == "|":
            subcommands.append(current)
            current = []
        else:
            current.append(argument)

    subcommands.append(current)

    # subcommands is now: \[\['C:\\Program Files\\WinAmp\\WinAmp.exe',
    # '--xforce', '--title=My Title', '$'\], \['flite', '-t'\]\]
    if replacement:
        for i, _ in enumerate(subcommands):
            subcommands[i] = [
                x.replace(placeholder, replacement) for x in subcommands[i]
            ]

    # Chaining commands...
    finalstdout = None
    if returnoutput:
        finalstdout = PIPE

    procs = []

    try:
        if len(subcommands) == 1:  # no need to fool around with pipes
            procs.append(
                Popen(
                    subcommands[0],
                    startupinfo=startupinfo,
                    stdout=finalstdout,
                )
            )
        else:
            procs.append(
                Popen(subcommands[0], startupinfo=startupinfo, stdout=PIPE)
            )

            for subcommand in subcommands[1:-1]:
                procs.append(
                    Popen(
                        subcommand,
                        startupinfo=startupinfo,
                        stdin=procs[-1].stdout,
                        stdout=PIPE,
                    )
                )

            procs.append(
                Popen(
                    subcommands[-1],
                    startupinfo=startupinfo,
                    stdin=procs[-1].stdout,
                    stdout=finalstdout,
                )
            )

        if not background and not returnoutput:
            procs[-1].wait()

    except Exception as error:
        command = subcommands[len(procs)]
        command_no = len(procs) + 1
        num_commands = len(subcommands)
        raise RuntimeError(
            "Problem while executing command"
            f" {command} ({command_no} of {num_commands}): {error}"
        ) from error

    if not returnoutput:
        return True

    return procs[-1].communicate()[0]


def _try_open_uri(uri):

    if sys.platform not in {"darwin", "win32"}:
        try:
            # pylint: disable=import-error
            from gi.repository import Gio

            Gio.AppInfo.launch_default_for_uri(uri)
            return

        except Exception:
            # Fall back to webbrowser module
            pass

    import webbrowser

    if not webbrowser.open(uri):
        raise webbrowser.Error("No known URI provider available")


def _open_path(path, is_folder=False, create_folder=False, create_file=False):
    """Currently used to either open a folder or play an audio file.

    Tries to run a user-specified command first, and falls back to the system
    default.
    """

    if path is None:
        return False

    try:
        from pynicotine.config import config

        path = os.path.abspath(path)
        path_encoded = encode_path(path)
        _path, separator, extension = path.rpartition(".")
        protocol_command = None
        protocol_handlers = config.sections["urls"]["protocols"]
        file_manager_command = config.sections["ui"]["filemanager"]

        if separator:
            from pynicotine.shares import FileTypes

            if "." + extension in protocol_handlers:
                protocol = "." + extension

            elif extension in FileTypes.AUDIO:
                protocol = "audio"

            elif extension in FileTypes.IMAGE:
                protocol = "image"

            elif extension in FileTypes.VIDEO:
                protocol = "video"

            elif extension in FileTypes.DOCUMENT:
                protocol = "document"

            elif extension in FileTypes.TEXT:
                protocol = "text"

            elif extension in FileTypes.ARCHIVE:
                protocol = "archive"

            else:
                protocol = None

            protocol_command = protocol_handlers.get(protocol)

        if not os.path.exists(path_encoded):
            if create_folder:
                os.makedirs(path_encoded)

            elif create_file:
                with open(path_encoded, "w", encoding="utf-8"):
                    # Create empty file
                    pass
            else:
                raise FileNotFoundError("File path does not exist")

        if is_folder and "$" in file_manager_command:
            execute_command(file_manager_command, path)

        elif protocol_command:
            execute_command(protocol_command, path)

        elif sys.platform == "win32":
            os.startfile(path_encoded)  # pylint: disable=no-member

        elif sys.platform == "darwin":
            execute_command("open $", path)

        else:
            _try_open_uri("file:///" + path)

    except Exception as error:
        from pynicotine.logfacility import log

        log.add(
            _("Cannot open file path %(path)s: %(error)s"),
            {"path": path, "error": error},
        )
        return False

    return True


def open_file_path(file_path, create_file=False):
    return _open_path(path=file_path, create_file=create_file)


def open_folder_path(folder_path, create_folder=False):
    return _open_path(
        path=folder_path, is_folder=True, create_folder=create_folder
    )


def open_uri(uri):
    """Open a URI in an external (web) browser.

    The given argument has to be a properly formed URI including the
    scheme (fe. HTTP).
    """

    from pynicotine.config import config

    try:
        # Situation 1, user defined a way of handling the protocol
        protocol = uri[: uri.find(":")]

        if not protocol.startswith(".") and protocol not in {
            "audio",
            "image",
            "video",
            "document",
            "text",
            "archive",
        }:
            protocol_handlers = config.sections["urls"]["protocols"]
            protocol_command = protocol_handlers.get(
                protocol + "://"
            ) or protocol_handlers.get(protocol)

            if protocol_command:
                execute_command(protocol_command, uri)
                return True

            if protocol == "slsk":
                from pynicotine.core import core

                core.userbrowse.open_soulseek_url(uri.strip())
                return True

        # Situation 2, user did not define a way of handling the protocol
        _try_open_uri(uri)

        return True

    except Exception as error:
        from pynicotine.logfacility import log

        log.add(
            _("Cannot open URL %(url)s: %(error)s"),
            {"url": uri, "error": error},
        )

    return False


def load_file(file_path, load_func, use_old_file=False):

    try:
        if use_old_file:
            file_path = f"{file_path}.old"

        elif os.path.isfile(encode_path(f"{file_path}.old")):
            file_path_encoded = encode_path(file_path)

            if not os.path.isfile(file_path_encoded):
                raise OSError("*.old file is present but main file is missing")

            if os.path.getsize(file_path_encoded) <= 0:
                # Empty files should be considered broken/corrupted
                raise OSError("*.old file is present but main file is empty")

        return load_func(file_path)

    except Exception as error:
        from pynicotine.logfacility import log

        log.add(
            _(
                "Something went wrong while reading file %(filename)s:"
                " %(error)s"
            ),
            {"filename": file_path, "error": error},
        )

        if not use_old_file:
            # Attempt to load data from .old file
            log.add(_("Attempting to load backup of file %s"), file_path)
            return load_file(file_path, load_func, use_old_file=True)

    return None


def write_file_and_backup(path, callback, protect=False):

    path_encoded = encode_path(path)
    path_old_encoded = encode_path(f"{path}.old")

    # Back up old file to path.old
    try:
        if os.path.exists(path_encoded) and os.stat(path_encoded).st_size > 0:
            os.replace(path_encoded, path_old_encoded)

            if protect:
                os.chmod(path_old_encoded, 0o600)

    except Exception as error:
        from pynicotine.logfacility import log

        log.add(
            _("Unable to back up file %(path)s: %(error)s"),
            {"path": path, "error": error},
        )
        return

    # Save new file
    if protect:
        oldumask = os.umask(0o077)

    try:
        with open(path_encoded, "w", encoding="utf-8") as file_handle:
            callback(file_handle)

            # Force write to file immediately in case of hard shutdown
            file_handle.flush()
            os.fsync(file_handle.fileno())

    except Exception as error:
        from pynicotine.logfacility import log

        log.add(
            _("Unable to save file %(path)s: %(error)s"),
            {"path": path, "error": error},
        )

        # Attempt to restore file
        try:
            if os.path.exists(path_old_encoded):
                os.replace(path_old_encoded, path_encoded)

        except Exception as second_error:
            log.add(
                _("Unable to restore previous file %(path)s: %(error)s"),
                {"path": path, "error": second_error},
            )

    if protect:
        os.umask(oldumask)


# Debugging #


def debug(*args):
    """Prints debugging info."""

    from pynicotine.logfacility import log

    truncated_args = [
        arg[:200] if isinstance(arg, str) else arg for arg in args
    ]
    log.add("*" * 8, truncated_args)


def strace(function):
    """Decorator for debugging."""

    from itertools import chain
    from pynicotine.logfacility import log

    def newfunc(*args, **kwargs):
        name = function.__name__
        lst = ", ".join(repr(x) for x in chain(args, list(kwargs.values())))
        log.add(f"{name}({lst})")
        retvalue = function(*args, **kwargs)
        log.add(f"{name}({lst}): {repr(retvalue)}")
        return retvalue

    return newfunc
