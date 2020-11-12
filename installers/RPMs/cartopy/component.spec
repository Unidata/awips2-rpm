%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#
# AWIPS II Python cartopy Spec File
#
Name: awips2-python-cartopy
Summary: AWIPS II Python cartopy Distribution
Version: 0.14.2
Release: 1
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
requires: awips2-python-numpy
provides: awips2-python-cartopy

%description
AWIPS II Python cartopy Site-Package

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
CARTOPY_SRC_DIR="%{_baseline_workspace}/foss/cartopy"
CARTOPY_TAR="v%{version}.tar.gz"
cp -v ${CARTOPY_SRC_DIR}/${CARTOPY_TAR} \
   %{_python_build_loc}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null
cd %{_python_build_loc}
tar -xvf ${CARTOPY_TAR}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
rm -fv ${CARTOPY_TAR}
if [ ! -d cartopy-%{version} ]; then
   file cartopy-${version}
   exit 1
fi

export BLAS=/awips2/python/lib
export LAPACK=/awips2/python/lib
source /etc/profile.d/awips2.sh
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null
cd cartopy-%{version}
export LD_LIBRARY_PATH=/awips2/python/lib
/awips2/python/bin/python setup.py build_ext --include-dirs=/awips2/python/include:/awips2/postgresql/include
RC=$?
if [ ${RC} -ne 0 ]; then
   # Try to build a second time. It seems to work
   # for some reason.
   /awips2/python/bin/python setup.py build_ext --include-dirs=/awips2/python/include:/awips2/postgresql/include
   RC=$?
   if [ ${RC} -ne 0 ]; then
      exit 1
   fi
fi
popd > /dev/null

%install

export BLAS=/awips2/python/lib
export LAPACK=/awips2/python/lib

pushd . > /dev/null
cd %{_python_build_loc}/cartopy-%{version}
export LD_LIBRARY_PATH=/awips2/python/lib
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%clean
rm -rf %{_build_root}
rm -rf %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/python/lib/python2.7/site-packages
/awips2/python/lib/python2.7/site-packages/*
