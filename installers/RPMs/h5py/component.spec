# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python_numpy %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c "import numpy; print(numpy.__version__)"; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _build_id_links none

#
# AWIPS II Python h5py Spec File
#
Name: awips2-python-h5py
Summary: AWIPS II Python h5py Distribution
Epoch: 1
Version: 3.8.0
Release: %{_installed_python_short}.%{_installed_python_numpy}.3%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}
Requires: awips2-python >= %{_installed_python_short}
Requires: awips2-python-numpy
Requires: libz.so.1

BuildRequires: awips2-hdf5
BuildRequires: awips2-hdf5-devel
BuildRequires: awips2-python
BuildRequires: awips2-python-pkgconfig
BuildRequires: awips2-python-cython
BuildRequires: awips2-python-numpy
BuildRequires: gcc
BuildRequires: python%{_installed_python_short}-pip
BuildRequires: awips2-python-setuptools
BuildRequires: python%{_installed_python_short}-six
BuildRequires: python%{_installed_python_short}-wheel

%description
AWIPS II Python h5py Site-Package

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm -rf %{_build_root}
if [ $? -ne 0 ]; then
   exit 1
fi
mkdir -p %{_build_root}
if [ $? -ne 0 ]; then
   exit 1
fi
mkdir -p %{_build_root}/awips2/python/lib
if [ $? -ne 0 ]; then
   exit 1
fi

if [ -d %{_python_build_loc} ]; then
   rm -rf %{_python_build_loc}
fi
mkdir -p %{_python_build_loc}

%build


%install
H5PY_SRC_DIR="%{_baseline_workspace}/foss/h5py-%{version}/packaged/"

# Copy the h5py source.
cp -rv ${H5PY_SRC_DIR}/* \
   %{_python_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null
cd %{_python_build_loc}
tar xvzf h5py-%{version}.tar.gz
if [ $? -ne 0 ]; then
   exit 1
fi

cd %{_python_build_loc}/h5py-%{version}
HDF5_DIR=/awips2/hdf5 H5PY_SETUP_REQUIRES=0 /awips2/python/bin/pip3 install \
   --disable-pip-version-check --verbose --no-deps --ignore-installed --no-index --no-build-isolation \
   --root %{_build_root} --prefix /awips2/python .
popd > /dev/null

# Merge lib64 into lib to avoid problems with installing into the virtualenv
if [ -d "%{_build_root}/awips2/python/lib64/" ]; then
    rsync -a %{_build_root}/awips2/python/lib64/ %{_build_root}/awips2/python/lib || exit 1
    rm -rf %{_build_root}/awips2/python/lib64
fi

%clean
rm -rf ${RPM_BUILD_ROOT}
rm -rf %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
/awips2/python/lib/python%{_installed_python_short}/site-packages/*
