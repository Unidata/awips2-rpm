%define _build_arch %(uname -i)

Name: awips2-g2c
Summary: AWIPS II g2c library distribution
Version: 3.4.6
Release: 1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: https://gcc.gnu.org/gcc-3.4
License: GPLv2+ and GPLv2+ with exceptions
Distribution: N/A
Vendor: ${_build_vendor}
Packager: %{_build_site}

AutoReq: no
Provides: libg2c.so.0

%description
AWIPS II g2c library distribution

%prep
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm --recursive --force %{_build_root}
mkdir --parents %{_build_root} || exit 1

%build

%install

docdir="%{_build_root}/usr/share/doc/compat-libf2c-34-%{version}/"
libdir="%{_build_root}/%{_libdir}/"
mkdir --parents "${docdir}"
cp --archive "%{_baseline_workspace}"/foss/g2c-%{version}/doc/* "${docdir}"
mkdir --parents "${libdir}"
cp --archive "%{_baseline_workspace}"/foss/g2c-%{version}/%{_build_arch}/* "${libdir}"

%clean
rm --recursive --force %{_build_root}

%files
%defattr(755,root,root,755)
%{_libdir}/libg2c.so
%{_libdir}/libg2c.so.0
%{_libdir}/libg2c.so.0.0.0
%defattr(644,root,root,755)
/usr/share/doc/compat-libf2c-34-%{version}/COPYING
/usr/share/doc/compat-libf2c-34-%{version}/COPYING.LIB
