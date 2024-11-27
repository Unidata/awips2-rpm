%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _installed_python_numpy %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c "import numpy; print(numpy.__version__)"; else echo 0; fi)
%define _src_pkg_prefix Bottleneck
%define _build_id_links none

#
# AWIPS II Python Bottleneck Spec File
#

Name: awips2-python-bottleneck
Summary: AWIPS II Python Bottleneck Distribution
Epoch: 1
Version: 1.3.7
Release: %{_installed_python_short}.%{_installed_python_numpy}.2%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: ${_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: awips2-python >= %{_installed_python_short}
Requires: awips2-python-numpy

BuildRequires: awips2-python
BuildRequires: awips2-python-numpy
BuildRequires: awips2-python-setuptools

%description
AWIPS II Python Bottleneck Site-Package

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
rm -rf %{_python_build_loc}
mkdir -p %{_python_build_loc}

%build
SRC_DIR="%{_baseline_workspace}/foss/%{_src_pkg_prefix}-%{version}/packaged"

cp -v ${SRC_DIR}/%{_src_pkg_prefix}-%{version}.tar.gz %{_python_build_loc}
pushd . > /dev/null
cd %{_python_build_loc}
tar xf %{_src_pkg_prefix}-%{version}.tar.gz
cd %{_src_pkg_prefix}-%{version}

/awips2/python/bin/python setup.py build || exit 1
popd > /dev/null

%install
pushd . > /dev/null
cd %{_python_build_loc}/%{_src_pkg_prefix}-%{version}
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

%clean
rm -rf %{_build_root}
rm -rf %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
/awips2/python/lib/python%{_installed_python_short}/site-packages/*
