%global _python_bytecompile_extra 0
%define _build_arch %(uname -i)
%define _netcdf_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%ifarch x86_64
%define _prefix /awips2/netcdf
%else
%define _prefix /awips2/netcdf32
%endif
%define _build_id_links none

#
# AWIPS II netCDF Spec File
#
Name: awips2-netcdf
Summary: AWIPS II NETCDF Distribution
Version: 4.6.1
Release: %{_component_version}.%{_component_release}.5%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
Provides: %{name} = %{version}
%ifarch x86_64
Requires: awips2-hdf5
%endif

BuildRequires: awips2-hdf5-devel
BuildRequires: binutils
BuildRequires: gcc-c++
BuildRequires: gcc-gfortran
BuildRequires: libcurl-devel
BuildRequires: m4
BuildRequires: make
BuildRequires: zlib-devel

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
%ifarch x86_64
Requires: awips2-hdf5-devel
%endif

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

rm --recursive --force %{_build_root}
mkdir --parents %{_build_root}/awips2/netcdf
if [ -d %{_netcdf_build_loc} ]; then
   rm --recursive --force %{_netcdf_build_loc}
fi
mkdir --parents %{_netcdf_build_loc}

%build
NETCDF_TAR="netcdf-%{version}.tar.gz"
FOSS_NETCDF_DIR="%{_baseline_workspace}/foss/netcdf-%{version}/packaged"

cp --verbose ${FOSS_NETCDF_DIR}/${NETCDF_TAR} %{_netcdf_build_loc}

pushd . > /dev/null

# Untar the source.
cd %{_netcdf_build_loc}
tar --extract --gzip --file=${NETCDF_TAR}

cd netcdf-%{version}
if [ %{_build_arch} = "x86_64" ]; then
   CPPFLAGS=-I/awips2/hdf5/include LDFLAGS='-L/awips2/hdf5/lib -Wl,-rpath,/awips2/hdf5/lib,-rpath,/awips2/netcdf/lib' ./configure --prefix=%{_prefix}
else
   CFLAGS=-m32 CXXFLAGS=-m32 LDFLAGS=-m32 ./configure --prefix=%{_prefix} --build=i686-pc-linux-gnu --disable-netcdf-4
fi
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
make install prefix=%{_build_root}%{_prefix}
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
%dir %{_prefix}
%dir %{_prefix}/share
%dir %{_prefix}/share/man
%dir %{_prefix}/share/man/man?
%doc %{_prefix}/share/man/man?/*

%defattr(755,awips,fxalpha,755)
%dir %{_prefix}/bin
%{_prefix}/bin/nccopy
%{_prefix}/bin/ncdump
%{_prefix}/bin/ncgen
%{_prefix}/bin/ncgen3
%{_prefix}/bin/ocprint
%defattr(644,awips,fxalpha,755)
%dir %{_prefix}/lib
%{_prefix}/lib/libnetcdf.so.*
%ifarch x86_64
%{_prefix}/lib/libbzip2.so
%{_prefix}/lib/libmisc.so
%endif

%files devel
%defattr(644,awips,fxalpha,755)
%{_prefix}/bin/nc-config
%dir %{_prefix}/include
%{_prefix}/include/netcdf*
%{_prefix}/lib/libnetcdf.so
%{_prefix}/lib/pkgconfig/*.pc
%exclude %{_prefix}/lib/*.a
%exclude %{_prefix}/lib/*.la
%exclude %{_prefix}/lib/libnetcdf.settings
