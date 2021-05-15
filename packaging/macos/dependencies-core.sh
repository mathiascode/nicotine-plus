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
export PATH="$HOME/.new_local/bin:$PATH"

curl https://gitlab.gnome.org/GNOME/gtk-osx/raw/master/gtk-osx-setup.sh -o gtk-osx-setup.sh
chmod +x gtk-osx-setup.sh
./gtk-osx-setup.sh

jhbuild bootstrap
jhbuild bootstrap-gtk-osx
jhbuild build python meta-gtk-osx-bootstrap meta-gtk-osx-gtk3

# Install dependencies with pip
pip3 install --no-cache-dir \
  flake8 \
  pep8-naming \
  pygobject \
  pytest
