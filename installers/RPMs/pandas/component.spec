%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _installed_python_numpy %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c "import numpy; print(numpy.__version__)"; else echo 0; fi)
%define _build_id_links none

#
# AWIPS II Python Pandas Spec File
#
Name: awips2-python-pandas
Summary: AWIPS II Python pandas Distribution
Epoch: 1
Version: 1.3.5
Release: %{_installed_python_short}.%{_installed_python_numpy}.2%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: http://pandas.pydata.org/
License: BSD
Vendor: ${_build_vendor}

AutoReq: no
Requires: awips2-python >= %{_installed_python_short}
Requires: awips2-python-bottleneck
Requires: awips2-python-numpy >= 1.17.3
Requires: awips2-python-dateutil >= 2.7.3
Requires: awips2-python-pytz >= 2017.3

BuildRequires: awips2-python
BuildRequires: awips2-python-numpy
BuildRequires: awips2-python-cython

%description
AWIPS II Python pandas Site-Package

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm --recursive --force %{_build_root}
mkdir --parents %{_build_root}

rm --recursive --force %{_build_root}
mkdir --parents %{_build_root}
if [ -d %{_python_build_loc} ]; then
   rm --recursive --force %{_python_build_loc}
fi
mkdir --parents %{_python_build_loc}

%build
PANDAS_SRC_DIR="%{_baseline_workspace}/foss/pandas-%{version}/packaged"
PANDAS_TAR="pandas-%{version}.tar.gz"

cp --recursive --verbose ${PANDAS_SRC_DIR}/${PANDAS_TAR} %{_python_build_loc}
pushd . > /dev/null
cd %{_python_build_loc}
tar --extract --file="${PANDAS_TAR}"
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
rm --force --verbose ${PANDAS_TAR}
if [ ! -d pandas-%{version} ]; then
   echo "Directory pandas-%{version} not found!"
   exit 1
fi

source /etc/profile.d/awips2Python.sh
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
cd pandas-%{version}

/awips2/python/bin/python setup.py build
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%install
pushd . > /dev/null
cd %{_python_build_loc}/pandas-%{version}
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

# Merge lib64 into lib to avoid problems with installing into the virtualenv
if [ -d "%{_build_root}/awips2/python/lib64/" ]; then
    rsync --archive %{_build_root}/awips2/python/lib64/ %{_build_root}/awips2/python/lib || exit 1
    rm --recursive --force %{_build_root}/awips2/python/lib64
fi

%pre

%post

%preun

%postun

%clean
rm --recursive --force %{_build_root}
rm --recursive --force %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/python/lib/python%{_installed_python_short}/site-packages/pandas
/awips2/python/lib/python%{_installed_python_short}/site-packages/pandas/*
%dir /awips2/python/lib/python%{_installed_python_short}/site-packages/pandas-%{version}-py%{_installed_python_short}.egg-info
/awips2/python/lib/python%{_installed_python_short}/site-packages/pandas-%{version}-py%{_installed_python_short}.egg-info/*
