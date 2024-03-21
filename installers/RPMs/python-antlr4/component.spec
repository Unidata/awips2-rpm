# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _pkgname antlr4-python3-runtime

Name: awips2-python-antlr4
Summary: AWIPS II Python ANTLR 4 Runtime Distribution
Epoch: 1
Version: 4.7.2
Release: %{_installed_python_short}.2%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Vendor: ${_build_vendor}

AutoReq: no
Requires: awips2-python >= %{_installed_python_short}

BuildRequires: awips2-python
BuildRequires: awips2-python-setuptools

%description
AWIPS II Python %{_pkgname} Site-Package

%prep
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
src_dir="%{_baseline_workspace}/foss/%{_pkgname}-%{version}/packaged"
tarball="%{_pkgname}-%{version}.tar.gz"

cp --verbose "${src_dir}/${tarball}" %{_python_build_loc}
pushd . > /dev/null
cd %{_python_build_loc}
tar --extract --file="${tarball}" || exit 1
rm --force --verbose "${tarball}"
if [ ! -d "%{_pkgname}-%{version}" ]; then
   echo "Directory %{_pkgname}-%{version} not found!"
   exit 1
fi

source /etc/profile.d/awips2Python.sh || exit 1
cd "%{_pkgname}-%{version}"

/awips2/python/bin/python setup.py build || exit 1
popd > /dev/null

%install
pushd . > /dev/null
cd %{_python_build_loc}/%{_pkgname}-%{version}
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
/awips2/python/lib/python%{_installed_python_short}/site-packages/antlr4
/awips2/python/lib/python%{_installed_python_short}/site-packages/antlr4_python3_runtime-%{version}-py%{_installed_python_short}.egg-info/
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/antlr4/__pycache__
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/antlr4/**/__pycache__

%changelog
* Wed Aug 11 2021 Tom Gurney <tom.gurney@raytheon.com>
- Initial creation
