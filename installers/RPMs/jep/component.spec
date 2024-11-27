# disable jar repacking
%global __jar_repack 0
# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python_numpy %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c "import numpy; print(numpy.__version__)"; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _installed_python_short_no_dot %(echo %{_installed_python_short} | tr -d .)
%define _build_id_links none

#
# AWIPS II Python Jep Spec File
#
Name: awips2-python-jep
Summary: AWIPS II Python Jep Distribution
Epoch: 1
Version: 4.1.1
Release: %{_installed_python_short}.%{_installed_python_numpy}.3%{?dist}
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
Requires: awips2-python-numpy

BuildRequires: awips2-python
BuildRequires: awips2-java
BuildRequires: awips2-python-numpy
BuildRequires: gcc

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

rm --recursive --force %{_build_root}
mkdir --parents %{_build_root}
if [ -d %{_python_build_loc} ]; then
   rm --recursive --force %{_python_build_loc}
fi
mkdir --parents %{_python_build_loc}

%build
JEP_SRC_DIR="%{_baseline_workspace}/foss/jep-%{version}/packaged"
JEP_ZIP="jep-%{version}.tar.gz"
cp --verbose ${JEP_SRC_DIR}/${JEP_ZIP} \
   %{_python_build_loc} || exit 1

pushd . > /dev/null
cd %{_python_build_loc}
tar --extract --file "${JEP_ZIP}" || exit 1
rm --force --verbose "${JEP_ZIP}"
cd jep-%{version} || exit 1

# patch - build failure of jep 4.1.1
# Adapt code to setuptools.dep_util deprecation
# This patch should be removed when jep is upgraded
# to 4.2 or later
patch commands/java.py << 'EOF'
2c2,5
< from setuptools.dep_util import newer_group
---
> try:
>     from setuptools.modified import newer_group
> except ImportError:
>     from setuptools.dep_util import newer_group
EOF
if [ $? -ne 0 ]; then
   exit 1
fi
patch commands/scripts.py << 'EOF'
14c14,17
< from distutils.dep_util import newer
---
> try:
>     from setuptools.modified import newer
> except ImportError:
>     from distutils.dep_util import newer
EOF
if [ $? -ne 0 ]; then
   exit 1
fi
# end patch
/awips2/python/bin/python setup.py clean || exit 1
/awips2/python/bin/python setup.py build || exit 1

popd > /dev/null

%install
pushd . > /dev/null
cd %{_python_build_loc}/jep-%{version}
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python || exit 1
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
%dir /awips2/python/lib/python%{_installed_python_short}/site-packages/jep
/awips2/python/lib/python%{_installed_python_short}/site-packages/jep/jep-%{version}.jar
/awips2/python/lib/python%{_installed_python_short}/site-packages/jep/jep.cpython-%{_installed_python_short_no_dot}-x86_64-linux-gnu.so
/awips2/python/lib/python%{_installed_python_short}/site-packages/jep/libjep.so
%defattr(755,awips,fxalpha,755)
/awips2/python/bin/jep

%changelog
* Thu Nov 07 2024 Howard Van Dam <howard.vandam@rtx.com>
- Patch build failure in jep 4.1.1
