#!/usr/bin/env python3
# COPYRIGHT (C) 2020-2024 Nicotine+ Contributors
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
import subprocess
import sys


def install_windows():
    """Install dependencies from the main MinGW repos (Windows)."""

    arch = os.environ.get("ARCH", "x86_64")
    prefix = "mingw-w64-clang-aarch64" if arch == "arm64" else "mingw-w64-x86_64"

    packages = [
        f"{prefix}-ca-certificates",
        f"{prefix}-cmake",
        f"{prefix}-toolchain",
        f"{prefix}-gobject-introspection",
        f"{prefix}-gettext-tools",
        f"{prefix}-gtk4",
        f"{prefix}-libadwaita",
        f"{prefix}-webp-pixbuf-loader"
    ]
    subprocess.check_call(["pacman", "--noconfirm", "-S", "--needed"] + packages)


def install_macos():
    """Install dependencies from the main Homebrew repos (macOS)."""

    packages = [
        "gettext",
        "gobject-introspection",
        "glib",
        "gtk4",
        "libadwaita",
        "librsvg"
    ]
    subprocess.check_call(["brew", "install"] + packages)


def install_pypi():
    """Install dependencies from PyPi."""

    os.environ["PIP_CONSTRAINT"] = "packaging/windows/constraints.txt"
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "--no-binary", "cx_Freeze",
        "--no-binary", "PyGObject",
        "--no-binary", "pycairo",
        "-c", "packaging/windows/constraints.txt",
        "-e", ".[packaging,tests]",
        "build",
        "setuptools",
        "wheel"
    ])


if __name__ == "__main__":
    if sys.platform == "win32":
        install_windows()

    elif sys.platform == "darwin":
        install_macos()

    install_pypi()
