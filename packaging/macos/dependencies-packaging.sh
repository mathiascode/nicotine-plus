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

### This script is used to install UI and packaging dependencies in Nix ###

# Install dependencies from the Nix repos
nix-env -iA \
  nixpkgs.cairo \
  nixpkgs.gdk-pixbuf \
  nixpkgs.gtk3-x11 \
  nixpkgs.gnome3.adwaita-icon-theme \
  nixpkgs.python3Packages.certifi \
  nixpkgs.python3Packages.pip

# Install dependencies with pip
pip3 install --user \
  pygobject \
  pyinstaller==4.3
