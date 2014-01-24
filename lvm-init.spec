Name:           lvm-init
Version:        0.1
Release:        1
Summary:        LVM init scripts for Mozilla Releng AWS instances

Group:          System Environment/Base
License:        MPL

Source0:        lvm-init-%{version}.tar.gz
BuildArch:      noarch
BuildRoot:      %{_tmppath}

Requires: lvm2
Requires: util-linux-ng
Requires: chkconfig


%description
lvm-init is a script for LVM setup used by Mozilla Releng.

%prep
%setup -q -n %{name}-%{version}


%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/lvm-init

install -m0755 -D lvm-init.py $RPM_BUILD_ROOT/sbin/lvm-init
install -m0755 -D init.d $RPM_BUILD_ROOT/%{_initddir}/lvm-init


%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{_initrddir}/lvm-init

%preun
/sbin/chkconfig --del lvm-init || :

%files

/sbin/lvm-init
%dir %{_sysconfdir}/lvm-init
%attr(0755, root, root) %{_initddir}/lvm-init


%changelog
* Fri Jan 24 2014 Rail Aliiev <rail@mozilla.com>
- first packaging
