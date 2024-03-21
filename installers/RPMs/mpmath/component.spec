# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)


Name: awips2-python-mpmath
Summary: AWIPS II Python mpmath module
Epoch: 1
Version: 1.3.0
Release: %{_installed_python_short}.1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: noarch
URL: N/A
License: N/A
Distribution: N/A
Vendor: ${_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: awips2-python >= %{_installed_python_short}

BuildRequires: awips2-python
BuildRequires: awips2-python-setuptools

%description
AWIPS II Python mpmath Site-Package

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
src_dir="%{_baseline_workspace}/foss/mpmath-%{version}/packaged"
package_file="mpmath-%{version}-py3-none-any.whl"
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
/awips2/python/lib/python%{_installed_python_short}/site-packages/mpmath
/awips2/python/lib/python%{_installed_python_short}/site-packages/mpmath-%{version}.dist-info
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/mpmath/__pycache__
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/mpmath/**/__pycache__

%changelog
* Mon Oct 02 2023 Freddy Camacho <freddy.camacho@noaa.gov> - 1.3.0
- update to version 1.3.0
* Wed Aug 11 2021 Tom Gurney <tom.gurney@raytheon.com>
- Initial creation
