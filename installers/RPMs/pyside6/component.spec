# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _build_arch %(uname -i)

# There are a lot of native shared libraries in this package.
# Disabling /usr/lib/.build-id links prevents conflicts with system packages
%define _build_id_links none


Name: awips2-python-pyside6
Summary: AWIPS II Python PySide6 package
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
Requires: awips2-python-shiboken6 >= 6.5.0
Obsoletes: awips2-python-pyside2

# Requirements identified through trial-and-error and running ldd on included
# shared libraries.
Requires: libxcb-icccm.so.4
Requires: libxcb-image.so.0
Requires: libxcb-keysyms.so.1
Requires: libxcb-render-util.so.0
Requires: libxkbcommon-x11.so.0

# Have to specify the package name instead of the soname because the package
# is for some reason not being recognized as providing libxcb-cursor.so.0
Requires: xcb-util-cursor

# Do not build a huge "Provides" list from all of the included shared libraries
AutoProv: no

BuildRequires: awips2-python

%description
AWIPS II Python pyside6 Site-Package

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
#src_dir="%{_baseline_workspace}/foss/pyside6-%{version}/packaged"
src_dir="/awips2/repo/awips2-static/awips2-rpm/foss/pyside6-%{version}/packaged"
# The package is split into three wheels.
# The main PySide6 wheel depends on the other two.
for name in PySide6 PySide6_Essentials PySide6_Addons; do
    package_file="$name-%{version}-cp37-abi3-manylinux_2_28_x86_64.whl"
/awips2/python/bin/pip3 install \
   --disable-pip-version-check --verbose --no-deps --ignore-installed --no-index \
   --root %{_build_root} --prefix /awips2/python \
   "${src_dir}/${package_file}" || exit 1
done
popd > /dev/null

# Merge lib64 into lib to avoid problems with installing into the virtualenv
if [ -d "%{_build_root}/awips2/python/lib64/" ]; then
    rsync --archive %{_build_root}/awips2/python/lib64/ %{_build_root}/awips2/python/lib || exit 1
    rm --recursive --force %{_build_root}/awips2/python/lib64
fi

%clean
rm --recursive --force %{_build_root}

%files
%defattr(0644,awips,fxalpha,0755)
/awips2/python/lib/python%{_installed_python_short}
%defattr(0755,awips,fxalpha,0755)
/awips2/python/bin
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/PySide6/__pycache__
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/PySide6/scripts/deploy_lib/android/__pycache__
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/PySide6/scripts/deploy_lib/android/recipes/PySide6/__pycache__
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/PySide6/scripts/deploy_lib/android/recipes/shiboken6/__pycache__
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/PySide6/scripts/deploy_lib/__pycache__
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/PySide6/scripts/project/__pycache__
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/PySide6/scripts/__pycache__
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/PySide6/scripts/qtpy2cpp_lib/__pycache__
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/PySide6/support/__pycache__

%changelog
* Thu Jun 29 2023 Tom Gurney <thomas.gurney@rtx.com>
- Fix issue with libxcb-cursor.so.0 not being found at install time
* Mon Jun 12 2023 Tom Gurney <thomas.gurney@rtx.com>
- Initial creation
