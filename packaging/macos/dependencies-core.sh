#!/bin/sh

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

### This script is used to install core dependencies in Homebrew ###

# Install dependencies from the main Homebrew repos
curl -L https://bintray.com/homebrew/bottles/download_file?file_path=adwaita-icon-theme-3.38.0.mojave.bottle.tar.gz -o adwaita-icon-theme.bottle.tar.gz
curl -L https://bintray.com/homebrew/bottles/download_file?file_path=gtk%2B3-3.24.29.mojave.bottle.tar.gz -o gtk+3.bottle.tar.gz
curl -L https://bintray.com/homebrew/bottles/download_file?file_path=pygobject3-3.40.1.mojave.bottle.tar.gz -o pygobject3.bottle.tar.gz
curl -L https://bintray.com/homebrew/bottles/download_file?file_path=python%403.9-3.9.4.mojave.bottle.tar.gz -o python3.bottle.tar.gz
ls
brew install -f \
  adwaita-icon-theme.bottle.tar.gz \
  flake8 \
  gtk+3.bottle.tar.gz \
  pygobject3.bottle.tar.gz \
  python3.bottle.tar.gz

# Install dependencies with pip
pip3 install \
  pep8-naming \
  pytest
