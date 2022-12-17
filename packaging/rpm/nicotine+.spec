%global application_id org.nicotine_plus.Nicotine
%global python_name nicotine-plus
%global short_name nicotine

Name: nicotine+
Version: 3.3.0.dev4
Release: 1%{?dist}
Summary: Graphical client for the Soulseek peer-to-peer network

License: GPLv3+ and CC-BY-SA and MIT
URL: https://nicotine-plus.org/
Source0: %{python_name}-%{version}.tar.gz

BuildArch: noarch

Requires:       gspell
Requires:       (gtk4 or gtk3)
Requires:       python3-gobject

%description
Nicotine+ is a graphical client for the Soulseek peer-to-peer
network.

Nicotine+ aims to be a pleasant, free and open source (FOSS)
alternative to the official Soulseek client, providing additional
functionality while keeping current with the Soulseek protocol.

%prep
%autosetup -n %{python_name}-%{version}

%build
python3 setup.py build

%install
python3 setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%files -f INSTALLED_FILES
