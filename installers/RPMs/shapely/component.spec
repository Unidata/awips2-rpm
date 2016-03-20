%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _geos_version 3.5.0
%define _shapely_version 1.5.9
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#
# AWIPS II Python shapely Spec File
#

Name: awips2-python-shapely
Summary: AWIPS II Python shapely Distribution
Version: %{_shapely_version}
Release: 2
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
provides: awips2-python-shapely

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

PYTHON_RPM_DIR="%{_baseline_workspace}/rpms/python.site-packages"
INSTALL_SETUPTOOLS_SH="${PYTHON_RPM_DIR}/deploy.builder/install-setuptools.sh"
# install setuptools
/bin/bash ${INSTALL_SETUPTOOLS_SH} %{_baseline_workspace} \
   %{_python_pkgs_dir} %{_build_root}/build-python
if [ $? -ne 0 ]; then
   exit 1
fi

rm -rf %{_build_root}/build-python

%build

%install
_python_staging=%{_python_build_loc}/awips2/python

mkdir -p %{_python_staging}
# build geos
__GEOS_TAR=geos-%{_geos_version}.tar.bz2
__GEOS_UNTARRED=geos-%{_geos_version}
INSTALLER_SHAPELY_DIR="%{_baseline_workspace}/foss/geos/packaged"

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
make
if [ $? -ne 0 ]; then
   exit 1
fi
make install prefix=${_python_staging}
if [ $? -ne 0 ]; then
   exit 1
fi

# build the shapely python site-package
__SHAPELY=shapely
__SHAPELY_TAR=Shapely-%{_shapely_version}.tar.gz
__SHAPELY_UNTARRED=Shapely-%{_shapely_version}
SHAPELY_SRC_DIR="%{_baseline_workspace}/foss/shapely/packaged"

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
export CPPFLAGS="-I%{_build_root}/awips2/python/include"
export CPPFLAGS="${CPPFLAGS} -L%{_build_root}/awips2/python/lib"

cd ${__SHAPELY_UNTARRED}

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
%dir /awips2/python/bin
/awips2/python/bin/*
%dir /awips2/python/lib
/awips2/python/lib/*
%dir /awips2/python/include
/awips2/python/include/*
%dir /awips2/python/shapely
/awips2/python/shapely/*
