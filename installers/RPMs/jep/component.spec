%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_numpy %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c "import numpy; print numpy.__version__"; else echo 0; fi)

#
# AWIPS II Python Jep Spec File
#
Name: awips2-python-jep
Summary: AWIPS II Python Jep Distribution
Version: 3.4.1
Release: 1.el6
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
Provides: awips2-python-jep = %{version}

BuildRequires: awips2-python
BuildRequires: awips2-python-numpy
BuildRequires: awips2-java

%description
AWIPS II Python Jep Site-Package

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
if [ -d %{_python_build_loc} ]; then
   rm -rf %{_python_build_loc}
fi
mkdir -p %{_python_build_loc}

%build
JEP_SRC_DIR="%{_baseline_workspace}/foss/jep-%{version}/packaged"
JEP_ZIP="jep-%{version}.zip"
cp -v ${JEP_SRC_DIR}/${JEP_ZIP} \
   %{_python_build_loc}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null
cd %{_python_build_loc}
unzip ${JEP_ZIP}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
rm -fv ${JEP_ZIP}
if [ ! -d jep-%{version} ]; then
   echo "Directory jep-%{version} not found!"
   exit 1
fi
source /etc/profile.d/awips2Python.sh
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
cd jep-%{version}
/awips2/python/bin/python setup.py clean
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi 
/awips2/python/bin/python setup.py build
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%install
JEP_SRC_DIR="%{_python_pkgs_dir}/jep"

pushd . > /dev/null
cd %{_python_build_loc}/jep-%{version}
export LD_LIBRARY_PATH=/awips2/python/lib
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%pre

%post

%preun

%postun

%clean
rm -rf %{_build_root}
rm -rf %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/python/lib/python2.7/site-packages
/awips2/python/lib/python2.7/site-packages/*
%dir /awips2/python/lib/python2.7/site-packages/jep
/awips2/python/lib/python2.7/site-packages/jep/jep-%{version}.jar
/awips2/python/lib/python2.7/site-packages/jep/jep.so
/awips2/python/lib/python2.7/site-packages/jep/libjep.so
%defattr(755,awips,fxalpha,755)
%dir /awips2/python/bin
/awips2/python/bin/*
