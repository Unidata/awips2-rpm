%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _netcdf_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
#
# AWIPS II netCDF Spec File
#
Name: awips2-netcdf
Summary: AWIPS II NETCDF Distribution
Version: 4.6.1
Release: %{_component_version}.%{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
#Vendor: Raytheon
Vendor:  %{_build_vendor}
Packager: %{_build_site}
AutoReq: no
Provides: %{name} = %{version}
Requires: awips2-hdf5
BuildRequires: awips2-hdf5
BuildRequires: binutils
BuildRequires: gcc-c++
BuildRequires: gcc-gfortran
BuildRequires: libcurl-devel
BuildRequires: make
## Due to the build servers building multiple versions of AWIPS
## these packages cannot be obsolete at this time as it will 
## fail previous versions.
# Remove the AWIPS modified variants that mirror base packages...
#Obsoletes: netcdf
#Obsoletes: netcdf-devel
#Obsoletes: netcdf-AWIPS
%description
AWIPS II NETCDF Distribution
%package devel
Summary: Header files, libraries and development documentation for %{name}.
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: pkgconfig
%description devel
AWIPS II NETCDF-DEVEL Distribution
%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi
rm -rf %{_build_root}
mkdir -p %{_build_root}/awips2/netcdf
if [ -d %{_netcdf_build_loc} ]; then
   rm -rf %{_netcdf_build_loc}
fi
mkdir -p %{_netcdf_build_loc}
%build
NETCDF_TAR="netcdf-%{version}.tar.gz"
FOSS_NETCDF_DIR="%{_baseline_workspace}/foss/netcdf-%{version}/packaged"
cp -v ${FOSS_NETCDF_DIR}/${NETCDF_TAR} %{_netcdf_build_loc}
pushd . > /dev/null
# Untar the source.
cd %{_netcdf_build_loc}
tar -zxf ${NETCDF_TAR}
cd netcdf-%{version}
CPPFLAGS=-I/awips2/hdf5/include LDFLAGS='-L/awips2/hdf5/lib -Wl,-rpath,/awips2/hdf5/lib,-rpath,/awips2/netcdf/lib' ./configure \
   --prefix=/awips2/netcdf
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
make %{?_smp_mflags}
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null
%install
pushd . > /dev/null
cd %{_netcdf_build_loc}/netcdf-%{version}
make install prefix=%{_build_root}/awips2/netcdf
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null
%clean
rm -rf %{_build_root}
rm -rf %{_netcdf_build_loc}
%files
%defattr(-, awips, fxalpha, 0755)
%dir /awips2/netcdf
%dir /awips2/netcdf/share
%dir /awips2/netcdf/share/man
%dir /awips2/netcdf/share/man/man?
%doc /awips2/netcdf/share/man/man?/*
%defattr(755,awips,fxalpha,755)
%dir /awips2/netcdf/bin
/awips2/netcdf/bin/nccopy
/awips2/netcdf/bin/ncdump
/awips2/netcdf/bin/ncgen
/awips2/netcdf/bin/ncgen3
/awips2/netcdf/bin/ocprint
%defattr(644,awips,fxalpha,755)
%dir /awips2/netcdf/lib
/awips2/netcdf/lib/libnetcdf.so.*
/awips2/netcdf/lib/libbzip2.so
/awips2/netcdf/lib/libmisc.so
%files devel
%defattr(644,awips,fxalpha,755)
/awips2/netcdf/bin/nc-config
%dir /awips2/netcdf/include
/awips2/netcdf/include/netcdf*
/awips2/netcdf/lib/libnetcdf.so
/awips2/netcdf/lib/pkgconfig/*.pc
%exclude /awips2/netcdf/lib/*.a
%exclude /awips2/netcdf/lib/*.la
%exclude /awips2/netcdf/lib/libnetcdf.settings
