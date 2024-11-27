# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _build_id_links none

Name: awips2-python-contourpy
Summary: AWIPS II Python ContourPy module
Version: 1.0.7
Release: %{_installed_python_short}.2%{?dist}
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
Requires: awips2-python-numpy >= 1.16.0

BuildRequires: awips2-python
BuildRequires: awips2-meson
BuildRequires: awips2-python-meson_python
BuildRequires: awips2-python-setuptools

%description
AWIPS II Python ContourPy Site-Package

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
rm --recursive --force %{_python_build_loc}
mkdir --parents %{_python_build_loc}


%build
SRC_DIR="%{_baseline_workspace}/foss/contourpy-%{version}/packaged"
PACKAGE_FILE="contourpy-%{version}.tar.gz"

cp --verbose ${SRC_DIR}/${PACKAGE_FILE} %{_python_build_loc}
pushd . > /dev/null
cd %{_python_build_loc}
tar --extract --file=${PACKAGE_FILE}
cd contourpy-%{version}
/awips2/python/bin/python setup.py build || exit 1
popd > /dev/null


%install
pushd . > /dev/null
cd %{_python_build_loc}/contourpy-%{version}
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python \
   || exit 1
popd > /dev/null

# Merge lib64 into lib to avoid problems with installing into the virtualenv
if [ -d "%{_build_root}/awips2/python/lib64/" ]; then
    rsync --archive %{_build_root}/awips2/python/lib64/ %{_build_root}/awips2/python/lib || exit 1
    rm --recursive --force %{_build_root}/awips2/python/lib64
fi


%clean
rm --recursive --force %{_build_root}


%files
%defattr(644,awips,fxalpha,755)
/awips2/python/lib/python%{_installed_python_short}/site-packages/contourpy
/awips2/python/lib/python%{_installed_python_short}/site-packages/contourpy-%{version}-py%{_installed_python_short}.egg-info
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/contourpy/__pycache__

%changelog
* Thu Jun 08 2023 David Gillingham <david.gillingham@rtx.com> 
- Initial package creation.
