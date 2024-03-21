# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)

#
# AWIPS II Python Cython Spec File
#
Name: awips2-python-cython
Summary: AWIPS II Python Cython Distribution
Epoch: 1
Version: 0.29.34
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
Requires: awips2-python >= %{_installed_python_short}

BuildRequires: awips2-python
BuildRequires: gcc

%description
AWIPS II Python Cython Site-Package

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

rm --recursive --force %{_build_root}
mkdir --parents %{_build_root}
if [ -d %{_python_build_loc} ]; then
   rm --recursive --force %{_python_build_loc}
fi
mkdir --parents %{_python_build_loc}

%build
CYTHON_SRC_DIR="%{_baseline_workspace}/foss/cython-%{version}/packaged"

cp --recursive --verbose ${CYTHON_SRC_DIR}/Cython-%{version}.tar.gz %{_python_build_loc}
pushd . > /dev/null
cd %{_python_build_loc}
tar --extract --file=Cython-%{version}.tar.gz
cd Cython-%{version}

/awips2/python/bin/python setup.py build
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%install
pushd . > /dev/null
cd %{_python_build_loc}/Cython-%{version}
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

# Merge lib64 into lib to avoid problems with installing into the virtualenv
if [ -d "%{_build_root}/awips2/python/lib64/" ]; then
    rsync -a %{_build_root}/awips2/python/lib64/ %{_build_root}/awips2/python/lib || exit 1
    rm -rf %{_build_root}/awips2/python/lib64
fi

%clean
rm --recursive --force %{_build_root}
rm --recursive --force %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
/awips2/python/lib/python%{_installed_python_short}/site-packages/*
%defattr(755,awips,fxalpha,755)
/awips2/python/bin/*
