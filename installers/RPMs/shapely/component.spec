# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _build_id_links none

#
# AWIPS II Python shapely Spec File
#

Name: awips2-python-shapely
Summary: AWIPS II Python shapely Distribution
Epoch: 1
Version: 1.8.4
Release: %{_installed_python_short}.2%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: awips2-python >= %{_installed_python_short}
Requires: awips2-python-geos >= 3.3
Requires: awips2-python-numpy

BuildRequires: awips2-python
BuildRequires: awips2-python-geos >= 3.3
BuildRequires: awips2-python-numpy
BuildRequires: awips2-python-cython
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
   rm --recursive --force ${RPM_BUILD_ROOT}
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi

rm --recursive --force %{_build_root}
mkdir --parents %{_build_root}
if [ -d %{_build_root}/build-python ]; then
   rm --recursive --force %{_build_root}/build-python
fi
mkdir --parents %{_build_root}/build-python
if [ -d %{_python_build_loc} ]; then
   rm --recursive --force %{_python_build_loc}
fi
mkdir --parents %{_python_build_loc}

%build
# build the shapely python site-package
SHAPELY_TAR=shapely-%{version}.tar.gz
SHAPELY_SRC_DIR="%{_baseline_workspace}/foss/shapely-%{version}/packaged"

cp ${SHAPELY_SRC_DIR}/${SHAPELY_TAR} \
   %{_python_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null
cd %{_python_build_loc}
tar --extract --verbose --file=${SHAPELY_TAR}
if [ $? -ne 0 ]; then
   exit 1
fi
rm --recursive --force ${SHAPELY_TAR}
export GEOS_CONFIG="/awips2/python/bin/geos-config"

cd shapely-%{version}
/awips2/python/bin/python setup.py build
if [ $? -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%install
pushd . > /dev/null
export GEOS_CONFIG="/awips2/python/bin/geos-config"
cd %{_python_build_loc}/shapely-%{version}
/awips2/python/bin/python setup.py install \
   --root=%{_python_build_loc} \
   --prefix=/awips2/python
if [ $? -ne 0 ]; then
   exit 1
fi
popd > /dev/null

mkdir --parents %{_build_root}/awips2
if [ $? -ne 0 ]; then
   exit 1
fi
cp --recursive --force %{_python_build_loc}/awips2/* %{_build_root}/awips2
if [ $? -ne 0 ]; then
   exit 1
fi

# Merge lib64 into lib to avoid problems with installing into the virtualenv
if [ -d "%{_build_root}/awips2/python/lib64/" ]; then
    rsync --archive %{_build_root}/awips2/python/lib64/ %{_build_root}/awips2/python/lib || exit 1
    rm --recursive --force %{_build_root}/awips2/python/lib64
fi

%clean
rm --recursive --force %{_build_root}
rm --recursive --force %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
/awips2/python/lib/*
