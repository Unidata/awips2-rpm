%global _python_bytecompile_extra 0
%define _build_arch %(uname -i)
%define _udunits_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _build_id_links none

#
# AWIPS II udunits Spec File
#
Name: awips2-udunits
Summary: AWIPS II UDUNITS Distribution
Version: 2.2.28
Release: %{_component_version}.%{_component_release}.1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: i686
URL: N/A
License: N/A
Distribution: N/A
Vendor: ${_build_vendor}
Packager: %{_build_site}

AutoReq: no
Provides: %{name} = %{version}
BuildRequires: make

%description
AWIPS II UDUNITS Distribution

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm --recursive --force %{_build_root}
mkdir --parents %{_build_root}/awips2/udunits
if [ -d %{_udunits_build_loc} ]; then
   rm --recursive --force %{_udunits_build_loc}
fi
mkdir --parents %{_udunits_build_loc}

%build
UDUNITS_TAR="udunits-%{version}.tar.gz"
FOSS_UDUNITS_DIR="%{_baseline_workspace}/foss/udunits-%{version}/packaged"

cp -v ${FOSS_UDUNITS_DIR}/${UDUNITS_TAR} %{_udunits_build_loc}

pushd . > /dev/null

# Untar the source.
cd %{_udunits_build_loc}
tar --extract --gzip --file=${UDUNITS_TAR}

cd udunits-%{version}

CFLAGS=-m32 CXXFLAGS=-m32 LDFLAGS=-m32 ./configure --prefix=/awips2/udunits --build=i686-pc-linux-gnu
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

make
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%install
pushd . > /dev/null

cd %{_udunits_build_loc}/udunits-%{version}
make install prefix=%{_build_root}/awips2/udunits
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

popd > /dev/null

%clean
rm --recursive --force %{_build_root}
rm --recursive --force %{_udunits_build_loc}

%files
%defattr(-, awips, fxalpha, 0755)
%dir /awips2/udunits
%dir /awips2/udunits/share
%dir /awips2/udunits/share/info
%doc /awips2/udunits/share/info/*
%dir /awips2/udunits/share/doc
%dir /awips2/udunits/share/doc/udunits
%doc /awips2/udunits/share/doc/udunits/*
%dir /awips2/udunits/share/udunits
%doc /awips2/udunits/share/udunits/*

%defattr(755,awips,fxalpha,755)
%dir /awips2/udunits/bin
/awips2/udunits/bin/udunits2

%defattr(644,awips,fxalpha,755)
%dir /awips2/udunits/include
/awips2/udunits/include/converter.h
/awips2/udunits/include/udunits.h
/awips2/udunits/include/udunits2.h
%dir /awips2/udunits/lib
/awips2/udunits/lib/libudunits2.so
/awips2/udunits/lib/libudunits2.so.*
%exclude /awips2/udunits/lib/*.a
%exclude /awips2/udunits/lib/*.la
