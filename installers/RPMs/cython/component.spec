%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _version 0.27.2
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#
# AWIPS II Python cython Spec File
#
Name: awips2-python-cython
Summary: AWIPS II Python cython Distribution
Version: %{_version}
Release: 1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
requires: awips2-python
provides: awips2-python-cython

%description
AWIPS II Python Cython Site-Package

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
export LD_LIBRARY_PATH=/awips2/tools/lib:/awips2/python/lib:$LD_LIBRARY_PATH
export PATH=/awips2/ant/bin:/awips2/java/bin:/awips2/python/bin:/awips2/groovy/bin:/awips2/tools/bin:$PATH

#source /etc/profile.d/awips2.sh
CYTHON_SRC_DIR="%{_baseline_workspace}/foss/cython"
CYTHON_TAR="Cython-%{_version}.tar.gz"
cp -v ${CYTHON_SRC_DIR}/${CYTHON_TAR} \
   %{_python_build_loc}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null
cd %{_python_build_loc}
tar -xvf ${CYTHON_TAR}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
rm -fv ${CYTHON_TAR}
if [ ! -d Cython-%{_version} ]; then
   file Cython-%{_version}
   exit 1
fi
cd Cython-%{_version}
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
CYTHON_SRC_DIR="%{_baseline_workspace}/foss/cython"

pushd . > /dev/null
cd %{_python_build_loc}/Cython-%{_version}
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
