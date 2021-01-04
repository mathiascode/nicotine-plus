# COPYRIGHT (C) 2020 Nicotine+ Team
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

from pynicotine.gtkgui.utils import human_size
from pynicotine.gtkgui.utils import load_ui_elements


class Statistics:

    def __init__(self, frame):

        self.frame = frame

        load_ui_elements(self, os.path.join(self.frame.gui_dir, "ui", "dialogs", "statistics.ui"))

        self.StatisticsDialog.set_transient_for(frame.MainWindow)

        self.StatisticsDialog.connect("destroy", self.hide)
        self.StatisticsDialog.connect("destroy-event", self.hide)
        self.StatisticsDialog.connect("delete-event", self.hide)
        self.StatisticsDialog.connect("delete_event", self.hide)

        self.append_downloaded_files(0)
        self.append_downloaded_size(0)
        self.append_uploaded_files(0)
        self.append_uploaded_size(0)

    def append_downloaded_files(self, session_value):

        total_value = self.frame.np.config.sections["statistics"]["downloaded_files"]

        self.downloaded_files_session.set_text(str(session_value))
        self.downloaded_files_total.set_text(str(total_value))

    def append_downloaded_size(self, session_value):

        total_value = self.frame.np.config.sections["statistics"]["downloaded_size"]

        self.downloaded_size_session.set_text(human_size(session_value))
        self.downloaded_size_total.set_text(human_size(total_value))

    def append_uploaded_files(self, session_value):

        total_value = self.frame.np.config.sections["statistics"]["uploaded_files"]

        self.uploaded_files_session.set_text(str(session_value))
        self.uploaded_files_total.set_text(str(total_value))

    def append_uploaded_size(self, session_value):

        total_value = self.frame.np.config.sections["statistics"]["uploaded_size"]

        self.uploaded_size_session.set_text(human_size(session_value))
        self.uploaded_size_total.set_text(human_size(total_value))

    def on_clear_statistics(self, *args):
        self.frame.np.statistics.clear_stats()

    def hide(self, w=None, event=None):
        self.StatisticsDialog.hide()
        return True

    def show(self):
        self.StatisticsDialog.show()
