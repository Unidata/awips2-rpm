# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python_numpy %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c "import numpy; print(numpy.__version__)"; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _build_id_links none

#
# AWIPS II Python scipy Spec File
#
Name: awips2-python-scipy
Summary: AWIPS II Python scipy Distribution
Epoch: 1
Version: 1.10.1
Release: %{_installed_python_short}.%{_installed_python_numpy}.4%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: blas
Requires: lapack
Requires: awips2-python >= %{_installed_python_short}
Requires: awips2-python-numpy >= 1.19.5
Provides: awips2-python-scipy = %{version}

BuildRequires: blas-devel
BuildRequires: lapack-devel
BuildRequires: awips2-python
BuildRequires: awips2-python-numpy >= 1.19.5

%description
AWIPS II Python scipy Site-Package

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
if [ -d %{_python_build_loc} ]; then
   rm --recursive --force %{_python_build_loc} || exit 1
fi
mkdir --parents %{_python_build_loc} || exit 1

%build
export SETUPTOOLS_USE_DISTUTILS=stdlib

SCIPY_SRC_DIR="%{_baseline_workspace}/foss/scipy-%{version}/packaged"
cp -v ${SCIPY_SRC_DIR}/scipy-%{version}.tar.gz %{_python_build_loc} || exit 1

source /etc/profile.d/awips2Python.sh || exit 1
cp -v ${SCIPY_SRC_DIR}/* %{_python_build_loc} || exit 1

source /etc/profile.d/awips2Python.sh || exit 1

pushd . > /dev/null
cd %{_python_build_loc}
tar --extract --verbose --file=scipy-%{version}.tar.gz || exit 1
cd scipy-%{version} || exit 1

# Apply patch to prevent submodule imports from hanging in jep sub-interpreters.
# See jep ticket for more info: https://github.com/ninia/jep/issues/487
patch scipy/__init__.py %{_baseline_workspace}/installers/RPMs/scipy/patches/scipy-%{version}-__init__.py.patch || exit 1

# pythran pulls in several more dependencies so we will disable it until it is
# determined to be desired for awips2
SCIPY_USE_PYTHRAN=0 CFLAGS=-std=c99 /awips2/python/bin/python setup.py build || exit 1
popd > /dev/null
unset SETUPTOOLS_USE_DISTUTILS

%install
# Force setuptools to use the stdlib version of distutils when building this foss.
# This will need removed when python is upgraded to >= 3.12.
export SETUPTOOLS_USE_DISTUTILS=stdlib

pushd . > /dev/null
cd %{_python_build_loc}/scipy-%{version} || exit 1
# pythran pulls in several more dependencies so we will disable it until it is
# determined to be desired for awips2
SCIPY_USE_PYTHRAN=0 CFLAGS=-std=c99 /awips2/python/bin/python setup.py install --root=%{_build_root} --prefix=/awips2/python || exit 1
popd > /dev/null

# Merge lib64 into lib to avoid problems with installing into the virtualenv
if [ -d "%{_build_root}/awips2/python/lib64/" ]; then
    rsync --archive %{_build_root}/awips2/python/lib64/ %{_build_root}/awips2/python/lib || exit 1
    rm --recursive --force %{_build_root}/awips2/python/lib64
fi
unset SETUPTOOLS_USE_DISTUTILS

%clean
rm --recursive --force %{_build_root}
rm --recursive --force %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
/awips2/python/lib/python%{_installed_python_short}/site-packages/*
