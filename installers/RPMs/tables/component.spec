# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_numpy %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c "import numpy; print(numpy.__version__)"; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)

#
# AWIPS II Python PyTables Spec File
#
Name: awips2-python-tables
Summary: AWIPS II Python PyTables Distribution
Version: 3.5.1
Release: %{_installed_python}.%{_installed_python_numpy}.1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: Raytheon
Packager: %{_build_site}

AutoReq: no
Requires: awips2-hdf5
Requires: awips2-python = %{_installed_python}
Requires: awips2-python-numpy = %{_installed_python_numpy}
Requires: awips2-python-mock
Requires: awips2-python-numexpr
Requires: awips2-python-six
Provides: awips2-python-tables = %{version}

BuildRequires: awips2-hdf5-devel
BuildRequires: awips2-python
BuildRequires: awips2-python-cython
BuildRequires: awips2-python-mock
BuildRequires: awips2-python-numexpr
BuildRequires: awips2-python-numpy
BuildRequires: awips2-python-setuptools
BuildRequires: awips2-python-six
BuildRequires: bzip2-devel
BuildRequires: gcc-c++

%description
AWIPS II Python PyTables Site-Package

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

TABLES_SRC_DIR="%{_baseline_workspace}/foss/tables-%{version}/packaged"
TABLES_TAR="PyTables-%{version}.tar.gz"
cp -v ${TABLES_SRC_DIR}/${TABLES_TAR} \
   %{_python_build_loc}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null
cd %{_python_build_loc}
tar -xvf ${TABLES_TAR}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
rm -fv ${TABLES_TAR}
if [ ! -d PyTables-%{version} ]; then
   echo "Directory PyTables-%{version} not found!"
   exit 1
fi
cd PyTables-%{version}
/awips2/python/bin/python setup.py build \
   --hdf5=/awips2/hdf5
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%install

pushd . > /dev/null
cd %{_python_build_loc}/PyTables-%{version}
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python \
   --hdf5=/awips2/hdf5
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
