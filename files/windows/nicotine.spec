# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import sys
from PyInstaller.utils.hooks import collect_data_files
sys.modules['FixTk'] = None
sys.modules['lib2to3'] = None

# Files to be added to the frozen app
added_files = [
    #
    # Application core modules
    #

    # About icon
    ('../org.nicotine_plus.Nicotine.svg', 'share/icons/hicolor/scalable/apps'),

    # Tray icons
    ('../../img/tray', 'share/icons/hicolor/32x32/apps'),

    # GTK Builder files, plugins, geoip database
    ('../../pynicotine', 'pynicotine'),

    # Translation files
    ('../../languages', 'share/locale'),
]

# Get the cacert.pem for the update checker
datas.append(
    collect_data_files('requests')
)

a = Analysis(['../../nicotine'],
             pathex=['.'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['FixTk', 'lib2to3', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

# Remove unwanted files
for file in a.datas[:]:
    excluded = ('.ani', '.cur', '.md', '.po', '.pot', '.py', '.pyc', 'merge_all', 'remove_fuzzy', 'remove_mo')

    if file[0].endswith(excluded) or \
        file[0].endswith('.png') and not 'org.nicotine_plus.Nicotine' in file[0]:
        a.datas.remove(file)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Nicotine+',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='nicotine-plus.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Nicotine+')
