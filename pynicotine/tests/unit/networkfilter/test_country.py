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

import os
import shutil

from unittest import TestCase

from pynicotine.config import config
from pynicotine.core import core

DATA_FOLDER_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp_data")


class CountryTest(TestCase):

    def setUp(self):

        config.data_folder_path = DATA_FOLDER_PATH
        config.config_file_path = os.path.join(DATA_FOLDER_PATH, "temp_config")

        core.init_components(enabled_components={"network_filter"})

    def tearDown(self):
        core.quit()
        self.assertIsNone(core.network_filter)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(DATA_FOLDER_PATH)

    def test_read_ip_country(self):
        """Test reading country codes at IP range boundaries."""

        for ip_address, country_code in (
            ("0.255.255.255", ""),
            ("1.0.0.0", "US"),
            ("1.0.0.255", "US"),
            ("1.0.1.0", "CN"),
            ("9.255.255.255", "US"),
            ("10.0.0.0", ""),
            ("13.255.255.255", "US"),
            ("14.0.0.0", "CN")
        ):
            self.assertEqual(core.network_filter.get_country_code(ip_address), country_code)

    def test_read_invalid_ip(self):
        """Test reading country codes of invalid IP addresses."""

        for ip_address, country_code in (
            ("0.0.0.0.0", ""),
            ("invalid_ip", ""),
            (None, "")
        ):
            self.assertEqual(core.network_filter.get_country_code(ip_address), country_code)
