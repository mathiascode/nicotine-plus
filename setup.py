#!/usr/bin/env python3
# COPYRIGHT (C) 2020-2021 Nicotine+ Team
# COPYRIGHT (C) 2016-2017 Michael Labouebe <gfarmerfr@free.fr>
# COPYRIGHT (C) 2009-2010 Quinox <quinox@users.sf.net>
# COPYRIGHT (C) 2009 Hedonist <ak@sensi.org>
# COPYRIGHT (C) 2006-2009 Daelstorm <daelstorm@gmail.com>
# COPYRIGHT (C) 2008-2009 eL_vErDe <gandalf@le-vert.net>
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

"""
To install Nicotine+ on a GNU/Linux distribution, run:
    pip3 install .
"""

import glob
import os
import pynicotine

from distutils.core import setup
from distutils.cmd import Command
from pkgutil import walk_packages

from pynicotine.config import config


class UpdatePot(Command):

    description = 'update .pot translation template'
    user_options = []

    def initialize_options(self):
        # Not used
        pass

    def finalize_options(self):
        # Not used
        pass

    def run(self):

        files = glob.glob("files/**/*.in", recursive=True) + \
            glob.glob("pynicotine/**/*.py", recursive=True) + \
            glob.glob("pynicotine/**/*.ui", recursive=True)

        os.system("xgettext -L Python -o po/nicotine.pot nicotine")
        os.system("xgettext --join-existing -o po/nicotine.pot " + " ".join(files))


def generate_translations():

    packages = []
    package_data = {}

    for po_file in glob.glob("po/*.po"):
        lang = os.path.basename(po_file[:-3])
        package = "pynicotine.locale." + lang + ".LC_MESSAGES"

        mo_dir = os.path.join("pynicotine", "locale", lang, "LC_MESSAGES")
        mo_file = os.path.join(mo_dir, "nicotine.mo")

        if not os.path.exists(mo_dir):
            os.makedirs(mo_dir)

        os.system("msgfmt " + po_file + " -o " + mo_file)

        packages.append(package)
        package_data[package] = ["*.mo"]

    # Merge translations into .desktop and metainfo files
    for desktop_file in glob.glob("files/*.desktop.in"):
        os.system("msgfmt --desktop --template=" + desktop_file + " -d po -o " + desktop_file[:-3])

    for metainfo_file in glob.glob("files/*.metainfo.xml.in"):
        os.system("msgfmt --xml --template=" + metainfo_file + " -d po -o " + metainfo_file[:-3])

    return packages, package_data


if __name__ == '__main__':

    LONG_DESCRIPTION = """Nicotine+ is a graphical client for the Soulseek peer-to-peer
file sharing network.

Nicotine+ aims to be a pleasant, Free and Open Source (FOSS)
alternative to the official Soulseek client, providing additional
functionality while keeping current with the Soulseek protocol."""

    L10N_PACKAGES, L10N_PACKAGE_DATA = generate_translations()
    PACKAGES = ["pynicotine"] + [name for importer, name, ispkg in walk_packages(path=pynicotine.__path__, prefix="pynicotine.") if ispkg] + L10N_PACKAGES
    PACKAGE_DATA = {**dict((package, ["*.bin", "*.md", "*.py", "*.svg", "*.ui", "PLUGININFO"]) for package in PACKAGES), **L10N_PACKAGE_DATA}

    SCRIPTS = ["nicotine"]

    DATA_FILES = [
        ("share/applications", glob.glob("files/*.desktop")),
        ("share/metainfo", glob.glob("files/*.metainfo.xml")),
        ("share/icons/hicolor/scalable/apps", glob.glob("pynicotine/gtkgui/icons/hicolor/scalable/apps/*.svg")),
        ("share/icons/hicolor/symbolic/apps", glob.glob("pynicotine/gtkgui/icons/hicolor/symbolic/apps/*.svg")),
        ("share/doc/nicotine", glob.glob("[!404.md]*.md") + glob.glob("doc/*.md") + ["COPYING"]),
        ("share/man/man1", glob.glob("files/*.1"))
    ]

    setup(
        name="nicotine-plus",
        version=config.version,
        license="GPLv3+",
        description="Graphical client for the Soulseek file sharing network",
        long_description=LONG_DESCRIPTION,
        author="Nicotine+ Team",
        author_email="nicotine-team@lists.launchpad.net",
        url="https://nicotine-plus.org/",
        platforms="any",
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        scripts=SCRIPTS,
        data_files=DATA_FILES,
        python_requires=">=3.5",
        install_requires=["PyGObject>=3.18"],
        cmdclass={"update_pot": UpdatePot}
    )
