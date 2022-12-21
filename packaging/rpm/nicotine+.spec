Name: nicotine+
Version: 3.3.0.dev4
Release: 1
Summary: Graphical client for the Soulseek peer-to-peer network

License: GPLv3+ and CC-BY-SA and MIT
URL: https://nicotine-plus.org/
Source0: nicotine-plus-%{version}.tar.gz

BuildArch: noarch
Requires: gspell
Requires: (gtk4 >= 4.6.6 or gtk3 >= 3.22.30)
Requires: python >= 3.6
Requires: python3-gobject

%description
Nicotine+ is a graphical client for the Soulseek peer-to-peer
network.

Nicotine+ aims to be a pleasant, free and open source (FOSS)
alternative to the official Soulseek client, providing additional
functionality while keeping current with the Soulseek protocol.

%install
pip3 install --verbose --no-build-isolation --no-deps --no-index --root=%{buildroot} --prefix=/usr %{SOURCE0}

%files
/usr/*
