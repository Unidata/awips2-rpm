# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _installed_python_numpy %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c "import numpy; print(numpy.__version__)"; else echo 0; fi)

#
# AWIPS II Python matplotlib Spec File
#
Name: awips2-python-matplotlib
Summary: AWIPS II Python matplotlib Distribution
Version: 2.2.4
Release: %{_installed_python}.%{_installed_python_numpy}.1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: Raytheon
Packager: %{_build_site}

AutoReq: no
Requires: awips2-python = %{_installed_python}
Requires: awips2-python-numpy = %{_installed_python_numpy}
Requires: awips2-python-six
Requires: awips2-python-dateutil
Requires: awips2-python-pytz
Requires: awips2-python-pyparsing
Requires: awips2-python-cycler
Requires: awips2-python-kiwisolver
Requires: awips2-python-backports-lru_cache
Requires: libpng
Requires: freetype
Provides: awips2-python-matplotlib = %{version}

BuildRequires: awips2-python
BuildRequires: awips2-python-setuptools
BuildRequires: awips2-python-numpy
BuildRequires: awips2-python-dateutil
BuildRequires: awips2-python-pyparsing
BuildRequires: awips2-python-six
BuildRequires: awips2-python-pytz
BuildRequires: freetype-devel
BuildRequires: gcc-c++
BuildRequires: libpng

%description
AWIPS II Python matplotlib Site-Package

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm -rf %{_build_root}
mkdir -p %{_build_root}

rm -rf %{_build_root}
mkdir -p %{_build_root}
if [ -d %{_python_build_loc} ]; then
   rm -rf %{_python_build_loc}
fi
mkdir -p %{_python_build_loc}

%build
MATPLOTLIB_DIR="%{_baseline_workspace}/foss/matplotlib-%{version}"
MATPLOTLIB_SRC_DIR="${MATPLOTLIB_DIR}/packaged"

cp --recursive --verbose ${MATPLOTLIB_SRC_DIR}/matplotlib-%{version}.tar.gz %{_python_build_loc}
pushd . > /dev/null
cd %{_python_build_loc}
tar --extract --file=matplotlib-%{version}.tar.gz
cd matplotlib-%{version}

# install our setup.cfg template which disables the GTK3 backends due to issues
# with Jep and Hazard Services.
# Refer to DR #7827
cp --verbose "${MATPLOTLIB_DIR}/setup.cfg" .

/awips2/python/bin/python setup.py build
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%install
pushd . > /dev/null
mkdir -p "%{_build_root}/awips2/python/lib/python%{_installed_python_short}/site-packages/matplotlib/backends/web_backend/"
unzip -u -o -d "%{_build_root}/awips2/python/lib/python%{_installed_python_short}/site-packages/matplotlib/backends/web_backend/" "%{_baseline_workspace}/foss/jquery-ui-1.12.1/packaged/jquery-ui-1.12.1.zip"
cd %{_python_build_loc}/matplotlib-%{version}
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%clean
rm -rf %{_build_root}
rm -rf %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
/awips2/python/lib/python%{_installed_python_short}/site-packages/* 
