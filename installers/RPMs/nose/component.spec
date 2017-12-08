%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#
# AWIPS II Python nose Spec File
#
Name: awips2-python-nose
Summary: AWIPS II Python nose Distribution
Version: 1.3.7
Release: 2%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: noarch
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: awips2-python
Provides: awips2-python-nose

BuildRequires: awips2-python

%description
AWIPS II Python nose Site-Package.

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
NOSE_SRC_DIR="%{_baseline_workspace}/foss/nose"
NOSE_TAR="nose-%{version}.tar.gz"
tar -xvzf ${NOSE_SRC_DIR}/${NOSE_TAR} -C %{_python_build_loc}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

#pushd . > /dev/null
#cd %{_python_build_loc}
#export LD_LIBRARY_PATH=/awips2/python/lib
#/awips2/python/bin/python setup.py build
#RC=$?
#if [ ${RC} -ne 0 ]; then
#   exit 1
#fi
#popd > /dev/null

%install
pushd . > /dev/null
cd %{_python_build_loc}/nose-%{version}
export LD_LIBRARY_PATH=/awips2/python/lib
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python
popd > /dev/null

rm -rf %{_python_build_loc}

%pre

%post

%preun

%postun

%clean
rm -rf %{_build_root}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/python/lib/python2.7/site-packages
/awips2/python/lib/python2.7/site-packages/*
%dir /awips2/python/man
/awips2/python/man/*
%defattr(755,awips,fxalpha,755)
%dir /awips2/python/bin
/awips2/python/bin/*
