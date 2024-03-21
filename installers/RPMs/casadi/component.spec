# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _installed_python_short_no_dot %(echo %{_installed_python_short} | tr -d .)
%define _build_arch %(uname -i)


Name: awips2-python-casadi
Summary: AWIPS II Python casadi module
Epoch: 1
Version: 3.6.3
Release: %{_installed_python_short}.1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: ${_build_vendor}
Packager: %{_build_site}

AutoReq: no

BuildRequires: awips2-python
BuildRequires: awips2-python-setuptools
Requires: awips2-python >= %{_installed_python_short}
Requires: awips2-python-matplotlib >= 2.2.4
Requires: awips2-python-numpy >= 1.16.2
Requires: awips2-python-scipy >= 1.2.1

%description
AWIPS II Python casadi Site-Package

%prep
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm --recursive --force %{_build_root}
mkdir --parents %{_build_root}


%build

%install
pushd . > /dev/null
src_dir="%{_baseline_workspace}/foss/casadi-%{version}/packaged"
package_file="casadi-%{version}-cp%{_installed_python_short_no_dot}-none-manylinux2014_x86_64.whl"
/awips2/python/bin/pip3 install \
   --disable-pip-version-check --verbose --no-deps --ignore-installed --no-index \
   --root %{_build_root} --prefix /awips2/python \
   "${src_dir}/${package_file}" || exit 1
popd > /dev/null

# Merge lib64 into lib to avoid problems with installing into the virtualenv
if [ -d "%{_build_root}/awips2/python/lib64/" ]; then
    rsync --archive %{_build_root}/awips2/python/lib64/ %{_build_root}/awips2/python/lib || exit 1
    rm --recursive --force %{_build_root}/awips2/python/lib64
fi

%clean
rm --recursive --force %{_build_root}


%files
%defattr(644,awips,fxalpha,755)
/awips2/python/lib/python%{_installed_python_short}/site-packages/casadi
/awips2/python/lib/python%{_installed_python_short}/site-packages/casadi-%{version}.dist-info
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/casadi/__pycache__
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/casadi/**/__pycache__
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/dummy.txt

%changelog
* Tue Jun 13 2023 Srinivas Moorthy <srinivas.moorthy@rtx.com>
- Upgrade to 3.6.3 for python 3.11
* Wed Aug 11 2021 Tom Gurney <tom.gurney@raytheon.com> 
- Initial creation
