%define _ninja_unzip_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _build_id_links none

Name: awips2-ninja-build
Summary: AWIPS II Ninja-Build Distribution
Version: 1.13.2
Release: %{_component_version}.%{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: Raytheon
Packager: %{_build_site}

AutoReq: no

%description
AWIPS II Ninja-Build Package

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm --recursive --force %{_build_root} || exit 1

if [ -d %{_ninja_unzip_loc} ]; then
   rm --recursive --force %{_ninja_unzip_loc} || exit 1
fi
mkdir --parents %{_ninja_unzip_loc} || exit 1

%build

%install
pushd . > /dev/null

NINJA_DIR="%{_baseline_workspace}/foss/ninja-build-%{version}/packaged"
NINJA_PACKAGE="ninja-linux.zip"
cp --verbose ${NINJA_DIR}/${NINJA_PACKAGE} %{_ninja_unzip_loc} || exit 1
cd %{_ninja_unzip_loc} || exit 1
unzip ${NINJA_PACKAGE} || exit 1
mkdir --parents %{_build_root}/awips2/ninja-build/bin || exit 1
cp ninja %{_build_root}/awips2/ninja-build/bin/ || exit 1

# Our profile.d scripts.
mkdir --parents %{_build_root}/etc/profile.d || exit 1
NINJA_PROJECT_DIR="%{_baseline_workspace}/installers/RPMs/ninja-build"
NINJA_SCRIPTS_DIR="${NINJA_PROJECT_DIR}/scripts"
NINJA_PROFILED_DIR="${NINJA_SCRIPTS_DIR}/profile.d"
cp -v ${NINJA_PROFILED_DIR}/* %{_build_root}/etc/profile.d || exit 1

popd > /dev/null

%clean
rm --recursive --force %{_build_root}
rm --recursive --force %{_ninja_unzip_loc}

%files
%defattr(644,awips,fxalpha,755)
%attr(755,root,root) /etc/profile.d/awips2Ninja.csh
%attr(755,root,root) /etc/profile.d/awips2Ninja.sh
%defattr(755,awips,fxalpha,755)
/awips2/ninja-build/bin/ninja
