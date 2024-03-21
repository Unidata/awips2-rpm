# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)

#
# AWIPS II Python numpy Spec File
#
Name: awips2-python-numpy
Summary: AWIPS II Python numpy Distribution
Epoch: 1
Version: 1.23.5
Release: %{_installed_python_short}.1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: libgfortran(x86-64) >= 4.4.7-3.el7
Requires: awips2-python >= %{_installed_python_short}
Requires: blas
Requires: lapack
Provides: awips2-python-numpy = %{version}

BuildRequires: blas-devel
BuildRequires: lapack-devel
BuildRequires: awips2-python
BuildRequires: libgfortran(x86-64) >= 4.4.7-3.el7
BuildRequires: gcc

%description
AWIPS II Python numpy Site-Package

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
NUMPY_SRC_DIR="%{_baseline_workspace}/foss/numpy-%{version}/packaged"
NUMPY_PKG="numpy-%{version}.tar.gz"
cp --verbose ${NUMPY_SRC_DIR}/${NUMPY_PKG} %{_python_build_loc} || exit 1

pushd . > /dev/null
cd %{_python_build_loc}
tar --extract --file="${NUMPY_PKG}" || exit 1
rm --force --verbose ${NUMPY_PKG} || exit 1
if [ ! -d numpy-%{version} ]; then
   echo "Directory numpy-%{version} not found!"
   exit 1
fi
source /etc/profile.d/awips2Python.sh || exit 1
cd numpy-%{version} || exit 1
/awips2/python/bin/python setup.py build || exit 1
popd > /dev/null

%install
pushd . > /dev/null
cd %{_python_build_loc}/numpy-%{version} || exit 1
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
/awips2/python/lib/python%{_installed_python_short}/site-packages/*
%defattr(755,awips,fxalpha,755)
/awips2/python/bin/*
