%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#
# AWIPS II Python numpy Spec File
#
Name: awips2-python-numpy
Summary: AWIPS II Python numpy Distribution
Version: 1.9.2
Release: %{_component_version}.%{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: Raytheon

AutoReq: no
requires: compat-libf2c-34(x86-64) >= 3.4.6-19.el6
requires: libgfortran(x86-64) >= 4.4.7-3.el6
requires: awips2-python
requires: awips2-python-nose
provides: awips2-python-numpy

%description
AWIPS II Python numpy Site-Package

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm -rf %{_build_root}
mkdir -p %{_build_root}
if [ -d %{_python_build_loc} ]; then
   rm -rf %{_python_build_loc}
fi
mkdir -p %{_python_build_loc}

%build
NUMPY_SRC_DIR="%{_baseline_workspace}/foss/numpy-%{version}/packaged"
NUMPY_TAR="numpy-%{version}.tar.gz"
cp -v ${NUMPY_SRC_DIR}/${NUMPY_TAR} \
   %{_python_build_loc}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null
cd %{_python_build_loc}
tar -xvf ${NUMPY_TAR}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
rm -fv ${NUMPY_TAR}
if [ ! -d numpy-%{version} ]; then
   file numpy-%{version}
   exit 1
fi
source /etc/profile.d/awips2.sh
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
cd numpy-%{version}
/awips2/python/bin/python setup.py clean
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi 
/awips2/python/bin/python setup.py build
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%install
NUMPY_SRC_DIR="%{_python_pkgs_dir}/numpy"

pushd . > /dev/null
cd %{_python_build_loc}/numpy-%{version}
export LD_LIBRARY_PATH=/awips2/python/lib
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%pre

%post

%preun

%postun

%clean
rm -rf %{_build_root}
rm -rf %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/python/lib/python2.7/site-packages
/awips2/python/lib/python2.7/site-packages/*
%defattr(755,awips,fxalpha,755)
%dir /awips2/python/bin
/awips2/python/bin/*
