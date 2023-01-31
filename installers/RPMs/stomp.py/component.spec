# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)

#
# AWIPS II Python stomp.py Spec File
#

Name: awips2-python-stomp.py
Summary: AWIPS II Python stomp.py Distribution
Version: 4.1.22
Release: %{_installed_python}.1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: noarch
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: awips2-python = %{_installed_python}
Provides: awips2-python-stomp.py = %{version}

BuildRequires: awips2-python
BuildRequires: awips2-python-setuptools

%description
AWIPS II Python stomp.py Site-Package

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

if [ -d ${RPM_BUILD_ROOT} ]; then
   rm -rf ${RPM_BUILD_ROOT}
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi

rm -rf %{_build_root}
mkdir -p %{_build_root}
if [ -d %{_build_root}/build-python ]; then
   rm -rf %{_build_root}/build-python
fi
mkdir -p %{_build_root}/build-python
if [ -d %{_python_build_loc} ]; then
   rm -rf %{_python_build_loc}
fi
mkdir -p %{_python_build_loc}

%build
SRC_DIR="%{_baseline_workspace}/foss/stomp.py-%{version}/packaged"

cp -rv ${SRC_DIR}/stomp.py-%{version}.tar.gz %{_python_build_loc}
pushd . > /dev/null
cd %{_python_build_loc}
tar xf stomp.py-%{version}.tar.gz
cd stomp.py-%{version}

/awips2/python/bin/python setup.py build
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%install
# To avoid needing to install the dependency for the docopt library we
# avoid using the install command. Using install_lib and install_egg_info
# avoids the dependency checking.
# docopt is only needed for a CLI client that we do not use in AWIPS.
# See: __main__.py in the stomp.py distribution.
pushd . > /dev/null
cd %{_python_build_loc}/stomp.py-%{version}
/awips2/python/bin/python setup.py install_lib \
   --install-dir=%{_build_root}/awips2/python/lib/python%{_installed_python_short}/site-packages
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
/awips2/python/bin/python setup.py install_egg_info \
   --install-dir=%{_build_root}/awips2/python/lib/python%{_installed_python_short}/site-packages
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
