%global _python_bytecompile_extra 0
%define _build_arch %(uname -i)
%define _hdf5_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _libaec_version 1.1.5
%define _zlibng_version 2.2.5
%define _build_id_links none

#
# AWIPS II HDF5 Spec File
#
Name: awips2-hdf5
Summary: AWIPS II HDF5 Distribution
# Can't use variables here since this line is parsed by SetupEnvironment.sh
Version: 2.1.0
Release: %{_component_version}.%{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
BuildRequires: gcc-c++
BuildRequires: make
Provides: %{name} = %{version}

BuildRequires: gcc-c++
BuildRequires: make
BuildRequires: awips2-ninja-build
BuildRequires: libaec
BuildRequires: libaec-devel
BuildRequires: zlib
BuildRequires: zlib-devel
Requires: zlib
Requires: libaec

# HDF5 is now provided by this RPM with all the libs required.
Obsoletes: awips2-tools

%description
AWIPS II HDF5 Distribution

%package devel
Summary: Header files, libraries and development documentation for %{name}.
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: pkgconfig

%description devel
AWIPS II HDF5-DEVEL Distribution

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi
rm -rf %{_build_root}
mkdir -p %{_build_root}/awips2/hdf5

if [ -d %{_hdf5_build_loc} ]; then
   rm -rf %{_hdf5_build_loc}
fi
mkdir -p %{_hdf5_build_loc}

%build
HDF5_TAR_GZ="hdf5-%{version}.tar.gz"
HDF5_SRC_DIR="%{_baseline_workspace}/foss/hdf5-%{version}/packaged"

cp -v ${HDF5_SRC_DIR}/${HDF5_TAR_GZ} %{_hdf5_build_loc}

pushd . > /dev/null
# Untar the source.
cd %{_hdf5_build_loc}
tar -xzvf ${HDF5_TAR_GZ}

pushd . > /dev/null
mkdir %{_hdf5_build_loc}/build
cd %{_hdf5_build_loc}/build

cmake -G "Unix Makefiles" -DCMAKE_BUILD_TYPE:STRING=Release -DBUILD_TESTING:BOOL=ON -DHDF5_BUILD_TOOLS:BOOL=ON -DHDF5_ENABLE_ZLIB_SUPPORT:BOOL=ON -DSZIP_USE_EXTERNAL:BOOL=OFF -DZLIB_USE_EXTERNAL:BOOL=OFF -DHDF5_ENABLE_SZIP_SUPPORT:BOOL=ON -DHDF5_ALLOW_EXTERNAL_SUPPORT:STRING="NO" -DBUILD_SHARED_LIBS:BOOL=ON ../hdf5-%{version}

cmake --build . --config Release
ctest . -C Release
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%install
pushd . > /dev/null
cd %{_hdf5_build_loc}/hdf5-%{version}
cmake --install ../build/ --prefix %{_build_root}/awips2/hdf5
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

# Our profile.d scripts.
mkdir -p %{_build_root}/etc/profile.d
HDF5_PROJECT_DIR="%{_baseline_workspace}/installers/RPMs/hdf5"
HDF5_SCRIPTS_DIR="${HDF5_PROJECT_DIR}/scripts"
HDF5_PROFILED_DIR="${HDF5_SCRIPTS_DIR}/profile.d"
cp -v ${HDF5_PROFILED_DIR}/* %{_build_root}/etc/profile.d
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

%clean
rm -rf %{_build_root}
rm -rf %{_hdf5_build_loc}

%files
%defattr(644,awips,fxalpha,755)
%attr(755,root,root) /etc/profile.d/awips2HDF5.csh
%attr(755,root,root) /etc/profile.d/awips2HDF5.sh
%dir /awips2/hdf5
%dir /awips2/hdf5/lib
/awips2/hdf5/lib/*
/awips2/hdf5/cmake/*
/awips2/hdf5/include/*
%exclude /awips2/hdf5/lib/*.a
%exclude /awips2/hdf5/lib/libhdf5.settings
%defattr(755,awips,fxalpha,755)
%dir /awips2/hdf5/bin
/awips2/hdf5/bin/*

%files devel
%defattr(644,awips,fxalpha,755)
%dir /awips2/hdf5/include
/awips2/hdf5/include/*.h
%dir /awips2/hdf5/share
/awips2/hdf5/share/*
