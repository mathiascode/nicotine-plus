#!/bin/sh

# COPYRIGHT (C) 2020 Nicotine+ Team
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

### This script is used to install UI and packaing dependencies in MinGW ###

# Install dependencies from the main MinGW repos
pacman --noconfirm -S --needed \
  git \
  unzip \
  mingw-w64-$ARCH-gspell \
  mingw-w64-$ARCH-gtk3 \
  mingw-w64-$ARCH-nsis \
  mingw-w64-$ARCH-python-certifi \
  mingw-w64-$ARCH-python-gobject

# Install dependencies with pip
pip3 install \
  plyer

wget https://github.com/pyinstaller/pyinstaller/archive/refs/tags/v4.3.zip
unzip v4.3.zip
cd pyinstaller-4.3/bootloader/

if [ $ARCH == "i686" ]; then
  python3 ./waf all --target-arch=32bit
else
  python3 ./waf all --target-arch=64bit
fi

pip3 install ..
