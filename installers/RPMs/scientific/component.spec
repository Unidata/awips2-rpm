%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#
# AWIPS II Python scientific Spec File
#
Name: awips2-python-scientific
Summary: AWIPS II Python scientific Distribution
Version: 2.8
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
Requires: netcdf >= 3.0.0
Provides: awips2-python-scientific = %{version}

BuildRequires: awips2-python
BuildRequires: netcdf

%description
AWIPS II Python scientific Site-Package

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
SCIENTIFIC_SRC_DIR="%{_baseline_workspace}/foss/scientific-%{version}/packaged"

cp -rv ${SCIENTIFIC_SRC_DIR}/* \
   %{_python_build_loc}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null
cd %{_python_build_loc}
tar xvzf scientific-%{version}.tar.gz
cd scientific-%{version}
export LD_LIBRARY_PATH=/awips2/python/lib
/awips2/python/bin/python setup.py build
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%install

pushd . > /dev/null
cd %{_python_build_loc}
cd scientific-%{version}
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
%defattr(644,awips,awips,755)
%dir /awips2/python/lib/python2.7/site-packages/Scientific
/awips2/python/lib/python2.7/site-packages/Scientific/*
/awips2/python/lib/python2.7/site-packages/ScientificPython-2.8-py2.7.egg-info
/awips2/python/include/python2.7/Scientific/*
%defattr(755,awips,awips,755)
/awips2/python/bin/bsp_virtual
/awips2/python/bin/task_manager
