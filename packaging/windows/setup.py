#!/usr/bin/env python3
# COPYRIGHT (C) 2021-2022 Nicotine+ Contributors
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

import glob
import os
import ssl
import subprocess
import sys
import tempfile

from cx_Freeze import Executable, setup  # pylint: disable=import-error


if sys.platform == "win32":
    GUI_BASE = "Win32GUI"
    SYS_BASE = sys.prefix
    LIB_FOLDER = os.path.join(SYS_BASE, "bin")
    LIB_EXTENSION = ".dll"
    ICON_NAME = "icon.ico"

elif sys.platform == "darwin":
    GUI_BASE = None
    SYS_BASE = "/usr/local"
    LIB_FOLDER = os.path.join(SYS_BASE, "lib")
    LIB_EXTENSION = (".dylib", ".so")
    ICON_NAME = "icon.icns"

else:
    raise RuntimeError("Only Windows and macOS are supported")

TEMP_PATH = tempfile.mkdtemp()
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
BUILD_PATH = os.path.join(CURRENT_PATH, "build")
PROJECT_PATH = os.path.abspath(os.path.join(CURRENT_PATH, "..", ".."))
sys.path.append(PROJECT_PATH)

from pynicotine.config import config  # noqa: E402  # pylint: disable=import-error,wrong-import-position

APPLICATION_NAME = config.application_name
APPLICATION_ID = config.application_id
VERSION = config.version
AUTHOR = config.author
COPYRIGHT = config.copyright

SCRIPT_NAME = "nicotine"
GTK_VERSION = os.environ.get("NICOTINE_GTK_VERSION") or '3'
USE_LIBADWAITA = GTK_VERSION == '4' and os.environ.get("NICOTINE_LIBADWAITA") == '1'

# Setup
setup(
    name=APPLICATION_NAME,
    description=APPLICATION_NAME,
    author=AUTHOR,
    version=VERSION,
    options={
        "build": dict(
            build_base=BUILD_PATH,
            build_exe=os.path.join(BUILD_PATH, "package", APPLICATION_NAME)
        ),
        "build_exe": dict(
            packages=[],
            excludes=["tkinter"],
            include_files=[]
        ),
        "bdist_msi": dict(
            all_users=True,
            dist_dir=BUILD_PATH,
            install_icon=os.path.join(CURRENT_PATH, ICON_NAME),
            upgrade_code="{8ffb9dbb-7106-41fc-9e8a-b2469aa1fe9f}"
        ),
        "bdist_mac": dict(
            bundle_name=APPLICATION_NAME,
            iconfile=os.path.join(CURRENT_PATH, ICON_NAME),
            plist_items=[
                ("CFBundleName", APPLICATION_NAME),
                ("CFBundleIdentifier", APPLICATION_ID),
                ("CFBundleShortVersionString", VERSION),
                ("CFBundleVersion", VERSION),
                ("CFBundleInfoDictionaryVersion", "6.0"),
                ("NSHumanReadableCopyright", COPYRIGHT)
            ],
            include_resources=[],
            codesign_identity='-',
            codesign_deep=True
        ),
        "bdist_dmg": dict(
            applications_shortcut=True
        )
    },
    packages=[],
    executables=[
        Executable(
            script=os.path.join(PROJECT_PATH, SCRIPT_NAME),
            base=GUI_BASE,
            target_name=APPLICATION_NAME,
            icon=os.path.join(CURRENT_PATH, ICON_NAME),
            copyright=COPYRIGHT,
            shortcut_name=APPLICATION_NAME,
            shortcut_dir="ProgramMenuFolder"
        )
    ],
)
