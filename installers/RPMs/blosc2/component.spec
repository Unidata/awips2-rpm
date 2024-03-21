# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)


Name: awips2-python-blosc2
Summary: AWIPS II Python Blosc2 module
Version: 2.0.0 
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
Requires: awips2-python-msgpack

BuildRequires: awips2-python
BuildRequires: awips2-python-setuptools

%description
AWIPS II Python Blosc2 Site-Package

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
SRC_DIR="%{_baseline_workspace}/foss/blosc2-%{version}/packaged"
# Using a wheel file for this because it has multiple build dependencies that we did not want to add
PACKAGE_FILE="blosc2-%{version}-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"
/awips2/python/bin/pip3 install \
   --disable-pip-version-check --verbose --no-deps --ignore-installed --no-index \
   --root %{_build_root} --prefix /awips2/python \
   "${SRC_DIR}/${PACKAGE_FILE}" || exit 1

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
/awips2/python/lib/*
/awips2/python/include/*
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/blosc2/__pycache__

%changelog
* Thu Jun 15 2023 John Sebahar <john.sebahar@rtx.com> 
- Initial package creation.

