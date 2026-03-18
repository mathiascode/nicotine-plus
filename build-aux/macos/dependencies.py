#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2020-2025 Nicotine+ Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import subprocess
import sys


def install_conda_forge():
    """Install dependencies from the main conda-forge repos."""

    environment_name = "nicotine-plus"
    pre_packages = ["icu<78.0",
                    "libsqlite"]
    packages = ["icu",
                "cx_freeze==8.6.0",
                "gobject-introspection",
                "gtk4",
                "libadwaita",
                "pygobject",
                "python-build"]

    subprocess.check_call(["mamba", "install", "-n", environment_name, "-y"] + pre_packages)
    subprocess.check_call(["mamba", "install", "-n", environment_name, "-y"] + packages)


if __name__ == "__main__":
    install_conda_forge()
