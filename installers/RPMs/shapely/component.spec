%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define geos_version 3.6.2

#
# AWIPS II Python shapely Spec File
#

Name: awips2-python-shapely
Summary: AWIPS II Python shapely Distribution
Version: 1.6.4
Release: 1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vender}
Packager: %{_build_site}

AutoReq: no
BuildRequires: awips2-python
BuildRequires: geos
Requires: awips2-python
Provides: awips2-python-shapely = %{version}


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
__GEOS_TAR=geos-%{geos_version}.tar.bz2
__GEOS_UNTARRED=geos-%{geos_version}
PYTHON_RPM_DIR="%{_baseline_workspace}/rpms/python.site-packages"
INSTALLER_SHAPELY_DIR="%{_baseline_workspace}/foss/geos"

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
__SHAPELY_TAR=Shapely-%{version}.post1.tar.gz
__SHAPELY_UNTARRED=Shapely-%{version}.post1
SHAPELY_SRC_DIR="%{_baseline_workspace}/foss/shapely"

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
