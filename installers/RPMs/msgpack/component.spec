# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)

Name: awips2-python-msgpack
Summary: AWIPS II Msgpack  Distribution
Version: 1.0.5
Release: %{_component_version}.%{_component_release}%{?dist}
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

BuildRequires: awips2-python
BuildRequires: awips2-python-setuptools
BuildRequires: gcc-c++

%description
AWIPS II Msgpack Package

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm --recursive --force %{_build_root} || exit 1
mkdir --parents %{_build_root} || exit 1
rm --recursive --force %{_python_build_loc} || exit 1
mkdir --parents %{_python_build_loc} || exit 1

%build
SRC_DIR="%{_baseline_workspace}/foss/msgpack-%{version}/packaged"
SRC_PACKAGE="msgpack-%{version}.tar.gz"
cp --verbose ${SRC_DIR}/${SRC_PACKAGE} %{_python_build_loc} || exit 1

pushd . > /dev/null
cd %{_python_build_loc}
tar --verbose --extract --gzip --file="${SRC_PACKAGE}" || exit 1
rm --force --verbose ${SRC_PACKAGE} || exit 1
cd msgpack-%{version} || exit 1
/awips2/python/bin/python setup.py build || exit 1
popd > /dev/null

%install
pushd . > /dev/null
cd %{_python_build_loc}/msgpack-%{version} || exit 1
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python || exit 1
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
/awips2/python/lib/python%{_installed_python_short}/site-packages/msgpack/*
/awips2/python/lib/python%{_installed_python_short}/site-packages/msgpack-%{version}-py%{_installed_python_short}.egg-info/*

%changelog
* Fri Jun 09 2023 John Sebahar <john.sebahar@raytheon.com>
- Initial package creation.

