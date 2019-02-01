%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _hdf5_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _szip_version 2.1.1

#
# AWIPS II HDF5 Spec File
#
Name: awips2-hdf5
Summary: AWIPS II HDF5 Distribution
Version: 1.8.20
Release: %{_component_version}.%{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: Raytheon
Packager: %{_build_site}

AutoReq: no
Provides: %{name} = %{version}

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
LZF_TAR="lzf.tar.gz"
HDF5_TAR="hdf5-%{version}.tar"
HDF5_SRC_DIR="%{_baseline_workspace}/foss/hdf5-%{version}/packaged"

SZIP_TAR="szip-%{_szip_version}.tar"
SZIP_TAR_GZ="${SZIP_TAR=}.gz"
SZIP_SRC_DIR="%{_baseline_workspace}/foss/szip-%{_szip_version}/packaged"

# Copy the szip source.
cp -rv ${SZIP_SRC_DIR}/${SZIP_TAR_GZ} \
   %{_hdf5_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi

# build szip
pushd . > /dev/null
cd %{_hdf5_build_loc}
/bin/gunzip ${SZIP_TAR_GZ}
/bin/tar -zxf ${SZIP_TAR}
if [ $? -ne 0 ]; then
   exit 1
fi
cd szip-%{_szip_version}
./configure --prefix=/awips2/hdf5
if [ $? -ne 0 ]; then
   exit 1
fi
make %{?_smp_mflags}
if [ $? -ne 0 ]; then
   exit 1
fi
#Install early to a tmp loc so HDF5 can use the lib
make install prefix=%{_hdf5_build_loc}/awips2/hdf5
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

cd ..
/bin/rm -f ${SZIP_TAR}
if [ $? -ne 0 ]; then
   exit 1
fi

popd > /dev/null

cp -v ${HDF5_SRC_DIR}/${HDF5_TAR} %{_hdf5_build_loc}
cp -v ${HDF5_SRC_DIR}/${LZF_TAR} %{_hdf5_build_loc}

pushd . > /dev/null
# Untar the source.
cd %{_hdf5_build_loc}
tar -xf ${HDF5_TAR}
tar -xf ${LZF_TAR}

pushd . > /dev/null
cd %{_hdf5_build_loc}/hdf5-%{version}

LDFLAGS='-Wl,-rpath,/awips2/hdf5/lib' ./configure \
   --prefix=/awips2/hdf5 \
   --with-szlib=%{_hdf5_build_loc}/awips2/hdf5
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

make %{?_smp_mflags}
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

pushd . > /dev/null 2>&1
# build lzf
cd %{_hdf5_build_loc}/lzf
gcc -O2 -I%{_hdf5_build_loc}/hdf5-%{version}/src \
   -fPIC \
   -shared lzf/*.c lzf_filter.c \
   -L %{_hdf5_build_loc}/hdf5-%{version}/src/.libs \
   -lhdf5 \
   -Wl,-rpath,/awips2/hdf5/lib \
   -o liblzf_filter.so
if [ $? -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%install

pushd . > /dev/null
cd %{_hdf5_build_loc}/szip-%{_szip_version}
make install prefix=%{_build_root}/awips2/hdf5
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

pushd . > /dev/null
cd %{_hdf5_build_loc}/hdf5-%{version}
make install prefix=%{_build_root}/awips2/hdf5
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

# Copy the lzf library to tools/lib
cp %{_hdf5_build_loc}/lzf/*.so \
   %{_build_root}/awips2/hdf5/lib

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
%exclude /awips2/hdf5/lib/*.a
%exclude /awips2/hdf5/lib/*.la
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
