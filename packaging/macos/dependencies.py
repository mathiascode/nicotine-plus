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


def install_brew():
    """Install dependencies from the main Homebrew repos."""

    gtk_version = os.environ.get("NICOTINE_GTK_VERSION", "4")
    use_libadwaita = (gtk_version == "4" and os.environ.get("NICOTINE_LIBADWAITA") == "1")

    packages = ["adwaita-icon-theme",
                "gettext",
                "gobject-introspection",
                f"gtk+{gtk_version}",
                "pipx"]

    if gtk_version == "3":
        packages.append("gspell")

    if use_libadwaita:
        packages.append("libadwaita")

    subprocess.check_call(["brew", "install"] + packages)


def install_pypi():
    """Install dependencies from PyPi."""

    packages = ["build",
                "git+https://github.com/marcelotduarte/cx_Freeze",
                ".[packaging,tests]"]

    subprocess.check_call(
        ["pipx", "install", "--no-binary", ":all:"] + packages)


if __name__ == "__main__":
    install_brew()
    install_pypi()
