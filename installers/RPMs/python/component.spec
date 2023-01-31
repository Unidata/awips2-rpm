# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _lapack_version 3.4.2

#
# AWIPS II Python Spec File
#
Name: awips2-python
Summary: AWIPS II Python Distribution
Version: 3.6.15
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
provides: awips2-python = %{version}
Requires: tk
Requires: readline
Requires: bzip2
Requires: openssl
Requires: zlib

# Required for  Tkinter
BuildRequires: tk-devel
BuildRequires: tcl-devel
BuildRequires: readline-devel
# Standard library support
BuildRequires: bzip2-devel
BuildRequires: gcc-gfortran
BuildRequires: make
BuildRequires: openssl-devel
BuildRequires: zlib-devel

Obsoletes: awips2-python-pmw

%description
AWIPS II Python Distribution - Contains Python V%{version} plus modules
required for AWIPS II.

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm -rf %{_build_root}
mkdir -p %{_build_root}/awips2/python
if [ -d %{_python_build_loc} ]; then
   rm -rf %{_python_build_loc}
fi
mkdir -p %{_python_build_loc}

%build
PYTHON_TAR="Python-%{version}.tgz"
PYTHON_PROJECT_SRC_DIR="%{_baseline_workspace}/foss/python-%{version}/packaged"
FOSS_PYTHON_DIR="%{_baseline_workspace}/foss/python-%{version}/packaged"

cp -v ${FOSS_PYTHON_DIR}/${PYTHON_TAR} %{_python_build_loc}

pushd . > /dev/null

# Untar the source.
cd %{_python_build_loc}
tar -xf ${PYTHON_TAR}

cd Python-%{version}

LDFLAGS='-Wl,-rpath=/awips2/python/lib,-rpath=/awips2/netcdf/lib,-rpath=/awips2/hdf5/lib' ./configure \
   --prefix=/awips2/python \
   --enable-shared
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

make clean
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
# Copies the standard licenses into a license directory for the
# current component.
function copyLegal()
{
   # $1 == Component Build Root
   
   COMPONENT_BUILD_DIR=${1}
   
   mkdir -p %{_build_root}/${COMPONENT_BUILD_DIR}/licenses

   cp "%{_baseline_workspace}/rpms/legal/Master_Rights_File.pdf" \
      %{_build_root}/${COMPONENT_BUILD_DIR}/licenses    
}
pushd . > /dev/null

cd %{_python_build_loc}/Python-%{version}
make install prefix=%{_build_root}/awips2/python
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

cd %{_build_root}/awips2/python/bin
ln --symbolic python3 python

popd > /dev/null

RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

# Our profile.d scripts.
mkdir -p %{_build_root}/etc/profile.d
PYTHON_PROJECT_DIR="%{_baseline_workspace}/installers/RPMs/python"
PYTHON_PROJECT_SRC_DIR="${PYTHON_PROJECT_DIR}/src"
PYTHON_SCRIPTS_DIR="${PYTHON_PROJECT_DIR}/scripts"
PYTHON_PROFILED_DIR="${PYTHON_SCRIPTS_DIR}/profile.d"
cp -v ${PYTHON_PROFILED_DIR}/* %{_build_root}/etc/profile.d
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

# The external libraries and headers we include with python.

PYTHON_PROJECT_DIR="%{_baseline_workspace}/installers/RPMs/python"
PYTHON_PROJECT_SRC_DIR="${PYTHON_PROJECT_DIR}/src"
PYTHON_PROJECT_NATIVE_DIR="${PYTHON_PROJECT_DIR}/nativeLib"
FOSS_LAPACK_DIR="%{_baseline_workspace}/foss/lapack-%{_lapack_version}/packaged"
LAPACK_TAR="lapack-%{_lapack_version}.tgz"
LAPACK_PATCH="lapack.patch1"

# The %{_build_vendor}-built native (nativeLib) libraries.
cp -vP ${PYTHON_PROJECT_NATIVE_DIR}/%{_build_arch}/grib2.so \
       ${PYTHON_PROJECT_NATIVE_DIR}/%{_build_arch}/gridslice.so \
       %{_build_root}/awips2/python/lib/python3.6
if [ $? -ne 0 ]; then
   exit 1
fi
cp -vP ${PYTHON_PROJECT_NATIVE_DIR}/%{_build_arch}/libjasper.so \
       ${PYTHON_PROJECT_NATIVE_DIR}/%{_build_arch}/libjasper.so.4 \
       ${PYTHON_PROJECT_NATIVE_DIR}/%{_build_arch}/libjasper.so.4.0.0 \
       %{_build_root}/awips2/python/lib
if [ $? -ne 0 ]; then
   exit 1
fi

# Copy the LAPACK tar file and patch to our build directory.
echo ${FOSS_LAPACK_DIR}/${LAPACK_TAR} 
cp -v ${FOSS_LAPACK_DIR}/${LAPACK_TAR} \
   %{_python_build_loc}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
cp -v ${FOSS_LAPACK_DIR}/${LAPACK_PATCH} \
   %{_python_build_loc}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
pushd . > /dev/null
cd %{_python_build_loc}
tar -xvf ${LAPACK_TAR}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
rm -fv ${LAPACK_TAR}
if [ ! -d lapack-%{_lapack_version} ]; then
   echo "Directory lapack-%{_lapack_version} not found!"
   exit 1
fi
patch -p1 -i ${LAPACK_PATCH}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
cd lapack-%{_lapack_version}
mv make.inc.example make.inc
if [ $? -ne 0 ]; then
   exit 1
fi
sed -i 's/-lg2c//g'  BLAS/SRC/Makefile
make %{?_smp_mflags} blaslib
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
sed -i 's/-lg2c//g'  SRC/Makefile
make %{?_smp_mflags} lapacklib
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
# Copy the libraries that we just built to
# the python lib directory.
if [ ! -f BLAS/SRC/libblas.so ]; then
   echo "File BLAS/SRC/libblas.so not found!"
   exit 1
fi
cp -v BLAS/SRC/libblas.so \
   %{_build_root}/awips2/python/lib
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
if [ ! -f SRC/liblapack.so ]; then
   echo "File SRC/liblapack.so not found"
   exit 1
fi
cp -v SRC/liblapack.so \
   %{_build_root}/awips2/python/lib
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

popd > /dev/null

copyLegal "awips2/python"

%clean
rm -rf %{_build_root}
rm -rf %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
%attr(755,root,root) /etc/profile.d/awips2Python.csh
%attr(755,root,root) /etc/profile.d/awips2Python.sh
%dir /awips2/python
%dir /awips2/python/lib
/awips2/python/lib/*
%docdir /awips2/python/licenses
%dir /awips2/python/licenses
/awips2/python/licenses/*
%dir /awips2/python/share
/awips2/python/share/*
%defattr(755,awips,fxalpha,755)
%dir /awips2/python/include
/awips2/python/include/*
%dir /awips2/python/bin
/awips2/python/bin/*

%changelog
* Tue Oct 06 2020 Ron Anderson <ron.anderson@raytheon.com> 
- Added obsoletes for pmw

