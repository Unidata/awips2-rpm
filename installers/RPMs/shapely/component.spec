# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)

#
# AWIPS II Python shapely Spec File
#

Name: awips2-python-shapely
Summary: AWIPS II Python shapely Distribution
Version: 1.6.4
Release: %{_installed_python}.3%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: awips2-python = %{_installed_python}
Provides: awips2-python-shapely = %{version}

BuildRequires: awips2-python
BuildRequires: awips2-python-setuptools
BuildRequires: gcc-c++
BuildRequires: make

%description
AWIPS II Python shapely Site-Package

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

if [ -d ${RPM_BUILD_ROOT} ]; then
   rm -rf ${RPM_BUILD_ROOT}
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi

rm -rf %{_build_root}
mkdir -p %{_build_root}
if [ -d %{_build_root}/build-python ]; then
   rm -rf %{_build_root}/build-python
fi
mkdir -p %{_build_root}/build-python
if [ -d %{_python_build_loc} ]; then
   rm -rf %{_python_build_loc}
fi
mkdir -p %{_python_build_loc}

%build

%install
_python_staging=%{_python_build_loc}/awips2/python

mkdir -p ${_python_staging}
# build geos
__GEOS_TAR=geos-3.5.2.tar.bz2
__GEOS_UNTARRED=geos-3.5.2
__GEOS_VERSION=3.5.2
PYTHON_RPM_DIR="%{_baseline_workspace}/rpms/python.site-packages"
INSTALLER_SHAPELY_DIR="%{_baseline_workspace}/foss/geos-${__GEOS_VERSION}/packaged"

cp ${INSTALLER_SHAPELY_DIR}/${__GEOS_TAR} \
   %{_python_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi

cd %{_python_build_loc}
tar -xvf ${__GEOS_TAR}
if [ $? -ne 0 ]; then
   exit 1
fi
cd ${__GEOS_UNTARRED}
./configure --prefix=/awips2/python
if [ $? -ne 0 ]; then
   exit 1
fi
make %{?_smp_mflags}
if [ $? -ne 0 ]; then
   exit 1
fi
make install prefix=${_python_staging}
if [ $? -ne 0 ]; then
   exit 1
fi

# build the shapely python site-package
__SHAPELY=shapely
__SHAPELY_TAR=Shapely-%{version}.post2.tar.gz
__SHAPELY_UNTARRED=Shapely-%{version}.post2
SHAPELY_SRC_DIR="%{_baseline_workspace}/foss/${__SHAPELY}-%{version}/packaged"

cp ${SHAPELY_SRC_DIR}/${__SHAPELY_TAR} \
   %{_python_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi
cd %{_python_build_loc}

tar -xvf ${__SHAPELY_TAR}
if [ $? -ne 0 ]; then
   exit 1
fi
# export GEOS_CONFIG="%{_build_root}/awips2/python/bin/geos-config"
export NO_GEOS_CONFIG="NO_GEOS_CONFIG"
export NO_GEOS_CHECK="NO_GEOS_CHECK"
export GEOS_LIBRARY_PATH="${_python_staging}/lib/libgeos.so"
export CFLAGS="-I${_python_staging}/include"
export LDFLAGS="-L${_python_staging}/lib -lgeos_c"

cd ${__SHAPELY_UNTARRED}
patch -i "%{_baseline_workspace}/foss/${__SHAPELY}-%{version}/packaged/../shapely-setup.py.patch"
if [ $? -ne 0 ]; then
   exit 1
fi

/awips2/python/bin/python setup.py build
if [ $? -ne 0 ]; then
   exit 1
fi
/awips2/python/bin/python setup.py install \
   --root=%{_python_build_loc} \
   --prefix=/awips2/python
if [ $? -ne 0 ]; then
   exit 1
fi
mkdir -p %{_build_root}/awips2
if [ $? -ne 0 ]; then
   exit 1
fi
cp -rf %{_python_build_loc}/awips2/* %{_build_root}/awips2
if [ $? -ne 0 ]; then
   exit 1
fi

%clean
rm -rf %{_build_root}
rm -rf %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
/awips2/python/bin/*
/awips2/python/lib/*
/awips2/python/include/*
