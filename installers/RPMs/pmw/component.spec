# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)

#
# AWIPS II Python pkgconfig Spec File
#
Name: awips2-python-pmw
Summary: AWIPS II Python Pmw Distribution
Epoch: 1
Version: 2.1
Release: %{_installed_python_short}.1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: noarch
URL: N/A
License: N/A
Distribution: N/A
Vendor: ${_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: awips2-python = %{_installed_python_short}

BuildRequires: awips2-python

%description
AWIPS II Python Python mega widgets (Pmw) Site-Package

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
_SRC_DIR="%{_baseline_workspace}/foss/pmw-%{version}/packaged"

cp --recursive --verbose ${_SRC_DIR}/Pmw-%{version}.tar.gz %{_python_build_loc}
pushd . > /dev/null
cd %{_python_build_loc}
tar --extract --file="Pmw-%{version}.tar.gz"
cd Pmw-%{version}

/awips2/python/bin/python setup.py build
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%install
pushd . > /dev/null
cd %{_python_build_loc}/Pmw-%{version}
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%clean
rm --recursive --force %{_build_root}
rm --recursive --force %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
/awips2/python/lib/python%{_installed_python_short}/site-packages/Pmw-%{version}-py%{_installed_python_short}.egg-info
/awips2/python/lib/python%{_installed_python_short}/site-packages/Pmw/*
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/Pmw/**/__pycache__
