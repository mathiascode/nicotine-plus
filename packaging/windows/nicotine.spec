# -*- mode: python ; coding: utf-8 -*-

# COPYRIGHT (C) 2020 Nicotine+ Team
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
import sys

from ctypes.util import find_library
from pkgutil import walk_packages

# Provide access to the pynicotine module
sys.path.append('.')

import pynicotine.plugins

from pynicotine.utils import version
from setup import generate_mo_translations


""" Add Contents """


# Add plugins and SSL support
hiddenimports = ["certifi"] + \
    [name for importer, name, ispkg in walk_packages(path=pynicotine.plugins.__path__, prefix="pynicotine.plugins.") if ispkg]


# GTK Builder files, plugins, geoip database, translations
datas = [("../../pynicotine", "pynicotine")]
mo_entries, languages = generate_mo_translations()

for target_path, mo_files in mo_entries:
    datas.append(("../../" + mo_files[0], target_path))


# Analyze required files
a = Analysis(['../../nicotine'],
             pathex=['.'],
             binaries=[],
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[],
             runtime_hooks=[],
             excludes=['FixTk', 'lib2to3', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None,
             noarchive=False)


# Remove unwanted files added in previous step
excluded = ('.ani', '.cur', '.md', '.png', '.py', '.pyc')

for file in a.datas[:]:
    if file[0].endswith(excluded):
        a.datas.remove(file)

    elif 'share/icons' in file[0] or \
            'share/themes' in file[0]:
        theme = file[0].split('/')[2]

        # Remove unwanted themes
        if theme not in ('Adwaita', 'Mac', 'hicolor', 'win32'):
            a.datas.remove(file)

        elif 'Adwaita/cursors' in file[0]:
            a.datas.remove(file)

    elif 'share/locale' in file[0]:
        lang = file[0].split('/')[2]

        # Remove system translations for unsupported languages
        if lang not in languages:
            a.datas.remove(file)


""" Archive """


pyz = PYZ(a.pure, a.zipped_data,
          cipher=None)


""" Freeze Application """


name = 'Nicotine+'

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name=name,
          debug=False,
          strip=False,
          upx=False,
          console=False,
          icon='nicotine.ico')


coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name=name)


""" Create macOS .app """


app = BUNDLE(coll,
             name=name + '.app',
             icon='nicotine.icns',
             info_plist=info_plist = {
                 "CFBundleDisplayName": name,
                 "NSHighResolutionCapable": True,
             },
             bundle_identifier='org.nicotine_plus.Nicotine',
             version=version)
