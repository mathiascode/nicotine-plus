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

import platform
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
                f"gtk+{gtk_version}"]

    if gtk_version == "3":
        packages.append("gspell")

    if use_libadwaita:
        packages.append("libadwaita")

    bottle_tag = "monterey"

    if platform.machine() == "arm64":
        bottle_tag = f"arm64_{bottle_tag}"

    cached_packages = []

    output = subprocess.check_output(["brew", "fetch", "--force", f"--bottle-tag={bottle_tag}"] + packages)

    for line in output.split(b"\n"):
        if line.startswith(b"Downloaded to: "):
            cached_packages.append(line.replace(b"Downloaded to: ", b""))

    subprocess.check_call(["brew", "install"] + cached_packages)


def install_pypi():
    """Install dependencies from PyPi."""

    subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-binary", ":all:",
                           "-e", ".[packaging,tests]", "build"])


if __name__ == "__main__":
    install_brew()
    install_pypi()
