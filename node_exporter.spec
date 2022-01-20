%define debug_package %{nil}

# Don't strip any binary files
%define __os_install_post %{nil}

# Ignore missing build ids
%global _missing_build_ids_terminate_build 0

%global app_name   node_exporter

%global process_user   %{app_name}

Name:          cl-%{app_name}
Version:       1.2.2
Release:       5%{?dist}
Summary:       Prometheus Exporter for machine metrics
License:       APL 2.0
URL:           https://github.com/prometheus/%{app_name}
BugURL:        https://github.com/schmidtw/test-rpmbuild
ExclusiveArch: x86_64

Source0: %{url}/releases/download/v%{version}/%{app_name}-%{version}.linux-amd64.tar.gz
Source1: %{app_name}.service

BuildRequires:     curl
%if 0%{?fedora} > 29 || 0%{?rhel} >= 8
BuildRequires:     systemd-rpm-macros
%{?systemd_requires}
%else
BuildRequires:     systemd
%endif

Requires(pre):     shadow-utils
Requires(post):    systemd
Requires(preun):   systemd
Requires(postun):  systemd
Requires(postun):  shadow-utils

Provides: %{app_name} = %{version}

%description
Exporter for machine metrics

%prep
pushd %{_sourcedir}
curl -s -L %{url}/releases/download/v%{version}/sha256sums.txt | grep "linux-amd64" | sha256sum -c -
popd
%setup -n %{app_name}-%{version}.linux-amd64

%pre
id %{process_user} >/dev/null 2>&1
if [ $? != 0 ]; then
    %{_sbindir}/groupadd -r %{process_user} >/dev/null 2>&1
    %{_sbindir}/useradd -d /var/run/%{process_user} -r -g %{process_user} %{process_user} >/dev/null 2>&1
fi

%post
%systemd_post %{app_name}.service

%preun
%systemd_preun %{app_name}.service

%postun
%systemd_postun_with_restart %{app_name}.service

# Do not remove the user if this is not an uninstall
if [ $1 = 0 ]; then
    %{_sbindir}/userdel -r %{process_user} >/dev/null 2>&1
    %{_sbindir}/groupdel %{process_user} >/dev/null 2>&1
    # Ignore errors from above
    true
fi

%install
%{__install} -p -D %{app_name} %{buildroot}%{_bindir}/%{app_name}
%{__install} -p -D %{SOURCE1}  %{buildroot}%{_unitdir}/%{app_name}.service


%files
%defattr(644, root, root, 755)
%doc LICENSE NOTICE

%attr(755, root, root) %{_bindir}/%{app_name}

%{_unitdir}/%{app_name}.service

%changelog
* Thu Dec 09 2021 Weston Schmidt <weston_schmidt@comcast.com> - 1.2.2-5
- Testing
