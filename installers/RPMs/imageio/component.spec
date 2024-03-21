# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)


#
# AWIPS II Python imageio Spec File
#

Name: awips2-python-imageio
Summary: AWIPS II Python imageio module
Epoch: 1
Version: 2.25.0
Release: %{_installed_python_short}.2%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: noarch
URL: N/A
License: N/A
Distribution: N/A
Vendor: ${_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: awips2-python >= %{_installed_python_short}
Requires: awips2-python-pillow
Requires: awips2-python-numpy

BuildRequires: awips2-python
BuildRequires: awips2-python-setuptools

%description
AWIPS II Python imageio Site-Package

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


%build


%install
pushd . > /dev/null
SRC_DIR="%{_baseline_workspace}/foss/imageio-%{version}/packaged"
PACKAGE_FILE="imageio-%{version}-py3-none-any.whl"
/awips2/python/bin/pip3 install \
   --disable-pip-version-check --verbose --no-deps --ignore-installed --no-index \
   --root %{_build_root} --prefix /awips2/python \
   "${SRC_DIR}/${PACKAGE_FILE}"
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


%files
%defattr(644,awips,fxalpha,755)
/awips2/python/lib/python%{_installed_python_short}/site-packages/imageio
/awips2/python/lib/python%{_installed_python_short}/site-packages/imageio-%{version}.dist-info
/awips2/python/bin/imageio_*
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/imageio/__pycache__
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/imageio/*/__pycache__

%changelog
* Fri Mar 10 2023 john.sebahar <john.sebahar@raytheon.com>
- Upgrade imageio to version 2.25.0.
* Thu Jul 15 2021 Lisa Singh <lisa.e.singh@raytheon.com> 
- Initial package creation.
