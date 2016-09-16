#
# AWIPS II Eclipse Spec File
#

%define CDT_ZIP_FILE cdt-master-8.0.2.zip
%define MEMORY_ANALYZER_ZIP_FILE MemoryAnalyzer-1.3.1.201401071412.zip
%define SHELLED_ZIP_FILE net.sourceforge.shelled-site-2.0.3.zip
%define PYDEV_ZIP_FILE PyDev-3.4.1.zip
%define WTP_ZIP_FILE wtp-repo-R-3.3.2-20120210195245.zip
%define GEF_ZIP_FILE GEF-ALL-3.7.2.zip
%define EMF_ZIP_FILE emf-runtime-2.8.3.zip
%define XSD_ZIP_FILE xsd-runtime-2.7.2.zip
%define DLTK_ZIP_FILE dltk-core-R-4.0-201206120903.zip
%define EGIT_ZIP_FILE org.eclipse.egit.repository-3.3.2.201404171909-r.zip

# --define arguments:
#   %{_build_root}
#   %{_baseline_workspace}

Name: awips2-eclipse
Summary: AWIPS II Eclipse Distribution
Version: 3.8.2
Release: 1
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


%description
AWIPS II Eclipse Distribution - Contains the AWIPS II Eclipse Distribution.

# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
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
ECLIPSE_TAR_FILE="eclipse-SDK-%{version}-linux-gtk-x86_64.tar.gz"
ECLIPSE_DELTA_FILE="eclipse-%{version}-delta-pack.zip"

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
unzip  ${ECLIPSE_BIN_DIR}/%{GEF_ZIP_FILE} -d ${REPOSITORY}/gef
${COMMON_CMD} ${INSTALL_ARG} org.eclipse.gef.feature.group ${REPO}/gef/
if [ $? -ne 0 ]; then
   exit 1
fi
rm -rf ${REPOSITORY}/gef

unzip  ${ECLIPSE_BIN_DIR}/%{EMF_ZIP_FILE} -d ${REPOSITORY}/emf
${COMMON_CMD} ${INSTALL_ARG} org.eclipse.emf.ecore.feature.group ${REPO}/emf/
if [ $? -ne 0 ]; then
   exit 1
fi
${COMMON_CMD} ${INSTALL_ARG} org.eclipse.emf.ecore.edit.feature.group ${REPO}/emf/
if [ $? -ne 0 ]; then
   exit 1
fi
${COMMON_CMD} ${INSTALL_ARG} org.eclipse.emf.edit.ui.feature.group ${REPO}/emf/
if [ $? -ne 0 ]; then
   exit 1
fi
rm -rf ${REPOSITORY}/emf

unzip  ${ECLIPSE_BIN_DIR}/%{XSD_ZIP_FILE} -d ${REPOSITORY}/xsd
${COMMON_CMD} ${INSTALL_ARG} org.eclipse.xsd.edit.feature.group ${REPO}/xsd/
if [ $? -ne 0 ]; then
   exit 1
fi
rm -rf ${REPOSITORY}/xsd

unzip  ${ECLIPSE_BIN_DIR}/%{WTP_ZIP_FILE} -d ${REPOSITORY}/wtp
${COMMON_CMD} ${INSTALL_ARG} org.eclipse.wst.xml_ui.feature.feature.group ${REPO}/wtp/
if [ $? -ne 0 ]; then
   exit 1
fi
rm -rf ${REPOSITORY}/wtp

#SHELLED_ZIP_FILE
unzip  ${ECLIPSE_BIN_DIR}/%{DLTK_ZIP_FILE} -d ${REPOSITORY}/dltk
${COMMON_CMD} ${INSTALL_ARG} org.eclipse.dltk.core.feature.group ${REPO}/dltk/
if [ $? -ne 0 ]; then
   exit 1
fi
rm -rf ${REPOSITORY}/dltk

unzip  ${ECLIPSE_BIN_DIR}/%{SHELLED_ZIP_FILE} -d ${REPOSITORY}/shelled
${COMMON_CMD} ${INSTALL_ARG} net.sourceforge.shelled.feature.group ${REPO}/shelled/
if [ $? -ne 0 ]; then
   exit 1
fi
rm -rf ${REPOSITORY}/shelled

#eGit
unzip  ${ECLIPSE_BIN_DIR}/%{EGIT_ZIP_FILE} -d ${REPOSITORY}/egit
${COMMON_CMD} ${INSTALL_ARG} org.eclipse.egit.feature.group ${REPO}/egit/
if [ $? -ne 0 ]; then
   exit 1
fi
rm -rf ${REPOSITORY}/egit

# Move the complete application and remove the temp folder.
mv ${TMP_BUILD_DIR}/awips2 %{_build_root}
rm -rf ${TMP_BUILD_DIR}

echo "-Dorg.eclipse.swt.internal.gtk.cairoGraphics=false" >> %{_build_root}/awips2/eclipse/eclipse.ini
echo "-Dorg.eclipse.swt.browser.DefaultType=mozilla" >> %{_build_root}/awips2/eclipse/eclipse.ini

%pre

%post

%preun

%postun

%clean
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(644,awips,awips,755)
%dir /awips2/eclipse
%dir /awips2/eclipse/about_files
/awips2/eclipse/about_files/*
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
%defattr(755,awips,awips,755)
/awips2/eclipse/about.html
/awips2/eclipse/artifacts.xml
/awips2/eclipse/eclipse
/awips2/eclipse/eclipse.ini
/awips2/eclipse/.eclipseproduct
/awips2/eclipse/epl-v10.html
/awips2/eclipse/icon.xpm
/awips2/eclipse/libcairo-swt.so
/awips2/eclipse/notice.html


