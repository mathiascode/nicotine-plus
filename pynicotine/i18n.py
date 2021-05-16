# COPYRIGHT (C) 2020-2021 Nicotine+ Team
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

import gettext
import locale
import os
import sys


def apply_translation():
    """ Enables translations by telling gettext where to locate them. """

    # Package name for gettext
    package = 'nicotine'

    # Local path where to find translation (mo) files
    local_mo_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'locale')

    if not gettext.find(package, localedir=local_mo_path):
        # Locales are not in the current dir, fall back to system dir
        gettext.install(package)
        return

    # Locales are in the current dir, use them
    gettext.install(package, local_mo_path)
