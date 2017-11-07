%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#
# AWIPS II Python matplotlib Spec File
#
Name: awips2-python-matplotlib
Summary: AWIPS II Python matplotlib Distribution
Version: 1.5.1
Release: 2
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: awips2-python
Requires: awips2-python-numpy
Requires: awips2-python-six
Requires: awips2-python-dateutil
Requires: awips2-python-pytz
Requires: awips2-python-pyparsing
Requires: libpng, freetype
Provides: awips2-python-matplotlib

BuildRequires: awips2-python
BuildRequires: awips2-python-setuptools
BuildRequires: awips2-python-numpy
BuildRequires: awips2-python-dateutil
BuildRequires: awips2-python-pyparsing
BuildRequires: awips2-python-six
BuildRequires: awips2-python-pytz
BuildRequires: libpng, freetype

%description
AWIPS II Python matplotlib Site-Package

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

rm -rf %{_build_root}
mkdir -p %{_build_root}
if [ -d %{_python_build_loc} ]; then
   rm -rf %{_python_build_loc}
fi
mkdir -p %{_python_build_loc}

%build
MATPLOTLIB_SRC_DIR="%{_baseline_workspace}/foss/matplotlib"

cp -rv ${MATPLOTLIB_SRC_DIR}/matplotlib-%{version}.tar.gz %{_python_build_loc}
pushd . > /dev/null
cd %{_python_build_loc}
tar xf matplotlib-%{version}.tar.gz
cd matplotlib-%{version}

#create setup.cfg and require pytz build
cp -v setup.cfg.template setup.cfg
sed -i 's/#pytz = False/pytz = True/g' setup.cfg

export LD_LIBRARY_PATH=/awips2/python/lib
/awips2/python/bin/python setup.py build
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%install
pushd . > /dev/null
cd %{_python_build_loc}/matplotlib-%{version}
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
