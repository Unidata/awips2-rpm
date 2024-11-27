# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _build_arch %(uname -i)
%define _build_id_links none

#
# AWIPS II Python shiboken6 Spec File
#

Name: awips2-python-shiboken6
Summary: AWIPS II Python shiboken6 module
Version: 6.5.0
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
Obsoletes: awips2-python-shiboken2

BuildRequires: awips2-python

%description
AWIPS II Python shiboken6 Site-Package

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


%build


%install
pushd . > /dev/null
src_dir="%{_baseline_workspace}/foss/shiboken6-%{version}/packaged"
package_file="shiboken6-%{version}-cp37-abi3-manylinux_2_28_x86_64.whl"
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
rm -rf %{_build_root}


%files
%defattr(644,awips,fxalpha,755)
/awips2/python/lib/python%{_installed_python_short}/site-packages/shiboken6
/awips2/python/lib/python%{_installed_python_short}/site-packages/shiboken6-%{version}.dist-info
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/shiboken6/__pycache__

%changelog
* Mon Jun 12 2023 Tom Gurney <thomas.gurney@rtx.com>
- Initial creation
