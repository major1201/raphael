%if 0%{?rhel} == 7
 %define dist .el7
%endif

Name:           raphael
Version:        0.1.0
Release:        1%{?dist}
Summary:        an OpenLDAP management system

License:        MIT
URL:            https://github.com/major1201/raphael
Source0:        raphael-0.1.0.tar.gz

BuildRequires:  python34,python34-devel,python34-pip,chrpath
Requires:       python34

%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

%description
An OpenLDAP management system. This package is built by @major1201.


%prep
%setup -T -b 0


%build


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}/opt/%{name} %{buildroot}/var/log/%{name} %{buildroot}/etc/%{name}
cp -r * %{buildroot}/opt/%{name}

# copy config files
cp {uwsgi.ini,config.yml} %{buildroot}/etc/%{name}/
rm -f %{buildroot}/opt/%{name}/{uwsgi.ini,config.yml} %{buildroot}/opt/%{name}/scripts/%{name}.spec

install -p -D -m 0644 %{buildroot}/opt/%{name}/scripts/%{name}.service %{buildroot}%{_unitdir}/%{name}.service

# remove rpath from build
chrpath -d %{buildroot}/opt/%{name}/venv/bin/uwsgi

%clean
rm -rf $RPM_BUILD_ROOT


%pre


%post
/usr/bin/systemctl daemon-reload


%preun
%systemd_preun %{name}.service


%postun
%systemd_postun %{name}.service


%files
%defattr(-,root,root)
%config(noreplace) /etc/%{name}/config.yml
%config(noreplace) /etc/%{name}/uwsgi.ini
/opt/%{name}/*
%{_unitdir}/%{name}.service
/var/log
