#
# AWIPS II Eclipse Spec File
#

%define ECLIPSE_VER 2020-09-R
%define CDT_ZIP_FILE cdt-10.0.0.zip
%define CDT_RCP_ZIP_FILE cdt-rcp-10.0.0.zip
%define MEMORY_ANALYZER_ZIP_FILE MemoryAnalyzer-1.10.0.202002252112.zip
%define PYDEV_ZIP_FILE PyDev-8.0.0.zip
%define WTP_ZIP_FILE wtp-repo-R-3.19.0-20200828030223.zip

Name: awips2-eclipse
Summary: AWIPS II Eclipse Distribution
Version: 4.17
Release: 1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
URL: N/A
License: N/A
Distribution: N/A
Vendor: Raytheon
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

# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
# disable jar repacking
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-java-repack-jars[[:space:]].*$!!g')

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "/tmp" ]
then
   echo "An Actual BuildRoot Must Be Specified. Use The --buildroot Parameter."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

if [ -d %{_build_root} ]; then
   rm -rf %{_build_root}
fi

%build

%install
TMP_BUILD_DIR="/tmp/eclipse-build/"

CORE_PROJECT_DIR="%{_baseline_workspace}/foss"
ECLIPSE_BIN_DIR="${CORE_PROJECT_DIR}/eclipse-%{version}/packaged"
ECLIPSE_TAR_FILE="eclipse-rcp-%{ECLIPSE_VER}-linux-gtk-x86_64.tar.gz"
ECLIPSE_DELTA_FILE="eclipse-%{ECLIPSE_VER}-delta-pack.zip"

ECLIPSE_EXE="${TMP_BUILD_DIR}/awips2/eclipse/eclipse"
NOSPLASH_ARG="-nosplash"
DIRECTOR_APP="-application org.eclipse.equinox.p2.director"
DESTINATION_ARG="-destination ${TMP_BUILD_DIR}/awips2/eclipse"
INSTALL_ARG="-installIU"
REPOSITORY="${TMP_BUILD_DIR}"
REPO="-repository file:${REPOSITORY}"

COMMON_CMD="${ECLIPSE_EXE} ${NOSPLASH_ARG} ${DIRECTOR_APP} ${DESTINATION_ARG}"

# Build in a temp location to avoid errors that build path is in files.
if [ -d ${TMP_BUILD_DIR} ]; then
   rm -rf ${TMP_BUILD_DIR}
fi
mkdir -p ${TMP_BUILD_DIR}/awips2/eclipse

# Extract Eclipse
tar -xf ${ECLIPSE_BIN_DIR}/${ECLIPSE_TAR_FILE} \
   -C ${TMP_BUILD_DIR}/awips2

# Extract the Eclipse Delta Pack
unzip -o ${ECLIPSE_BIN_DIR}/${ECLIPSE_DELTA_FILE} \
   -d ${TMP_BUILD_DIR}/awips2

#CDT_ZIP_FILE
unzip  ${ECLIPSE_BIN_DIR}/%{CDT_RCP_ZIP_FILE} -d ${REPOSITORY}/cdt-rcp
${COMMON_CMD} ${INSTALL_ARG} com.sun.xml.bind,org.eclipse.launchbar.core,org.eclipse.cdt.dsf.ui,org.eclipse.cdt.dsf.gdb.ui ${REPO}/cdt-rcp/
if [ $? -ne 0 ]; then
   exit 1
fi
rm -rf ${REPOSITORY}/cdt-rcp

unzip  ${ECLIPSE_BIN_DIR}/%{CDT_ZIP_FILE} -d ${REPOSITORY}/cdt
${COMMON_CMD} ${INSTALL_ARG} org.eclipse.cdt.feature.group ${REPO}/cdt/
if [ $? -ne 0 ]; then
   exit 1
fi
rm -rf ${REPOSITORY}/cdt

#MEMORY_ANALYZER_ZIP_FILE
unzip  ${ECLIPSE_BIN_DIR}/%{MEMORY_ANALYZER_ZIP_FILE} -d ${REPOSITORY}/ma
${COMMON_CMD} ${INSTALL_ARG} org.eclipse.mat.feature.feature.group ${REPO}/ma/
if [ $? -ne 0 ]; then
   exit 1
fi
rm -rf ${REPOSITORY}/ma

#PYDEV_ZIP_FILE
unzip  ${ECLIPSE_BIN_DIR}/%{PYDEV_ZIP_FILE} -d ${REPOSITORY}/pydev
${COMMON_CMD} ${INSTALL_ARG} org.python.pydev.feature.feature.group ${REPO}/pydev/
if [ $? -ne 0 ]; then
   exit 1
fi
rm -rf ${REPOSITORY}/pydev

#WTP_ZIP_FILE
unzip  ${ECLIPSE_BIN_DIR}/%{WTP_ZIP_FILE} -d ${REPOSITORY}/wtp
${COMMON_CMD} ${INSTALL_ARG} org.eclipse.wst.xml_ui.feature.feature.group ${REPO}/wtp/
if [ $? -ne 0 ]; then
   exit 1
fi
rm -rf ${REPOSITORY}/wtp

# Move the complete application and remove the temp folder.
mv ${TMP_BUILD_DIR}/awips2 %{_build_root}
rm -rf ${TMP_BUILD_DIR}

echo "-Dorg.eclipse.swt.internal.gtk.cairoGraphics=false" >> %{_build_root}/awips2/eclipse/eclipse.ini
echo "-Dorg.eclipse.swt.browser.DefaultType=mozilla" >> %{_build_root}/awips2/eclipse/eclipse.ini

%clean
rm -rf ${RPM_BUILD_ROOT}

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


