#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2020-2025 Nicotine+ Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

import glob
import os
import subprocess
import sys

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
NOICU_PATH = os.path.join(CURRENT_PATH, "noicu.yaml")


def install_conda_forge():
    """Install dependencies from the main conda-forge repos."""

    subprocess.check_call(["conda", "install", "-y", "rattler-build"])
    subprocess.check_call(["rattler-build", "build", "--recipe", NOICU_PATH])

    for file_path in glob.glob(os.path.join("output", "**", "noicu*.conda"), recursive=True):
        subprocess.check_call(["conda", "install", "-y", file_path])

    pre_packages = ["libsqlite",
                    "libxml2"]

    subprocess.check_call(["conda", "install", "-y"] + pre_packages)
    subprocess.check_call(["conda", "install", "-y", "--no-deps", "harfbuzz"])

    packages = ["cx_freeze",
                "gobject-introspection",
                "gtk4",
                "libadwaita",
                "pygobject",
                "python-build"]

    subprocess.check_call(["conda", "install", "-y", "--freeze-installed"] + packages)
    subprocess.check_call(["conda", "remove", "-y", "noicu"])


if __name__ == "__main__":
    install_conda_forge()
