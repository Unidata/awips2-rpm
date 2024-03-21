# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)


#
# AWIPS II Python more_itertools Spec File
#

Name: awips2-python-more_itertools
Summary: AWIPS II Python more_itertools module
Version: 9.1.0
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
Requires: awips2-python >= %{_installed_python_short}

BuildRequires: awips2-python
BuildRequires: awips2-python-setuptools

%description
AWIPS II Python more_itertools Site-Package

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
SRC_DIR="%{_baseline_workspace}/foss/more_itertools-%{version}/packaged"
PACKAGE_FILE="more_itertools-%{version}-py3-none-any.whl"
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
/awips2/python/lib/python%{_installed_python_short}/site-packages/more_itertools
/awips2/python/lib/python%{_installed_python_short}/site-packages/more_itertools-%{version}.dist-info
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/more_itertools/__pycache__

%changelog
* Mon Jun 05 2023 David Gillingham <david.gillingham@rtx.com> 
- Initial package creation.
