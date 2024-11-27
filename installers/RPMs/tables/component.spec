# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _installed_python_numpy %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c "import numpy; print(numpy.__version__)"; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _build_id_links none

#
# AWIPS II Python PyTables Spec File
#
Name: awips2-python-tables
Summary: AWIPS II Python PyTables Distribution
Epoch: 1
Version: 3.8.0
Release: %{_installed_python_short}.3%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: awips2-hdf5 >= 1.12.0
Requires: awips2-python >= %{_installed_python_short}
Requires: awips2-python-numexpr >= 2.6.2
Requires: awips2-python-numpy >= 1.19.0
Requires: awips2-python-py_cpuinfo
Requires: awips2-python-blosc2 >= 2.0.0
Requires: python%{_installed_python_short}-packaging
Requires: lzo
Requires: zlib
Requires: bzip2

BuildRequires: awips2-hdf5-devel
BuildRequires: awips2-python
BuildRequires: awips2-python-setuptools
BuildRequires: python%{_installed_python_short}-wheel
BuildRequires: python%{_installed_python_short}-packaging
BuildRequires: awips2-python-py_cpuinfo
BuildRequires: awips2-python-cython
BuildRequires: awips2-python-numexpr
BuildRequires: awips2-python-numpy
BuildRequires: awips2-python-blosc2
BuildRequires: lzo-devel
BuildRequires: zlib-devel
BuildRequires: bzip2-devel
BuildRequires: gcc-c++

%description
AWIPS II Python PyTables Site-Package

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
if [ -d %{_python_build_loc} ]; then
   rm --recursive --force %{_python_build_loc}
fi
mkdir --parents %{_python_build_loc}

%build

TABLES_SRC_DIR="%{_baseline_workspace}/foss/tables-%{version}/packaged"
TABLES_TAR="tables-%{version}.tar.gz"
cp --verbose ${TABLES_SRC_DIR}/${TABLES_TAR} \
   %{_python_build_loc} || exit 1

pushd . > /dev/null
cd %{_python_build_loc}
tar --extract --verbose --file=${TABLES_TAR} || exit 1
rm --recursive --force ${TABLES_TAR}
if [ ! -d tables-%{version} ]; then
   echo "Directory tables-%{version} not found!"
   exit 1
fi
cd tables-%{version}
/awips2/python/bin/python setup.py build \
   --hdf5=/awips2/hdf5 \
   --lflags="-Xlinker -rpath -Xlinker /awips2/hdf5/lib" || exit 1

popd > /dev/null

%install

pushd . > /dev/null
cd %{_python_build_loc}/tables-%{version}
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python \
   --hdf5=/awips2/hdf5 || exit 1

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
