# -*- mode: python ; coding: utf-8 -*-

# COPYRIGHT (C) 2021 Nicotine+ Team
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

import os
import sys

# Provide access to the pynicotine module
PYNICOTINE_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", ".."))
sys.path.append(PYNICOTINE_PATH)

from pkgutil import walk_packages

import pynicotine.plugins

from cx_Freeze import Executable, setup
from pynicotine.config import config
from pynicotine.i18n import generate_translations


include_files = []
plugins = [name for importer, name, ispkg in walk_packages(path=pynicotine.plugins.__path__, prefix="pynicotine.plugins.") if ispkg]

# Translations
_mo_entries, languages = generate_translations()
include_files.append((os.path.join(PYNICOTINE_PATH, "mo"), "share/locale"))

for language in languages:
    mo_path = os.path.join("share/locale", language, "LC_MESSAGES/gtk30.mo")
    full_path = os.path.join(sys.prefix, mo_path)

    if os.path.exists(full_path):
        include_files.append((full_path, mo_path))

# GTK
required_dlls = ['libgtk-3-0.dll']

for dll in required_dlls:
    include_files.append((os.path.join(sys.prefix, "bin", dll), dll))

required_gi_namespaces = [
    "Gtk-3.0",
    "Gio-2.0",
    "Gdk-3.0",
    "GLib-2.0",
    "HarfBuzz-0.0",
    "Atk-1.0",
    "Pango-1.0",
    "GObject-2.0",
    "GdkPixbuf-2.0",
    "cairo-1.0",
    "GModule-2.0",
]

for namespace in required_gi_namespaces:
    subpath = "lib/girepository-1.0/%s.typelib" % namespace
    include_files.append((os.path.join(sys.prefix, subpath), subpath))

gtk_files = [
    "lib/gdk-pixbuf-2.0/2.10.0/loaders/libpixbufloader-png.dll",
    "lib/gdk-pixbuf-2.0/2.10.0/loaders/libpixbufloader-svg.dll",
    "lib/gdk-pixbuf-2.0/2.10.0/loaders.cache"
]

for gtk_file in gtk_files:
    include_files.append((os.path.join(sys.prefix, gtk_file), gtk_file))

# Setup
setup(
    name="Nicotine+",
    author="Nicotine+ Team",
    version=config.version,
    options={
        "build_exe": dict(
            build_exe="dist/Nicotine+",
            packages=["gi"] + plugins,
            excludes=["lib2to3", "pygtkcompat", "tkinter"],
            include_files=include_files,
        ),
    },
    executables=[
        Executable(
            script=os.path.join(PYNICOTINE_PATH, "nicotine"),
            targetName="Nicotine+.exe",
            base="Win32GUI" if sys.platform == "win32" else None,
        )
    ],
)
