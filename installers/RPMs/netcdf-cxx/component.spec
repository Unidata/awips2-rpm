%global _python_bytecompile_extra 0
%define _build_arch %(uname -i)
%define _netcdf_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#
# AWIPS II netCDF-cxx Spec File
#
Name: awips2-netcdf-cxx
Summary: AWIPS II NETCDF-cxx Distribution
Version: 4.2
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
# Requires and BuildRequires can't specify an architecture, but they can
# specify they require a file that is only provided by an RPM for a specific
# architecture. Therefore this is here to ensure the 32-bit awips2-netcdf-devel
# is installed since it is required to build netcdf-cxx.
BuildRequires: /awips2/netcdf32/lib/libnetcdf.so

%description
AWIPS II NETCDF-cxx Distribution

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm --recursive --force %{_build_root}
mkdir --parents %{_build_root}/awips2/netcdf32
if [ -d %{_netcdf_build_loc} ]; then
   rm --recursive --force %{_netcdf_build_loc}
fi
mkdir --parents %{_netcdf_build_loc}

%build
NETCDF_TAR="netcdf-cxx-%{version}.tar.gz"
FOSS_NETCDF_DIR="%{_baseline_workspace}/foss/netcdf-cxx-%{version}/packaged"

cp -v ${FOSS_NETCDF_DIR}/${NETCDF_TAR} %{_netcdf_build_loc}

pushd . > /dev/null

# Untar the source.
cd %{_netcdf_build_loc}
tar --extract --gzip --file=${NETCDF_TAR}

cd netcdf-cxx-%{version}

CFLAGS=-m32 CXXFLAGS=-m32 LDFLAGS=-m32 CPPFLAGS=-I/awips2/netcdf32/include ./configure --prefix=/awips2/netcdf32 --build=i686-pc-linux-gnu
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

cd %{_netcdf_build_loc}/netcdf-cxx-%{version}
make install prefix=%{_build_root}/awips2/netcdf32
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

popd > /dev/null

%clean
rm --recursive --force %{_build_root}
rm --recursive --force %{_netcdf_build_loc}

%files
%defattr(-, awips, fxalpha, 0755)
%dir /awips2/netcdf32
%dir /awips2/netcdf32/share
%dir /awips2/netcdf32/share/info
%doc /awips2/netcdf32/share/info/dir
%doc /awips2/netcdf32/share/info/netcdf-cxx.info

%defattr(644,awips,fxalpha,755)
%dir /awips2/netcdf32/include
/awips2/netcdf32/include/ncvalues.h
/awips2/netcdf32/include/netcdf.hh
/awips2/netcdf32/include/netcdfcpp.h
%dir /awips2/netcdf32/lib
/awips2/netcdf32/lib/libnetcdf_c++.so
/awips2/netcdf32/lib/libnetcdf_c++.so.*
%exclude /awips2/netcdf32/lib/*.a
%exclude /awips2/netcdf32/lib/*.la
