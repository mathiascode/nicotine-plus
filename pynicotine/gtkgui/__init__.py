# COPYRIGHT (C) 2021 Nicotine+ Team
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


def check_gui_dependencies():

    if os.getenv("NICOTINE_GTK_VERSION") == '4':
        gtk_version = (4, 4, 0)
        pygobject_version = (3, 40, 0)
    else:
        gtk_version = pygobject_version = (3, 18, 0)

    import gi
    gi.check_version(pygobject_version)

    api_version = (gtk_version[0], 0)
    gi.require_version('Gtk', '.'.join(map(str, api_version)))

    from gi.repository import Gtk

    if Gtk.check_version(*gtk_version):
        return _("You are using an unsupported version of GTK %(major_version)s. You should install "
                 "GTK %(complete_version)s or newer.") % {
            "major_version": gtk_version[0],
            "complete_version": '.'.join(map(str, gtk_version))}

    return None


def run_gui(network_processor, trayicon, hidden, bindip, port, ci_mode, multi_instance):
    """ Run Nicotine+ GTK GUI """

    error = check_gui_dependencies()

    if error:
        print(error)
        return 1

    from pynicotine.gtkgui.frame import Application
    return Application(network_processor, trayicon, hidden, bindip, port, ci_mode, multi_instance).run()
