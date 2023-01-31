# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)

#
# AWIPS II Python numpy Spec File
#
Name: awips2-python-numpy
Summary: AWIPS II Python numpy Distribution
Version: 1.16.2
Release: %{_installed_python}.1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: compat-libf2c-34(x86-64) >= 3.4.6-19.el7
Requires: libgfortran(x86-64) >= 4.4.7-3.el7
Requires: awips2-python = %{_installed_python}
Provides: awips2-python-numpy = %{version}

BuildRequires: awips2-python
BuildRequires: awips2-python-setuptools
BuildRequires: compat-libf2c-34(x86-64) >= 3.4.6-19.el7
BuildRequires: gcc
BuildRequires: libgfortran(x86-64) >= 4.4.7-3.el7

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
   echo "Directory numpy-%{version} not found!"
   exit 1
fi
source /etc/profile.d/awips2Python.sh
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
cd numpy-%{version}
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
/awips2/python/lib/python%{_installed_python_short}/site-packages/*
%defattr(755,awips,fxalpha,755)
/awips2/python/bin/*
