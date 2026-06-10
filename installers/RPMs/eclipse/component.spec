#
# AWIPS II Eclipse Spec File
#

%define ECLIPSE_VER 2024-03-R
%define CDT_ZIP_FILE cdt-11.5.0.zip
%define MEMORY_ANALYZER_ZIP_FILE MemoryAnalyzer-1.15.0.202312061754.zip
%define PYDEV_ZIP_FILE PyDev-12.0.0.zip
%define WTP_ZIP_FILE wtp-repo-R-3.33.0-20240304165142.zip
# Disabling build ID links prevents conflicts with other packages that include
# Eclipse binaries.
%define _build_id_links none

Name: awips2-eclipse
Summary: AWIPS II Eclipse Distribution
Version: 4.31
Release: 1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
Provides: awips2-eclipse
Requires: awips2-ant
Requires: awips2-java
Requires: awips2-python
Requires: gtk3

BuildRequires: awips2-java

%description
AWIPS II Eclipse Distribution - Contains the AWIPS II Eclipse Distribution.

# disable python byte compile
%global _python_bytecompile_extra 0
# disable jar repacking
%global __jar_repack 0
# disable stripping of binaries, required to prevent "JAR has been tampered" error during CAVE build
%global __strip /bin/true

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "/tmp" ]
then
   echo "An Actual BuildRoot Must Be Specified. Use The --buildroot Parameter."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

if [ -d %{_build_root} ]; then
   rm --recursive --force %{_build_root}
fi

%install
TMP_BUILD_DIR="/tmp/eclipse-build"

CORE_PROJECT_DIR="%{_baseline_workspace}/foss"
ECLIPSE_BIN_DIR="${CORE_PROJECT_DIR}/eclipse-%{version}/packaged"
ECLIPSE_STATIC_DIR=ECLIPSE_STATIC_DIR="/awips2/repo/awips2-static/eclipse-%{version}/packaged"
ECLIPSE_TAR_FILE="eclipse-rcp-%{ECLIPSE_VER}-linux-gtk-x86_64.tar.gz"
ECLIPSE_DELTA_FILE="eclipse-%{ECLIPSE_VER}-delta-pack.zip"

ECLIPSE_EXE="${TMP_BUILD_DIR}/awips2/eclipse/eclipse"
NOSPLASH_ARG="-nosplash"
DIRECTOR_APP="-application org.eclipse.equinox.p2.director"
DESTINATION_ARG="-destination ${TMP_BUILD_DIR}/awips2/eclipse"
INSTALL_ARG="-installIU"
REPO="-repository jar:file:${ECLIPSE_STATIC_DIR}"

COMMON_CMD="${ECLIPSE_EXE} ${NOSPLASH_ARG} ${DIRECTOR_APP} ${DESTINATION_ARG}"

# Build in a temp location to avoid errors that build path is in files.
if [ -d ${TMP_BUILD_DIR} ]; then
   rm --recursive --force ${TMP_BUILD_DIR}
fi
mkdir --parents ${TMP_BUILD_DIR}/awips2/eclipse

# Extract Eclipse
tar --warning=no-unknown-keyword --extract --file=${ECLIPSE_STATIC_DIR}/${ECLIPSE_TAR_FILE} \
   --directory=${TMP_BUILD_DIR}/awips2

# Extract the Eclipse Delta Pack
unzip -o ${ECLIPSE_STATIC_DIR}/${ECLIPSE_DELTA_FILE} \
   -d ${TMP_BUILD_DIR}/awips2

#CDT_ZIP_FILE
${COMMON_CMD} ${INSTALL_ARG} org.eclipse.cdt.feature.group ${REPO}/%{CDT_ZIP_FILE}! || exit 1

#MEMORY_ANALYZER_ZIP_FILE
${COMMON_CMD} ${INSTALL_ARG} org.eclipse.mat.feature.feature.group ${REPO}/%{MEMORY_ANALYZER_ZIP_FILE}! || exit 1

#PYDEV_ZIP_FILE
# Pydev no longer packages as an installable p2 bundle, so cannot use p2 director to install.

# Extract to Eclipse Plugins/Features dirs so P2 build can use them during the build process.
unzip ${ECLIPSE_STATIC_DIR}/%{PYDEV_ZIP_FILE} -d ${TMP_BUILD_DIR}/awips2/eclipse/ || exit 1
# Extract to Eclipse Dropins dir for Eclipse application to find Pydev in development.
unzip ${ECLIPSE_STATIC_DIR}/%{PYDEV_ZIP_FILE} -d ${TMP_BUILD_DIR}/awips2/eclipse/dropins/ || exit 1

#WTP_ZIP_FILE
${COMMON_CMD} ${INSTALL_ARG} org.eclipse.wst.xml_ui.feature.feature.group ${REPO}/%{WTP_ZIP_FILE}! || exit 1

# Remove jetty and log4j due to security vulnerabilities
rm --force ${TMP_BUILD_DIR}/awips2/eclipse/plugins/org.eclipse.*jetty*.jar
rm --force ${TMP_BUILD_DIR}/awips2/eclipse/plugins/org.apache.*log4j*.jar

# Do not use the internal JRE for Eclipse
sed --in-place '/^-vm$/,+1 d' ${TMP_BUILD_DIR}/awips2/eclipse/eclipse.ini

# Move the complete application and remove the temp folder.
mv ${TMP_BUILD_DIR}/awips2 %{_build_root}
rm --recursive --force ${TMP_BUILD_DIR}

echo "-Dorg.eclipse.swt.internal.gtk.cairoGraphics=false" >> %{_build_root}/awips2/eclipse/eclipse.ini
echo "-Dorg.eclipse.swt.browser.DefaultType=mozilla" >> %{_build_root}/awips2/eclipse/eclipse.ini

%clean
rm --recursive --force ${RPM_BUILD_ROOT}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/eclipse
%dir /awips2/eclipse/binary
/awips2/eclipse/binary/*
%dir /awips2/eclipse/configuration
/awips2/eclipse/configuration/*
%dir /awips2/eclipse/features
/awips2/eclipse/features/*
%dir /awips2/eclipse/p2
/awips2/eclipse/p2/*
%dir /awips2/eclipse/plugins
/awips2/eclipse/plugins/*
%dir /awips2/eclipse/dropins
/awips2/eclipse/dropins/*
%dir /awips2/eclipse/readme
/awips2/eclipse/readme/*
%dir /awips2/eclipse/dropins
%defattr(755,awips,fxalpha,755)
/awips2/eclipse/artifacts.xml
/awips2/eclipse/eclipse
/awips2/eclipse/eclipse.ini
/awips2/eclipse/.eclipseproduct
/awips2/eclipse/icon.xpm
/awips2/eclipse/notice.html


