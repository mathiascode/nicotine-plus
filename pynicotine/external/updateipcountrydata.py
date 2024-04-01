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
import struct
import urllib.request
import zipfile


COUNTRY_DB_URL = "https://download.ip2location.com/lite/IP2LOCATION-LITE-DB1.CSV.ZIP"
FILE_PATH, _HEADERS = urllib.request.urlretrieve(COUNTRY_DB_URL)
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

output = bytearray(b"""# IP2Location LITE (c) 2001-2024 Hexasoft Development Sdn. Bhd.

# IP2Location LITE is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.

# You should have received a copy of the license along with this
# work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>.

""")
country_codes = set()
addresses = []
countries = []

with zipfile.ZipFile(FILE_PATH, "r") as zip_file_handle:
    with zip_file_handle.open(zip_file_handle.namelist()[-1]) as csv_file_handle:
        for row in csv.reader(io.TextIOWrapper(csv_file_handle)):
            _address_from, address_to, country_code, _country_name = list(row)
            address_to = int(address_to)
            country_code = str(country_code)

            if len(country_code) != 2 and country_code != "-":
                raise ValueError("Invalid country code")

            if address_to > 4294967295:
                raise ValueError("Invalid IP address")

            country_codes.add(country_code)
            addresses.append(address_to)
            countries.append(country_code)

output.extend(b"# Country code mapping\n")

for country_code in sorted(country_codes):
    output.extend(f'{country_code.replace("-", "_")},'.encode("utf-8"))

output.extend(b" = ")

for country_code in sorted(country_codes):
    output.extend(f'"{country_code}",'.encode("utf-8"))

output.extend(b"\n\n# IP ranges\n")
output.extend(b"addresses = (")

for address in addresses:
    output.extend(f"{address},".encode("utf-8"))

output.extend(b")\n\n")
output.extend(b"# Country codes for IP ranges\n")
output.extend(b"countries = (")

for country_code in countries:
    output.extend(f'{country_code.replace("-", "_")},'.encode("utf-8"))

output.extend(b")\n\n")

with open(os.path.join(CURRENT_PATH, "ipcountrydata.py"), "wb") as file_handle:
    file_handle.write(output)
