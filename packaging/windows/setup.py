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

import glob
import os
import ssl
import sys

# Provide access to the pynicotine module
PYNICOTINE_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", ".."))
sys.path.append(PYNICOTINE_PATH)

from pkgutil import walk_packages

import pynicotine.plugins

from cx_Freeze import Executable, setup
from pynicotine.config import config
from pynicotine.i18n import generate_translations


gui_base = None
sys_base = None

include_files = []
plugin_packages = []
required_dlls = []

if sys.platform == "win32":
    gui_base = "Win32GUI"
    sys_base = sys.prefix
    required_dlls = [
        'gtk-3-0',
        'gdk-3-0',
        'epoxy-0',
        'gdk_pixbuf-2.0-0',
        'pango-1.0-0',
        'pangocairo-1.0-0',
        'pangoft2-1.0-0',
        'pangowin32-1.0-0',
        'atk-1.0-0',
        'xml2-2',
        'rsvg-2-2'
    ]

elif sys.platform == "darwin":
    sys_base = "/usr/local"

else:
    raise RuntimeError("Only Windows and macOS is supported")

# Plugins
for importer, name, ispkg in walk_packages(path=pynicotine.plugins.__path__, prefix="pynicotine.plugins."):
    if ispkg:
        plugin_packages.append(name)

# SSL support
ssl_paths = ssl.get_default_verify_paths()
include_files.append((ssl_paths.openssl_cafile, "etc/ssl/cert.pem"))

if os.path.exists(ssl_paths.openssl_capath):
    include_files.append((ssl_paths.openssl_capath, "etc/ssl/certs"))

# Translations
_mo_entries, languages = generate_translations()
include_files.append((os.path.join(PYNICOTINE_PATH, "mo"), "share/locale"))

for language in languages:
    mo_path = os.path.join("share/locale", language, "LC_MESSAGES/gtk30.mo")
    full_path = os.path.join(sys.prefix, mo_path)

    if os.path.exists(full_path):
        include_files.append((full_path, mo_path))

# GTK
required_folders = [
    "lib/gdk-pixbuf-2.0"
]
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
    "GModule-2.0"
]
icons_path = os.path.join(sys_base, "share/icons")
themes_path = os.path.join(sys_base, "share/themes")

for dll_name in required_dlls:
    filename = "lib" + dll_name + ".dll"
    include_files.append((os.path.join(sys_base, "bin", filename), filename))

for folder in required_folders:
    include_files.append((os.path.join(sys_base, folder), folder))

for namespace in required_gi_namespaces:
    subpath = "lib/girepository-1.0/%s.typelib" % namespace
    include_files.append((os.path.join(sys_base, subpath), subpath))

for path in glob.glob(os.path.join(icons_path, '**'), recursive=True):
    icon_path = os.path.relpath(path, icons_path)

    if not icon_path.startswith(("Adwaita", "hicolor")):
        continue

    if path.endswith((".theme", ".svg")):
        include_files.append((path, os.path.relpath(path, sys_base)))

for path in glob.glob(os.path.join(themes_path, '**'), recursive=True):
    theme_path = os.path.relpath(path, themes_path)

    if theme_path.startswith(("Default", "Mac")):
        include_files.append((path, os.path.relpath(path, sys_base)))

# Setup
setup(
    name="Nicotine+",
    author="Nicotine+ Team",
    version=config.version,
    options={
        "build_exe": dict(
            build_exe="dist/Nicotine+",
            packages=["gi"] + plugin_packages,
            excludes=["pygtkcompat", "tkinter"],
            include_files=include_files,
        ),
    },
    executables=[
        Executable(
            script=os.path.join(PYNICOTINE_PATH, "nicotine"),
            target_name="Nicotine+.exe",
            base=gui_base,
        )
    ],
)
