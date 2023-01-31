# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)

#
# AWIPS II Python Cheroot Spec File
#

Name: awips2-python-cheroot
Summary: AWIPS II Python Cheroot Distribution
Version: 6.5.5
Release: %{_installed_python}.2%{?dist}
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
Provides: awips2-python-cheroot = %{version}

BuildRequires: awips2-python
BuildRequires: awips2-python-setuptools
BuildRequires: awips2-python-setuptools_scm
BuildRequires: awips2-python-setuptools_scm_git_archive

%description
AWIPS II Python Cheroot Site-Package

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
SRC_DIR="%{_baseline_workspace}/foss/cheroot-%{version}/packaged"

cp -rv ${SRC_DIR}/cheroot-%{version}.tar.gz %{_python_build_loc}
pushd . > /dev/null
cd %{_python_build_loc}
tar xf cheroot-%{version}.tar.gz
cd cheroot-%{version}

# This patch is required to make cheroot versions earlier than 8.0.0 build and
# install with setuptools 41.4 or later. After cheroot is upgraded to 8.0.0 or
# later, remove this patch.
patch -u -i "${SRC_DIR}/setup.py_8.0.0.patch" || exit 1

/awips2/python/bin/python setup.py clean || exit 1
/awips2/python/bin/python setup.py build || exit 1

popd > /dev/null

%install
pushd . > /dev/null
cd %{_python_build_loc}/cheroot-%{version}
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
%defattr(755,awips,fxalpha,755)
/awips2/python/bin/*
