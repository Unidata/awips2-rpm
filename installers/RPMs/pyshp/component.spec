%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)

#
# AWIPS II Python Shapefile Library Spec File
#
Name: awips2-python-pyshp
Summary: AWIPS II Python Shapefile Library Distribution
Version: 1.2.11
Release: 2.%{_installed_python}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: https://github.com/GeospatialPython/pyshp
License: N/A
Vendor: %{_build_vendor}

AutoReq: no
Requires: awips2-python = %{_installed_python}
Provides: awips2-python-pyshp = %{version}

BuildRequires: awips2-python
BuildRequires: awips2-python-setuptools

%description
AWIPS II Python Shapefile Library Site-Package

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
PYSHP_SRC_DIR="%{_baseline_workspace}/foss/pyshp-%{version}/packaged"
PYSHP_TAR="pyshp-%{version}.tar.gz"

cp -rv ${PYSHP_SRC_DIR}/${PYSHP_TAR} %{_python_build_loc}
pushd . > /dev/null
cd %{_python_build_loc}
tar xf ${PYSHP_TAR}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
rm -fv ${PYSHP_TAR}
if [ ! -d pyshp-%{version} ]; then
   echo "Directory pyshp-%{version} not found!"
   exit 1
fi

source /etc/profile.d/awips2Python.sh
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
cd pyshp-%{version}

/awips2/python/bin/python setup.py build
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%install
pushd . > /dev/null
cd %{_python_build_loc}/pyshp-%{version}
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
/awips2/python/lib/python%{_installed_python_short}/site-packages/shapefile.py
/awips2/python/lib/python%{_installed_python_short}/site-packages/__pycache__/*
%dir /awips2/python/lib/python%{_installed_python_short}/site-packages/pyshp-%{version}-py%{_installed_python_short}.egg-info
/awips2/python/lib/python%{_installed_python_short}/site-packages/pyshp-%{version}-py%{_installed_python_short}.egg-info/*
