%global _python_bytecompile_extra 0
%define _pgtcl_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _pgtcl_version_short %(echo %{version} | cut -f1,2 -d'.')
%define _build_arch %(uname -i)

#
# AWIPS II Pgtcl Spec File
#

Name: awips2-pgtcl
Summary: AWIPS II Pgtcl Distribution
Version: 2.7.7
Release: 1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: https://flightaware.github.io/Pgtcl
License: N/A
Distribution: N/A
Vendor: ${_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: postgresql
Requires: tcl >= 8.5
BuildRequires: make

%description
AWIPS II Pgtcl Distribution

%prep
# Ensure that a "buildroot" has been specified.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm --recursive --force %{_build_root}
mkdir --parents "%{_build_root}/awips2/pgtcl"
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

if [ -d %{_pgtcl_build_loc} ]; then
   rm --recursive --force %{_pgtcl_build_loc}
fi
mkdir --parents %{_pgtcl_build_loc}

%build
SRC_DIR="%{_baseline_workspace}/foss/pgtcl-%{version}/packaged"
PKG_FILE="Pgtcl-%{version}.tar.gz"
cp --verbose ${SRC_DIR}/${PKG_FILE} %{_pgtcl_build_loc}
pushd . > /dev/null

# Untar the source.
cd %{_pgtcl_build_loc}
tar --extract --gzip --file ${PKG_FILE}

cd Pgtcl-%{version}

autoconf
./configure --prefix="%{_build_root}/awips2/pgtcl" --exec-prefix="%{_build_root}/awips2/pgtcl"
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

make
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

popd > /dev/null

%install
pushd . > /dev/null

#Copy profile.d script
mkdir --parents "%{_build_root}/etc/profile.d"
cp "%{_baseline_workspace}/installers/RPMs/pgtcl/profile.d/"* \
    "%{_build_root}/etc/profile.d"

cd %{_pgtcl_build_loc}/Pgtcl-%{version}

#Perform install
make install

RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

popd > /dev/null

%clean
rm --recursive --force %{_build_root}
rm --recursive --force %{_pgtcl_build_loc}

%files
%defattr(-, awips, fxalpha, 0755)
%dir /awips2/pgtcl

%defattr(644,awips,fxalpha,755)
%dir /awips2/pgtcl/bin
%dir /awips2/pgtcl/share
%doc /awips2/pgtcl/share/man
%doc /awips2/pgtcl/share/man/mann
%doc /awips2/pgtcl/share/man/mann/*
%dir /awips2/pgtcl/include
/awips2/pgtcl/include/pgtclId.h
%dir /awips2/pgtcl/lib
/awips2/pgtcl/lib/libpgtcl.so
%dir /awips2/pgtcl/lib/pgtcl%{_pgtcl_version_short}
/awips2/pgtcl/lib/pgtcl%{_pgtcl_version_short}/libpgtcl%{version}.so
/awips2/pgtcl/lib/pgtcl%{_pgtcl_version_short}/pkgIndex.tcl
/awips2/pgtcl/lib/pgtcl%{_pgtcl_version_short}/postgres-helpers.tcl

%defattr(755,root,root,755)
/etc/profile.d/awips2Pgtcl.sh
/etc/profile.d/awips2Pgtcl.csh


%changelog
* Mon Dec 06 2021 Lisa Singh <lisa.e.singh@raytheon.com>
- Initial package creation.

