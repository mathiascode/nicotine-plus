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

import csv
import io
import os
import urllib.request
import zipfile


COUNTRY_DB_URL = "https://download.ip2location.com/lite/IP2LOCATION-LITE-DB1.CSV.ZIP"
FILE_PATH, _HEADERS = urllib.request.urlretrieve(COUNTRY_DB_URL)
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
MAX_IPV4_RANGE = 4294967295


def update_ip_country_data():
    """Dowmload IP2Location country data and convert it for use in Python."""

    output = bytearray(b"""# IP2Location LITE (c) 2001-2024 Hexasoft Development Sdn. Bhd.

    # IP2Location LITE is licensed under a
    # Creative Commons Attribution-ShareAlike 4.0 International License.

    # You should have received a copy of the license along with this
    # work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>.

    """)
    country_codes = set()
    ip_ranges = []
    country_values = []

    with zipfile.ZipFile(FILE_PATH, "r") as zip_file_handle:
        with zip_file_handle.open(zip_file_handle.namelist()[-1]) as csv_file_handle:
            for row in csv.reader(io.TextIOWrapper(csv_file_handle)):
                _address_from, address_to, country_code, _country_name = list(row)
                address_to = int(address_to)
                country_code = str(country_code)

                if len(country_code) != 2 and country_code != "-":
                    raise ValueError("Invalid country code")

                if address_to > MAX_IPV4_RANGE:
                    raise ValueError("Invalid IP address")

                country_codes.add(country_code)
                ip_ranges.append(address_to)
                country_values.append(country_code)

    output.extend(b"# Country code mapping\n")

    for country_code in sorted(country_codes):
        output.extend(f'{country_code.replace("-", "_")},'.encode("utf-8"))

    output.extend(b" = ")

    for country_code in sorted(country_codes):
        output.extend(f'"{country_code.replace("-", "")}",'.encode("utf-8"))

    output.extend(b"\n\n# IP ranges\n")
    output.extend(b"ip_ranges = (")

    for ip_address in ip_ranges:
        output.extend(f"{ip_address},".encode("utf-8"))

    output.extend(b")\n\n")
    output.extend(b"# Country codes for IP ranges\n")
    output.extend(b"country_values = (")

    for country_code in country_values:
        output.extend(f'{country_code.replace("-", "_")},'.encode("utf-8"))

    output.extend(b")\n\n")

    with open(os.path.join(CURRENT_PATH, "data", "ipcountry.py"), "wb") as file_handle:
        file_handle.write(output)


if __name__ == "__main__":
    update_ip_country_data()
