# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _build_arch %(uname -i)
%define _build_id_links none

#
# AWIPS II Python pyresample Spec File
#

Name: awips2-python-pyresample
Summary: AWIPS II Python pyresample module
Epoch: 1
Version: 1.26.1
Release: %{_installed_python_short}.6%{?dist}
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
Requires: awips2-python-importlib-metadata
Requires: awips2-python-numpy >= 1.10.0
Requires: awips2-python-pykdtree >= 1.3.1
Requires: awips2-python-pyproj >= 3.0
Requires: awips2-python-shapely
Requires: python%{_installed_python_short}-pyyaml

BuildRequires: awips2-python
BuildRequires: awips2-python-cython

%description
AWIPS II Python pyresample Site-Package

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

if [ -d ${RPM_BUILD_ROOT} ]; then
   rm --recursive --force ${RPM_BUILD_ROOT}
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi

rm --recursive --force %{_build_root}
mkdir --parents %{_build_root}
if [ -d %{_python_build_loc} ]; then
   rm --recursive --force %{_python_build_loc}
fi
mkdir --parents %{_python_build_loc}


%build
SRC_DIR="%{_baseline_workspace}/foss/pyresample-%{version}/packaged"
PKG_FILE="pyresample-%{version}.tar.gz"
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
if [ ! -d pyresample-%{version} ]; then
   echo "Directory pyresample-%{version} not found!"
   exit 1
fi
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
cd pyresample-%{version}

/awips2/python/bin/python setup.py clean || exit 1

/awips2/python/bin/python setup.py build || exit 1

popd > /dev/null


%install
pushd . > /dev/null
cd %{_python_build_loc}/pyresample-%{version}
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
/awips2/python/lib/python%{_installed_python_short}/site-packages/pyresample
/awips2/python/lib/python%{_installed_python_short}/site-packages/pyresample-%{version}-py%{_installed_python_short}.egg-info
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/pyresample/__pycache__


%changelog
* Mon Mar 20 2023 Tom Gurney <thomas.gurney@rtx.com>
- Update to 1.26.1
* Thu Sep 2 2021 David Gillingham <david.gillingham@raytheon.com> 
- Change to RHEL official package python38-pyyaml.
* Thu Jul 15 2021 Lisa Singh <lisa.e.singh@raytheon.com> 
- Initial package creation.
