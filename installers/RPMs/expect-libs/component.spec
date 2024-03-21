%define _build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Name: awips2-expect-libs
Summary: AWIPS II expect-libs 32-bit
Version: 5.45
Release: 1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: i686
URL: https://core.tcl-lang.org/expect/index
License: Public Domain
Distribution: N/A
Vendor: ${_build_vendor}
Packager: %{_build_site}

AutoReq: no
BuildRequires: tcl-devel
BuildRequires: libtcl8.6.so
BuildRequires: /usr/lib/libtclstub8.6.a
Requires: tcl
Provides: libexpect%{version}.so

%description
Provides 32-bit Expect shared library and header files.

%prep
if [ "%{_build_root}" = "" ]; then
    echo "ERROR: A BuildRoot has not been specified."
    echo "FATAL: Unable to Continue ... Terminating."
    exit 1
fi
rm --recursive --force "%{_build_root}"

mkdir --parents "%{_build_loc}"

%build
pushd "%{_build_loc}" || exit 1
tar xf "%{_baseline_workspace}/foss/expect-libs-%{version}/packaged/expect%{version}.tar.gz"
cd expect%{version}
CFLAGS="-m32 -march=i686" ./configure || exit 1
make || exit 1
popd

%install
pushd "%{_build_loc}"/expect%{version}
mkdir --parents "%{_build_root}"/usr/{include,lib}
cp -a libexpect%{version}.so "%{_build_root}"/usr/lib/
cp -a expect.h "%{_build_root}"/usr/include/
cp -a expect_comm.h "%{_build_root}"/usr/include/
cp -a expect_tcl.h "%{_build_root}"/usr/include/
cp -a tcldbg.h "%{_build_root}"/usr/include/
popd

%clean
rm --recursive --force "%{_build_loc}"
rm --recursive --force ${RPM_BUILD_ROOT}

%files
%defattr(755,root,root,755)
/usr/lib/libexpect%{version}.so
%defattr(644,root,root,755)
/usr/include/expect.h
/usr/include/expect_comm.h
/usr/include/expect_tcl.h
/usr/include/tcldbg.h
