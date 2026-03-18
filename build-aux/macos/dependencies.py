#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2020-2025 Nicotine+ Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import subprocess
import sys


def install_conda_forge():
    """Install dependencies from the main conda-forge repos."""

    pre_packages = ["icu==67.1",
                    "libsqlite"]

    subprocess.check_call(["conda", "install", "-y"] + pre_packages)

    packages = ["icu",
                "cx_freeze",
                "gobject-introspection",
                "gtk4",
                "libadwaita",
                "pygobject",
                "python-build"]

    subprocess.check_call(["conda", "install", "-y"] + packages)


if __name__ == "__main__":
    install_conda_forge()
