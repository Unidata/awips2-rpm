# disable python byte compile
%global _python_bytecompile_extra 0
# disable jar repacking
%global __jar_repack 0

%define _build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _build_name yajsw-stable-%{version}


#
# AWIPS II YAJSW Spec File
#

Name: awips2-yajsw
Summary: AWIPS II yajsw Distribution
Version: 13.11
Release: %{_component_version}.%{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: noarch
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no

Provides: awips2-yajsw
BuildRequires: awips2-gradle
BuildRequires: awips2-java
Requires: awips2
Requires: awips2-java

%description
AWIPS II yajsw Distribution - A custom compilation of yajsw %{version} used
by several AWIPS II components.

%prep
# Ensure that a "buildroot" has been specified.
if [ "%{_build_root}" = "" ]; then
   echo "ERROR: A BuildRoot has not been specified."
   echo "FATAL: Unable to Continue ... Terminating."
   exit 1
fi

if [ -d %{_build_root} ]; then
   rm --recursive --force %{_build_root}
fi
if [ -d %{build_loc} ]; then
   rm --recursive --force %{_build_loc}
fi
mkdir --parents %{_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi

SOURCE_DIR="%{_baseline_workspace}/foss/yajsw-%{version}/packaged"

cp --verbose ${SOURCE_DIR}/%{_build_name}.zip %{_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi

%build
PATCH_DIR="%{_baseline_workspace}/installers/RPMs/yajsw/patches"
BUILD_DIR="%{_build_loc}/%{_build_name}"

pushd . > /dev/null 2>&1
cd %{_build_loc}
unzip -q "%{_build_name}.zip"
cd %{_build_name}

### Apply patches ###
echo "Applying patches...."

# Update Netty
rm --force ./lib/core/netty/netty-*.jar
cp ${PATCH_DIR}/lib/netty-transport-4.1.132.Final.jar ./lib/core/netty/
cp ${PATCH_DIR}/lib/netty-common-4.1.132.Final.jar ./lib/core/netty/
cp ${PATCH_DIR}/lib/netty-buffer-4.1.132.Final.jar ./lib/core/netty/
cp ${PATCH_DIR}/lib/netty-codec-4.1.132.Final.jar ./lib/core/netty/
cp ${PATCH_DIR}/lib/netty-handler-4.1.132.Final.jar ./lib/core/netty/
cp ${PATCH_DIR}/lib/netty-resolver-4.1.132.Final.jar ./lib/core/netty/

# Update Apache Commons Configuration
rm --force ./lib/core/commons/commons-configuration2-2.8.0.jar
cp ${PATCH_DIR}/lib/commons-configuration2-2.12.0.jar ./lib/core/commons

# Update Apache Commons VFS
rm --force ./lib/core/commons/commons-vfs2-2.9.0.jar
cp ${PATCH_DIR}/lib/commons-vfs2-2.10.0.jar ./lib/core/commons

# Update Apache Commons Logging
rm --force ./lib/core/commons/commons-logging-1.2.jar
cp ${PATCH_DIR}/lib/commons-logging-1.3.4.jar ./lib/core/commons

# Update Apache Commons IO
rm --force ./lib/core/commons/commons-io-2.11.0.jar
cp ${PATCH_DIR}/lib/commons-io-2.18.0.jar ./lib/core/commons

# Update Apache Commons Lang3
rm --force ./lib/core/commons/commons-lang3-3.12.0.jar
cp ${PATCH_DIR}/lib/commons-lang3-3.18.0.jar ./lib/core/commons

# Patch build files to account for the dependency updates
patch ./build/gradle/build.gradle < ${PATCH_DIR}/build/build.gradle_patch || exit 1
patch --ignore-whitespace -p3 < ${PATCH_DIR}/build/settings.gradle_patch || exit 1
patch ./build/MANIFEST.MF < ${PATCH_DIR}/build/MANIFEST.MF_patch || exit 1

# Patch source code
patch --ignore-whitespace -p3 < ${PATCH_DIR}/src/AbstractScript.java_patch || exit 1
patch --ignore-whitespace -p3 < ${PATCH_DIR}/src/AbstractWrappedProcess.java_patch || exit 1
patch --ignore-whitespace -p3 < ${PATCH_DIR}/src/AppStarter.java_patch || exit 1
patch --ignore-whitespace -p3 < ${PATCH_DIR}/src/BSDProcess.java_patch || exit 1
patch --ignore-whitespace -p3 < ${PATCH_DIR}/src/MyFileHandler.java_patch || exit 1
patch --ignore-whitespace -p3 < ${PATCH_DIR}/src/PosixProcess.java_patch || exit 1
patch --ignore-whitespace -p3 < ${PATCH_DIR}/src/WrappedJavaProcess.java_patch || exit 1
patch --ignore-whitespace -p3 < ${PATCH_DIR}/src/WrapperExe.java_patch || exit 1
patch --ignore-whitespace -p3 < ${PATCH_DIR}/src/WrapperManagerImpl.java_patch || exit 1
patch ./src/yajsw/src/main/java/io/netty/util/internal/PlatformDependent0.java < ${PATCH_DIR}/src/PlatformDependent0.java_patch || exit 1

### End Apply Patches ###

## Build YAJSW
echo "Building YAJSW..."
cd build/gradle
gradle --gradle-user-home ${BUILD_DIR}
popd > /dev/null 2>&1

%install
SCRIPTS_DIR="%{_baseline_workspace}/installers/RPMs/yajsw/scripts"
DEST_DIR="%{_build_root}/awips2/yajsw"
BUILD_DIR="%{_build_loc}/%{_build_name}"

mkdir --parents ${DEST_DIR}

cp --verbose ${BUILD_DIR}/build/gradle/wrapper/build/libs/wrapper.jar \
   ${DEST_DIR}
cp --verbose ${BUILD_DIR}/build/gradle/wrapper-app/build/libs/wrapperApp.jar \
   ${DEST_DIR}
cp --verbose ${BUILD_DIR}/LICENSE.txt \
   ${DEST_DIR}

cp --verbose --recursive  ${BUILD_DIR}/lib \
   ${DEST_DIR}

mkdir --parents %{_build_root}/etc/profile.d
if [ $? -ne 0 ]; then
   exit 1
fi
cp --recursive --verbose ${SCRIPTS_DIR}/profile.d/* %{_build_root}/etc/profile.d/
if [ $? -ne 0 ]; then
   exit 1
fi

%clean
rm --recursive --force ${RPM_BUILD_ROOT}
rm --recursive --force %{_build_loc}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/yajsw/
/awips2/yajsw/*.jar
/awips2/yajsw/*.txt
%dir /awips2/yajsw/lib
/awips2/yajsw/lib/*
#exclude unused dependencies
%exclude /awips2/yajsw/lib/extended/commons
%exclude /awips2/yajsw/lib/extended/glazedlists
%exclude /awips2/yajsw/lib/extended/keystore
%exclude /awips2/yajsw/lib/extended/regex
%exclude /awips2/yajsw/lib/extended/sigar
%exclude /awips2/yajsw/lib/extended/vfs-dbx
%exclude /awips2/yajsw/lib/extended/vfs-webdav
%exclude /awips2/yajsw/lib/extended/yajsw

%license /awips2/yajsw/LICENSE.txt

%attr(744,root,root) /etc/profile.d/*

%changelog
* Thu Apr 02 2026 Mark Peters <mark.a.peters@rtx.com>
- Upgrade netty to 4.1.132.Final
* Wed Jan 07 2026 Srinivas Moorthy <srinivas.moorthy@noaa.gov>
- Upgrade netty to 4.1.130.Final
* Thu Oct 30 2025 Nate Jensen <nathan.jensen@noaa.gov>
- Upgrade netty to 4.1.128.Final
* Tue Oct 28 2025 Nate Jensen <nathan.jensen@noaa.gov>
- Upgrade commons-configuration2 to 2.12.0
* Thu Oct 09 2025 Srinivas Moorthy <srinivas.moorthy@noaa.gov>
- Upgrade netty to 4.1.125
* Wed Sep 03 2025 Nate Jensen <nathan.jensen@noaa.gov>
- Upgrade netty to 4.1.124.Final
* Wed Aug 06 2025 Ada Lockleigh <ada.lockleigh@noaa.gov>
- Upgrade commons-lang3 to 3.18.0
* Tue May 20 2025 Tom Gurney <thomas.gurney@rtx.com>
- Upgrade commons-lang3 to 3.17.0
* Tue May 20 2025 Tom Gurney <thomas.gurney@rtx.com>
- Upgrade commons-io to 2.18.0
* Tue May 20 2025 Tom Gurney <thomas.gurney@rtx.com>
- Upgrade commons-logging to 1.3.4
* Mon Apr 21 2025 John Sebahar <john.sebahar@rtx.com>
- Update commons-vfs2 to 2.10
* Mon Apr 08 2024 Adam Ford <adam.j.ford@rtx.com>
- Update YAJSW to 13.11
* Mon Oct 30 2023 Lisa Singh <lisa.e.singh@rtx.com>
- Updated YAJSW to build from source.
