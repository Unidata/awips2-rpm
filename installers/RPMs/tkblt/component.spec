%global _python_bytecompile_extra 0
%define _tkblt_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _tkblt_version_short %(echo %{version} | cut -f1,2 -d'.')
%define _build_arch %(uname -i)

#
# AWIPS II Tkblt Spec File
#

Name: awips2-tkblt
Summary: AWIPS II Tkblt Distribution
Version: 3.2.23
Release: 1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: i686
URL: https://github.com/wjoye/tkblt
License: N/A
Distribution: N/A
Vendor: ${_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: tk
Requires: libX11
Requires: tcl >= 8.4
BuildRequires: make
BuildRequires: tcl-devel
BuildRequires: tk-devel
BuildRequires: libX11-devel

%description
AWIPS II Tkblt Distribution

%prep
# Ensure that a "buildroot" has been specified.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm --recursive --force %{_build_root}
mkdir --parents "%{_build_root}/awips2/tkblt"
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

if [ -d %{_tkblt_build_loc} ]; then
   rm --recursive --force %{_tkblt_build_loc}
fi
mkdir --parents %{_tkblt_build_loc}

%build
SRC_DIR="%{_baseline_workspace}/foss/tkblt-%{version}/packaged"
PKG_FILE="tkblt-%{version}.tar.gz"
cp --verbose ${SRC_DIR}/${PKG_FILE} %{_tkblt_build_loc}

pushd . > /dev/null

# Untar the source.
cd %{_tkblt_build_loc}
tar --extract --gzip --file ${PKG_FILE}

cd tkblt-%{version}

CFLAGS=-m32 CXXFLAGS=-m32 LDFLAGS=-m32 ./configure --prefix="%{_build_root}/awips2/tkblt" --exec-prefix="%{_build_root}/awips2/tkblt" --build=i686-pc-linux-gnu

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

cd %{_tkblt_build_loc}/tkblt-%{version}

#Perform install
make install

RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

# The config file uses the build directories to specify the lib locations.
# Replace it with the actual locations of libraries, which is similar to /usr/lib/tclConfig.sh
sed -i "s@%{_build_root}@@" %{_build_root}/awips2/tkblt/lib/tkbltConfig.sh
sed -i "s@%{_tkblt_build_loc}@/awips2/tkblt@" %{_build_root}/awips2/tkblt/lib/tkbltConfig.sh

popd > /dev/null

%clean
rm --recursive --force %{_build_root}
rm --recursive --force %{_tkblt_build_loc}

%files
%defattr(-, awips, fxalpha, 0755)
%dir /awips2/tkblt

%defattr(644,awips,fxalpha,755)
%dir /awips2/tkblt/bin
%dir /awips2/tkblt/share
%doc /awips2/tkblt/share/man
%dir /awips2/tkblt/include
/awips2/tkblt/include/tkbltDecls.h
/awips2/tkblt/include/tkbltVector.h
%dir /awips2/tkblt/lib
/awips2/tkblt/lib/tkbltConfig.sh
/awips2/tkblt/lib/tkblt%{_tkblt_version_short}/libtkblt%{_tkblt_version_short}.so
/awips2/tkblt/lib/tkblt%{_tkblt_version_short}/libtkbltstub%{_tkblt_version_short}.a
/awips2/tkblt/lib/tkblt%{_tkblt_version_short}/graph.tcl
/awips2/tkblt/lib/tkblt%{_tkblt_version_short}/pkgIndex.tcl

%changelog
* Mon Dec 06 2021 Lisa Singh <lisa.e.singh@raytheon.com>
- Initial package creation.

