# COPYRIGHT (C) 2023 Nicotine+ Contributors
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

output = bytearray()

country_codes = set()
address_values = []
country_values = []

with open("IP2LOCATION-LITE-DB1.CSV", "r") as file_handle:
    csv_reader = csv.reader(file_handle)
    for row in csv_reader:
        _address_from, address_to, country_code, _country_name = list(row)

        country_codes.add(country_code)
        address_values.append(address_to)
        country_values.append(country_code)

for country_code in country_codes:
    output.extend(f'{country_code.replace("-", "_")} = "{country_code}"\n'.encode("utf-8"))

output.extend(b"\n")
output.extend(b"address_values = (")

for address in address_values:
    output.extend(f"{address},".encode("utf-8"))

output.extend(b")\n")
output.extend(b"country_values = (")

for country_value in country_values:
    output.extend(f"{country_value.replace('-', '_')},".encode("utf-8"))

output.extend(b")\n")

with open("ipcountries.py", "wb") as file_handle:
    file_handle.write(output)