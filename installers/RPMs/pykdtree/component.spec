# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _build_id_links none

#
# AWIPS II Python pykdtree Spec File
#

Name: awips2-python-pykdtree
Summary: AWIPS II Python pykdtree module
Epoch: 1
Version: 1.3.7.post0
Release: %{_installed_python_short}.2%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: ${_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: awips2-python >= %{_installed_python_short}
Requires: awips2-python-numpy
Requires: libgomp

BuildRequires: awips2-python
BuildRequires: awips2-python-numpy
BuildRequires: libgomp
BuildRequires: awips2-python-setuptools

%description
AWIPS II Python pykdtree Site-Package

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

rm --recursive --force %{_python_build_loc}
mkdir --parents %{_python_build_loc}

SRC_DIR="%{_baseline_workspace}/foss/pykdtree-%{version}/packaged"
TAR_FILE="pykdtree-%{version}.tar.gz"
cp --verbose ${SRC_DIR}/${TAR_FILE} \
   %{_python_build_loc} \
   || exit 1

pushd . > /dev/null
cd %{_python_build_loc}
tar --extract --verbose --file=${TAR_FILE} || exit 1
rm --force --verbose ${TAR_FILE}
if [ ! -d pykdtree-%{version} ]; then
   echo "Directory pykdtree-%{version} not found!"
   exit 1
fi
popd > /dev/null


%build


%install

pushd . > /dev/null
cd %{_python_build_loc}/pykdtree-%{version}
# use libgomp to build
USE_OMP="gomp" /awips2/python/bin/pip3 install \
   --disable-pip-version-check --verbose --no-deps --ignore-installed --no-index \
   --root %{_build_root} --prefix /awips2/python . \
   || exit 1
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
/awips2/python/lib/python%{_installed_python_short}/site-packages/pykdtree
/awips2/python/lib/python%{_installed_python_short}/site-packages/pykdtree-%{version}.dist-info
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/pykdtree/__pycache__


%changelog
* Mon Jun 19 2023 David Gillingham <david.gillingham@rtx.com> 
- Update to version 1.3.7.post0 to support python 3.11.
- Fix dependencies.
* Thu Jul 15 2021 Lisa Singh <lisa.e.singh@raytheon.com> 
- Initial package creation.
