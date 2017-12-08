%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#
# AWIPS II Python awips Spec File
#
Name: awips2-python-awips
Summary: AWIPS II Python awips Distribution
Version: 0.9.10
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
Obsoletes: awips2-python-ufpy < 15.1.3-1
Obsoletes: awips2-python-dynamicserialize < 15.1.3-1
Obsoletes: awips2-python-thrift < 20080411p1-4
provides: awips2-python-awips

%description
AWIPS II Python Awips Site-Package

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

%build

%install
PYTHON_AWIPS=/awips2/repo/python-awips

mkdir -p %{_build_root}/awips2/python/lib/python2.7/site-packages/awips
if [ $? -ne 0 ]; then
   exit 1
fi
cp -rv ${PYTHON_AWIPS}/awips/* \
   %{_build_root}/awips2/python/lib/python2.7/site-packages/awips

# dynamicserialize
mkdir -p %{_build_root}/awips2/python/lib/python2.7/site-packages/dynamicserialize
if [ $? -ne 0 ]; then
   exit 1
fi
cp -rv ${PYTHON_AWIPS}/dynamicserialize/* \
   %{_build_root}/awips2/python/lib/python2.7/site-packages/dynamicserialize

# thrift
mkdir -p %{_build_root}/awips2/python/lib/python2.7/site-packages/thrift
if [ $? -ne 0 ]; then
   exit 1
fi
cp -rv ${PYTHON_AWIPS}/thrift/* \
   %{_build_root}/awips2/python/lib/python2.7/site-packages/thrift

%pre
if [ -d /awips2/python/lib/python2.7/site-packages/awips ]; then
   rm -rf /awips2/python/lib/python2.7/site-packages/awips
fi
if [ -d /awips2/python/lib/python2.7/site-packages/dynamicserialize ]; then
   rm -rf /awips2/python/lib/python2.7/site-packages/dynamicserialize
fi
if [ -d /awips2/python/lib/python2.7/site-packages/thrift ]; then
   rm -rf /awips2/python/lib/python2.7/site-packages/thrift
fi

%post

%preun

%postun

%clean
rm -rf %{_build_root}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/python/lib/python2.7/site-packages
/awips2/python/lib/python2.7/site-packages/*
