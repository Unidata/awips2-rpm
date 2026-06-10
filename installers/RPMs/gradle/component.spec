# disable python byte compile
%global _python_bytecompile_extra 0
# disable jar repacking
%global __jar_repack 0

Name: awips2-gradle
Summary: AWIPS II Gradle Distribution
Version: 8.4
Release: %{_component_version}.%{_component_release}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: noarch
Prefix: /awips2/gradle
URL: N/A
License: N/A
Distribution: N/A
Vendor: Raytheon
Packager: %{_build_site}

AutoReq: no
provides: awips2-gradle = %{version}

Requires: awips2-java

%description
AWIPS II Gradle Distribution - Contains Gradle V%{version}

%prep
# Ensure that a "buildroot" has been specified.
if [ "%{_build_root}" = "" ]; then
   echo "ERROR: A BuildRoot has not been specified."
   echo "FATAL: Unable to Continue ... Terminating."
   exit 1
fi

if [ -d %{_build_root} ]; then
   rm --recursive --force %{_build_root}
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi

%build

%install
mkdir --parents ${RPM_BUILD_ROOT}/etc/profile.d || exit 1

CORE_PROJECT_DIR="%{_baseline_workspace}/foss"
GRADLE_BIN_DIR="${CORE_PROJECT_DIR}/gradle-%{version}/packaged"
GRADLE_ZIP_FILE="gradle-%{version}-bin.zip"
GRADLE_SCRIPTS_DIR="%{_baseline_workspace}/installers/RPMs/gradle/scripts"

# Will Be Extracted Into gradle-%{version}
unzip ${GRADLE_BIN_DIR}/${GRADLE_ZIP_FILE} \
   -d %{_build_root}/awips2
# Move Files From %{version} To The Generic Directory
mv %{_build_root}/awips2/gradle-%{version}/ \
   %{_build_root}/awips2/gradle/

cp ${GRADLE_SCRIPTS_DIR}/profile.d/* %{_build_root}/etc/profile.d 

%clean
rm --recursive --force ${RPM_BUILD_ROOT}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/gradle/*
/awips2/gradle/lib/*
%doc /awips2/gradle/init.d/readme.txt
%license /awips2/gradle/LICENSE
%doc /awips2/gradle/NOTICE
%doc /awips2/gradle/README

%attr(755,awips,fxalpha) /awips2/gradle/bin/gradle
%attr(644,awips,fxalpha) /awips2/gradle/bin/gradle.bat

%attr(755,root,root) /etc/profile.d/awips2Gradle.csh
%attr(755,root,root) /etc/profile.d/awips2Gradle.sh

%changelog
* Wed Oct 04 2023 Lisa Singh <lisa.e.singh@rtx.com>
- Initial creation with Gradle 8.4.
