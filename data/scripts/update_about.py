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

import os

BASE_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", ".."))
HEADING_PREFIX = "# "
SUBHEADING_PREFIX = "### "
LIST_ITEM_PREFIX = " - "
URL_START_CHAR = "["
URL_MIDDLE_CHARS = "]("
URL_END_CHAR = ")"


def format_line(line):

    url_start = line.find(URL_START_CHAR)
    url_middle = line.find(URL_MIDDLE_CHARS, url_start)
    url_end = line.find(URL_END_CHAR, url_middle)

    if url_start > -1 and url_middle > -1 and url_end > -1:
        url = line[url_middle + len(URL_MIDDLE_CHARS):url_end]
        label = line[url_start + len(URL_START_CHAR):url_middle]

        line = line.replace(line[url_start:url_end], f'<a href="{url}">{label}</a>')

    return line.replace(LIST_ITEM_PREFIX, " •  ").strip()


def parse_md_file(basename, list_name, ignored_sections=None):

    output = ""
    sections = {}

    with open(os.path.join(BASE_PATH, basename), "r", encoding="utf-8") as file_handle:
        for line in file_handle:
            if line.startswith(HEADING_PREFIX):
                heading = line.replace(HEADING_PREFIX, "").strip()
                subheading = None
                sections[heading] = {}

            elif line.startswith(SUBHEADING_PREFIX):
                subheading = line.replace(SUBHEADING_PREFIX, "").strip()
                sections[heading][subheading] = f"<b>{subheading}</b>"

            elif line.strip() and subheading is not None:
                sections[heading][subheading] += f"\n{format_line(line)}"

    for heading, subsections in sections.items():
        if ignored_sections and heading in ignored_sections:
            continue

        if not output:
            output += f"    {list_name} = ["
            output += f'\n    "<b>{heading}</b>"'
        else:
            output += f',\n\n\n    "\n<b>{heading}</b>"'

        for section_output in subsections.values():
            output += f',\n\n    """{section_output}"""'

    output += "]"
    print(output)
    return output


def update_about():

    authors_output = parse_md_file(
        "AUTHORS.md", list_name="AUTHORS", ignored_sections={"Third-Party Attributions"}
    )
    translators_output = parse_md_file(
        "TRANSLATORS.md", list_name="TRANSLATORS"
    )
    license_output = parse_md_file(
        "AUTHORS.md", list_name="LICENSE",
        ignored_sections={
            "Nicotine+ Team", "Nicotine+ Team (Inactive)", "Nicotine Team",
            "PySoulSeek Contributors"
        }
    )


if __name__ == "__main__":
    update_about()
