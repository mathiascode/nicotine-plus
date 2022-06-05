%global application_id org.nicotine_plus.Nicotine
%global python_name nicotine-plus
%global short_name nicotine

Name: nicotine+
Version: 3.3.0.dev1
Release: 1%{?dist}
Summary: Graphical client for the Soulseek peer-to-peer network

License: GPLv3+ and CC-BY-SA and MIT
URL: https://nicotine-plus.org/
Source0: %{python_name}-%{version}.tar.gz

BuildArch: noarch
BuildRequires:  gettext
BuildRequires:  gtk3
BuildRequires:  python3-devel
BuildRequires:  python3-gobject
BuildRequires:  python3-pytest-xvfb
BuildRequires:  python3-wheel

Requires:       gdbm
Requires:       gspell
Requires:       gtk3
Requires:       libappindicator-gtk3
Requires:       python3-gobject

%description
Nicotine+ is a graphical client for the Soulseek peer-to-peer
network.

Nicotine+ aims to be a pleasant, free and open source (FOSS)
alternative to the official Soulseek client, providing additional
functionality while keeping current with the Soulseek protocol.

%prep
%autosetup -n %{python_name}-%{version}

%generate_buildrequires
%pyproject_buildrequires -r

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files pynicotine
%find_lang %{short_name}

%check
%pytest

%files -f %{pyproject_files} -f %{short_name}.lang
%license COPYING
%{_bindir}/%{short_name}
%{_datadir}/applications/%{application_id}.desktop
%{_datadir}/icons/hicolor/*/apps/%{application_id}*.*
%{_datadir}/icons/hicolor/*/intl/*.*
%{_datadir}/icons/hicolor/*/status/*.*
%{_defaultdocdir}/%{short_name}/*
%{_metainfodir}/%{application_id}.appdata.xml
%{_mandir}/man1/%{short_name}.1.*