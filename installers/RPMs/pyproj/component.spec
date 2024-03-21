%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)


Name: awips2-python-pyproj
Summary: AWIPS II Python pyproj Distribution
Epoch: 1
Version: 3.4.1
Release: %{_installed_python_short}.1%{?dist}
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
Requires: awips2-python-proj >= 8.2
Requires: awips2-python-certifi

BuildRequires: awips2-python
BuildRequires: awips2-python-proj >= 8.2

%description
AWIPS II Python pyproj Site-Package

%prep
# Verify that the user has specified a build root
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm --recursive --force %{_build_root}
mkdir --parents %{_build_root}
if [ -d %{_python_build_loc} ]; then
   rm --recursive --force %{_python_build_loc}
fi
mkdir --parents %{_python_build_loc}

%build
SRC_DIR="%{_baseline_workspace}/foss/pyproj-%{version}/packaged"
PKG_FILE="pyproj-%{version}.tar.gz"
cp --verbose ${SRC_DIR}/${PKG_FILE} \
   %{_python_build_loc}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null
cd %{_python_build_loc}
tar --extract --file ${PKG_FILE}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
rm --force --verbose ${PKG_FILE}
if [ ! -d pyproj-%{version} ]; then
   echo "Directory pyproj-%{version} not found!"
   exit 1
fi
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
cd pyproj-%{version}

/awips2/python/bin/python setup.py clean || exit 1

/awips2/python/bin/python setup.py build || exit 1

popd > /dev/null

%install
pushd . > /dev/null
cd %{_python_build_loc}/pyproj-%{version}
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
rm --recursive --force %{_build_root}
rm --recursive --force %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
/awips2/python/bin/pyproj
/awips2/python/lib/python%{_installed_python_short}/site-packages/pyproj
/awips2/python/lib/python%{_installed_python_short}/site-packages/pyproj-%{version}-py%{_installed_python_short}.egg-info

%changelog
* Mon Mar 20 2023 Tom Gurney <thomas.gurney@rtx.com>
- Upgrade to 3.4.1
* Fri Jul 23 2021 Nate Jensen <nate.jensen@raytheon.com>
- Build and install from source instead of from wheel
* Thu May 20 2021 Tom Gurney <tom.gurney@raytheon.com> 
- Initial creation

