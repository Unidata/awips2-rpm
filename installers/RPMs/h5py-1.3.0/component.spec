%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#
# AWIPS II Python h5py Spec File
#
Name: awips2-python-h5py
Summary: AWIPS II Python h5py Distribution
Version: 1.3.0
Release: 5.el6
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: Raytheon
Packager: Bryan Kowal

AutoReq: no
requires: awips2-python
requires: awips2-python-numpy
requires: libz.so.1
provides: awips2-python-h5py

%description
AWIPS II Python h5py Site-Package

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm -rf %{_build_root}
if [ $? -ne 0 ]; then
   exit 1
fi
mkdir -p %{_build_root}
if [ $? -ne 0 ]; then
   exit 1
fi
mkdir -p %{_build_root}/awips2/python/lib
if [ $? -ne 0 ]; then
   exit 1
fi

PRE_REQS_HDF5_TAR=""
if [ "%{_build_arch}" = "i386" ]; then
   PRE_REQS_HDF5_TAR="hdf5-1.8.4-patch1-linux-shared.tar.gz"
else
   if [ "%{_build_arch}" = "x86_64" ]; then
      PRE_REQS_HDF5_TAR="hdf5-1.8.4-patch1-linux-x86_64-shared.tar.gz"
   else
      echo "ERROR: Unrecognized Architecture."
      exit 1
   fi
fi

if [ -d %{_python_build_loc} ]; then
   rm -rf %{_python_build_loc}
fi
mkdir -p %{_python_build_loc}

PRE_REQS_DIR="%{_baseline_workspace}/rpms/python.site-packages/deploy.builder/pre-reqs"
cp -v ${PRE_REQS_DIR}/${PRE_REQS_HDF5_TAR} \
   %{_python_build_loc}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null
cd %{_python_build_loc}
/bin/tar -xvf ${PRE_REQS_HDF5_TAR}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
rm -f ${PRE_REQS_HDF5_TAR}
popd > /dev/null

%build
HDF5_PATH=
if [ "%{_build_arch}" = "i386" ]; then
   HDF5_PATH="%{_python_build_loc}/hdf5-1.8.4-patch1-linux-shared"
else
   HDF5_PATH="%{_python_build_loc}/hdf5-1.8.4-patch1-linux-x86_64-shared"
fi

SZIP_VERSION=2.1
H5PY_SRC_DIR="%{_baseline_workspace}/foss/h5py-%{version}/packaged/"
SZIP_SRC_DIR="%{_baseline_workspace}/foss/szip-$SZIP_VERSION/packaged"
SZIP_TAR="szip-2.1.tar"

# Copy the h5py source.
cp -rv ${H5PY_SRC_DIR}/* \
   %{_python_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi
# Copy the szip source.
cp -rv ${SZIP_SRC_DIR}/${SZIP_TAR} \
   %{_python_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi
pushd . > /dev/null
# build h5py
cd %{_python_build_loc}

pushd . > /dev/null
tar xvzf h5py-%{version}.tar.gz
cd h5py-%{version}
export LD_LIBRARY_PATH=/awips2/python/lib
/awips2/python/bin/python setup.py build \
   --hdf5=${HDF5_PATH}
if [ $? -ne 0 ]; then
   exit 1
fi
# build szip

popd > /dev/null
/bin/tar -xf ${SZIP_TAR}
if [ $? -ne 0 ]; then
   exit 1
fi
cd szip-$SZIP_VERSION
./configure
if [ $? -ne 0 ]; then
   exit 1
fi
make
if [ $? -ne 0 ]; then
   exit 1
fi
cd ..
/bin/rm -f ${SZIP_TAR}
if [ $? -ne 0 ]; then
   exit 1
fi

popd > /dev/null

%install
HDF5_PATH=
if [ "%{_build_arch}" = "i386" ]; then
   HDF5_PATH="%{_python_build_loc}/hdf5-1.8.4-patch1-linux-shared"
else
   HDF5_PATH="%{_python_build_loc}/hdf5-1.8.4-patch1-linux-x86_64-shared"
fi

pushd . > /dev/null
cd %{_python_build_loc}

cd h5py-%{version}
export LD_LIBRARY_PATH=/awips2/python/lib
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python
popd > /dev/null

pushd . > /dev/null
cd %{_python_build_loc}/szip-2.1
cp -P src/.libs/libsz.so* \
   %{_build_root}/awips2/python/lib
if [ $? -ne 0 ]; then
   exit 1
fi
cd ..
/bin/rm -rf szip-2.1
if [ $? -ne 0 ]; then
   exit 1
fi
popd > /dev/null

rm -rf ${HDF5_PATH}

%pre

%post

%preun

%postun

%clean
rm -rf ${RPM_BUILD_ROOT}
rm -rf %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/python/lib
/awips2/python/lib/*
