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

### This script is used to install core dependencies in Nix ###
### These are enough to run unit tests and use non-UI code ###

# Install dependencies from the Nix repos
nix-env -iA \
  nixpkgs.python39Packages.flake8
  nixpkgs.python39Packages.pep8-naming
  nixpkgs.python39Packages.pytest
