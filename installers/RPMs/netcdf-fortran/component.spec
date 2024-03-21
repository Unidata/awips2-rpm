%global _python_bytecompile_extra 0
%define _netcdf_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#
# AWIPS II netCDF Fortran Spec File
#
Name: awips2-netcdf-fortran
Summary: AWIPS II NETCDF Fortran Distribution
Version: 4.5.2
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

Requires: awips2-netcdf >= 4.6.0
BuildRequires: awips2-netcdf >= 4.6.0
BuildRequires: gcc-gfortran
BuildRequires: make

%description
AWIPS II NETCDF Fortran Distribution

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
NETCDF_TAR="netcdf-fortran-%{version}.tar.gz"
FOSS_NETCDF_DIR="%{_baseline_workspace}/foss/netcdf-fortran/packaged"

cp --verbose ${FOSS_NETCDF_DIR}/${NETCDF_TAR} %{_netcdf_build_loc}

pushd . > /dev/null

# Untar the source.
cd %{_netcdf_build_loc}
tar --extract --gzip --file=${NETCDF_TAR}

cd netcdf-fortran-%{version}
export LD_LIBRARY_PATH=/awips2/netcdf32/lib:$LD_LIBRARY_PATH
NFDIR=/awips2/netcdf32
NCDIR=/awips2/netcdf32
FCFLAGS=-m32 FFLAGS=-m32 CFLAGS=-m32 LDFLAGS="-m32 -L${NCDIR}/lib" CPPFLAGS="-m32 -I${NCDIR}/include" ./configure --prefix=${NFDIR} --build=i686-pc-linux-gnu --disable-fortran-type-check
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

cd %{_netcdf_build_loc}/netcdf-fortran-%{version}
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
%dir /awips2/netcdf32/share/man
%dir /awips2/netcdf32/share/man/man?
%doc /awips2/netcdf32/share/man/man?/*

%defattr(644,awips,fxalpha,755)
%dir /awips2/netcdf32/bin
/awips2/netcdf32/bin/nf-config
%dir /awips2/netcdf32/include
/awips2/netcdf32/include/netcdf.inc
/awips2/netcdf32/include/netcdf*.mod
/awips2/netcdf32/include/typesizes.mod
%dir /awips2/netcdf32/lib
/awips2/netcdf32/lib/libnetcdff.so
/awips2/netcdf32/lib/libnetcdff.so.*
/awips2/netcdf32/lib/pkgconfig/netcdf-fortran.pc
%exclude /awips2/netcdf32/lib/*.a
%exclude /awips2/netcdf32/lib/*.la
