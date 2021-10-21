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

from pkgutil import walk_packages
from cx_Freeze import Executable, setup


include_files = []
plugin_packages = []

required_dlls = (
    "gtk-",
    "epoxy-",
    "gdk_pixbuf-",
    "pango-",
    "pangocairo-",
    "pangoft2-",
    "pangowin32-",
    "atk-",
    "xml2-",
    "rsvg-"
)
required_gi_namespaces = (
    "Gtk-",
    "Gio-",
    "Gdk-",
    "GLib-",
    "Atk-",
    "HarfBuzz-",
    "Pango-",
    "GObject-",
    "GdkPixbuf-",
    "cairo-",
    "GModule-"
)
required_icon_packs = (
    "Adwaita",
    "hicolor"
)
required_themes = (
    "Default",
    "Mac"
)

pynicotine_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", ".."))
dlls_path = "bin"
pixbuf_path = "lib/gdk-pixbuf-2.0"
typelibs_path = "lib/girepository-1.0"
locales_path = "share/locale"
icons_path = "share/icons"
themes_path = "share/themes"

sys.path.append(pynicotine_path)

if sys.platform == "win32":
    target_name = "Nicotine+.exe"
    gui_base = "Win32GUI"
    sys_base = sys.prefix

elif sys.platform == "darwin":
    target_name = "Nicotine+.app"
    gui_base = None
    sys_base = "/usr/local"

else:
    raise RuntimeError("Only Windows and macOS is supported")

# Translations
from pynicotine.i18n import generate_translations  # noqa: E402

_mo_entries, languages = generate_translations()
include_files.append((os.path.join(pynicotine_path, "mo"), "share/locale"))

for full_path in glob.glob(os.path.join(sys_base, locales_path, '**'), recursive=True):
    locale_path = os.path.relpath(full_path, os.path.join(sys_base, locales_path))

    if locale_path.startswith(tuple(languages)) and locale_path.contains("gtk") and locale_path.endswith("0.mo"):
        include_files.append((full_path, locale_path))

# Plugins
import pynicotine.plugins  # noqa: E402

for importer, name, ispkg in walk_packages(path=pynicotine.plugins.__path__, prefix="pynicotine.plugins."):
    if ispkg:
        plugin_packages.append(name)

# SSL support
ssl_paths = ssl.get_default_verify_paths()
include_files.append((ssl_paths.openssl_cafile, "etc/ssl/cert.pem"))

if os.path.exists(ssl_paths.openssl_capath):
    include_files.append((ssl_paths.openssl_capath, "etc/ssl/certs"))

# DLLs
for full_path in glob.glob(os.path.join(sys_base, dlls_path, '**')):
    dll_path = os.path.relpath(full_path, os.path.join(sys_base, dlls_path))

    if dll_path.startswith(required_dlls) and dll_path.endswith(".dll"):
        include_files.append((full_path, dll_path))

# Pixbuf loaders
include_files.append((os.path.join(sys_base, pixbuf_path), pixbuf_path))

# Typelibs
for full_path in glob.glob(os.path.join(sys_base, typelibs_path, '**')):
    typelib_path = os.path.relpath(full_path, os.path.join(sys_base, typelibs_path))

    if typelib_path.startswith(required_gi_namespaces) and typelib_path.endswith(".typelib"):
        include_files.append((full_path, typelib_path))

# Icons
for full_path in glob.glob(os.path.join(sys_base, icons_path, '**'), recursive=True):
    icon_path = os.path.relpath(full_path, os.path.join(sys_base, icons_path))

    if icon_path.startswith(required_icon_packs) and icon_path.endswith((".theme", ".svg")):
        include_files.append((full_path, icon_path))

# Themes
for full_path in glob.glob(os.path.join(sys_base, themes_path, '**'), recursive=True):
    theme_path = os.path.relpath(full_path, os.path.join(sys_base, themes_path))

    if theme_path.startswith(required_themes):
        include_files.append((full_path, theme_path))

# Setup
from pynicotine.config import config  # noqa: E402

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
            script=os.path.join(pynicotine_path, "nicotine"),
            target_name=target_name,
            base=gui_base,
        )
    ],
)
