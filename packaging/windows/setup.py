import os
import sys
from cx_Freeze import setup, Executable


common_include_files = []

required_gi_namespaces = [
    "Gtk-3.0",
    "Gdk-3.0",
    "Pango-1.0",
    "GObject-2.0",
    "GLib-2.0",
    "Gio-2.0",
    "GdkPixbuf-2.0",
]

for ns in required_gi_namespaces:
    subpath = "lib/girepository-1.0/{}.typelib".format(ns)
    fullpath = os.path.join(sys.prefix, subpath)
    assert os.path.isfile(fullpath), (
        "Required file {} is missing" .format(
            fullpath,
        ))
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
