import os
import sys
from cx_Freeze import Executable, setup


common_include_files = []

required_dll_search_paths = os.getenv("PATH", os.defpath).split(os.pathsep)
required_dlls = [
    'libgtk-3-0.dll',
    'libgdk-3-0.dll',
    'libepoxy-0.dll',
    'libgdk_pixbuf-2.0-0.dll',
    'libpango-1.0-0.dll',
    'libpangocairo-1.0-0.dll',
    'libpangoft2-1.0-0.dll',
    'libpangowin32-1.0-0.dll',
    'libatk-1.0-0.dll',
]

for dll in required_dlls:
    dll_path = None

    for p in required_dll_search_paths:
        p = os.path.join(p, dll)
        if os.path.isfile(p):
            dll_path = p
            break

    common_include_files.append((dll_path, dll))

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
    fullpath = os.path.join(sys.prefix, subpath)
    common_include_files.append((fullpath, subpath))

setup(
    name="Nicotine+",
    author="Nicotine+ Team",
    version="0.1",
    description="dummy",
    options={
        "build_exe": dict(
            build_exe="dist/Nicotine+",
            packages=["gi"],
            includes=["gi"],
            excludes=["lib2to3", "pygtkcompat", "tkinter"],
            include_files=common_include_files,
        ),
    },
    executables=[
        Executable(
            script="nicotine",
            targetName="Nicotine+.exe",
            base="Win32GUI",
        )
    ],
)
