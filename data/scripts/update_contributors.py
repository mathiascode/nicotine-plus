#!/usr/bin/env python3
# COPYRIGHT (C) 2024 Nicotine+ Contributors
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

import glob
import os
import subprocess


def update_contributors():
    """Update .pot translation template."""

    duplicates = {
        "Adam Cecile",
        "Adam Cécile (Le_Vert)",
        "Anonymous",
        "droserasprout",
        "Han",
        "Hosted Weblate",
        "Kip",
        "Mat",
        "Mathias",
        "Michael Laboube",
        "Nick",
        "OpenAI",
        "Toine",
        "Weblate (bot)",
    }

    non_git = {
        "(._.)",
        "Airn Here",
        "Alexey Vyskubov",
        "Amun-Ra",
        "Aubin Paul",
        "blueboy",
        "Brett W. Thompson",
        "Christian Swinehart",
        "dbazza",
        "Dreslo",
        "Felipe Nogaroto Gonzalez",
        "Geert Kloosterman",
        "Gustavo J. A. M. Carneiro",
        "hednod",
        "heni",
        "infinito",
        "INMCM",
        "Joe Halliwell",
        "Jozef Říha",
        "Josselin Mouette",
        "Julen",
        "Julien Wajsberg",
        "Kari Viittanen",
        "Kenny Verstraete",
        "lee8oi",
        "lippel"
        "ManWell",
        "Markus Magnuson",
        "mathsped",
        "Meokater",
        "nicola",
        "Nils",
        "Nir Arbel",
        "sierracat",
        "Silvio Orta",
        "SmackleFunky",
        "stillbirth",
        "suser-guru",
        "systr",
        "thine",
        "(va)\*10^3",
        "vasi",
        "Wojciech Owczarek",
        "Wretched",
        "Žygimantas Beručka"
    }

    git = set(subprocess.check_output(["git", "log", "--format=%an"]).decode().split("\n"))

    print(sorted(non_git.union(git) - duplicates, key=str.casefold))


if __name__ == "__main__":
    update_contributors()
