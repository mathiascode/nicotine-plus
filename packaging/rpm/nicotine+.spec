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

%install
pip3 install . --root=$RPM_BUILD_ROOT

%files
%{_bindir}/%{short_name}
%{_datadir}/applications/%{application_id}.desktop
%{_datadir}/icons/hicolor/*/apps/%{application_id}*.*
%{_datadir}/icons/hicolor/*/intl/*.*
%{_datadir}/icons/hicolor/*/status/*.*
%{_metainfodir}/%{application_id}.appdata.xml
%{_mandir}/man1/%{short_name}.1.*
%{python3_sitelib}/pynicotine/
%{python3_sitelib}/%{python_name}-*.dist-info/
