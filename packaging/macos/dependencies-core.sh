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
curl -L https://bintray.com/homebrew/bottles/download_file?file_path=gdk-pixbuf-2.42.6.mojave.bottle.tar.gz -o gdk-pixbuf-2.42.6.mojave.bottle.tar.gz
curl -L https://bintray.com/homebrew/bottles/download_file?file_path=glib-2.68.0.mojave.bottle.tar.gz -o glib-2.68.0.mojave.bottle.tar.gz
curl -L https://bintray.com/homebrew/bottles/download_file?file_path=gtk%2B3-3.24.29.mojave.bottle.tar.gz -o gtk+3-3.24.29.mojave.bottle.tar.gz
curl -L https://bintray.com/homebrew/bottles/download_file?file_path=pango-1.48.4.mojave.bottle.tar.gz -o pango-1.48.4.mojave.bottle.tar.gz
curl -L https://bintray.com/homebrew/bottles/download_file?file_path=python%403.9-3.9.4.mojave.bottle.tar.gz -o python@3.9-3.9.4.mojave.bottle.tar.gz

brew uninstall --ignore-dependencies gdk-pixbuf
brew uninstall --ignore-dependencies glib
brew uninstall --ignore-dependencies gtk+3
brew uninstall --ignore-dependencies pango
brew uninstall --ignore-dependencies python3
brew cleanup -s python3

brew install -f \
  gdk-pixbuf-2.42.6.mojave.bottle.tar.gz \
  glib-2.68.0.mojave.bottle.tar.gz \
  gtk+3-3.24.29.mojave.bottle.tar.gz \
  pango-1.48.4.mojave.bottle.tar.gz \
  python@3.9-3.9.4.mojave.bottle.tar.gz \
  adwaita-icon-theme \
  flake8

brew unlink gdk-pixbuf && brew link --force --overwrite gdk-pixbuf
brew unlink glib && brew link --force --overwrite glib
brew unlink gtk+3 && brew link --force --overwrite gtk+3
brew unlink pango && brew link --force --overwrite pango
brew unlink python3 && brew link --force --overwrite python3

# Install dependencies with pip
pip3 install \
  pep8-naming \
  pygobject \
  pytest
