%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#
# AWIPS II Python numexpr Spec File
#
Name: awips2-python-numexpr
Summary: AWIPS II Python numexpr Distribution
Version: 2.6.2
Release: 1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: Raytheon
Packager: %{_build_site}

AutoReq: no
Requires: awips2-python
Requires: awips2-python-numpy
Provides: awips2-python-numexpr = %{version}

BuildRequires: awips2-python
BuildRequires: awips2-python-numpy
BuildRequires: awips2-java

%description
AWIPS II Python numexpr Site-Package

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
SRC_DIR="%{_baseline_workspace}/foss/numexpr"
ZIP="v%{version}.zip"
cp -v ${SRC_DIR}/${ZIP} \
   %{_python_build_loc}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null
cd %{_python_build_loc}
unzip ${ZIP}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
rm -fv ${ZIP}
if [ ! -d numexpr-%{version} ]; then
   echo "Directory numexpr-%{version} not found!"
   exit 1
fi
cd numexpr-%{version}
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
pushd . > /dev/null
cd %{_python_build_loc}/numexpr-%{version}
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
if [ ! -L /awips2/python/lib/libnumexpr.so ]; then
  ln -s /awips2/python/lib/python2.7/site-packages/numexpr/libnumexpr.so /awips2/python/lib/libnumexpr.so
fi

%preun

%postun

%clean
rm -rf %{_build_root}
rm -rf %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
/awips2/python/lib/python2.7/site-packages/numexpr*
%dir /awips2/python/lib/python2.7/site-packages/numexpr
