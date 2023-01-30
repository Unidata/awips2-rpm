# disable jar repacking
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-java-repack-jars[[:space:]].*$!!g')
# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
#
# AWIPS II Ant Spec File
#
Name: awips2-ant
Summary: AWIPS II Ant Distribution
Version: 1.9.16
Release: %{_component_version}.%{_component_release}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: noarch
Prefix: /awips2/ant
URL: N/A
License: N/A
Distribution: N/A
Vendor: Raytheon
Packager: %{_build_site}

AutoReq: no
provides: awips2-ant

%description
AWIPS II Ant Distribution - Contains Ant V%{version}

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm -rf %{_build_root}
mkdir -p %{_build_root}

%build

%install
# Copies the standard Raytheon licenses into a license directory for the
# current component.
function copyLegal()
{
   # $1 == Component Build Root
   
   COMPONENT_BUILD_DIR=${1}
   
   mkdir -p %{_build_root}/${COMPONENT_BUILD_DIR}/licenses
   
   # Create a Tar file with our FOSS licenses.
   tar -cjf %{_baseline_workspace}/rpms/legal/FOSS_licenses.tar \
      %{_baseline_workspace}/rpms/legal/FOSS_licenses/
   
   cp "%{_baseline_workspace}/rpms/legal/Master_Rights_File.pdf" \
      %{_build_root}/${COMPONENT_BUILD_DIR}/licenses
   cp %{_baseline_workspace}/rpms/legal/FOSS_licenses.tar \
      %{_build_root}/${COMPONENT_BUILD_DIR}/licenses
      
   rm -f %{_baseline_workspace}/rpms/legal/FOSS_licenses.tar    
}

mkdir -p ${RPM_BUILD_ROOT}/awips2/ant
mkdir -p ${RPM_BUILD_ROOT}/etc/profile.d

CORE_PROJECT_DIR="%{_baseline_workspace}/foss"
ANT_BIN_DIR="${CORE_PROJECT_DIR}/ant-%{version}/packaged"
ANT_TAR_FILE="apache-ant-%{version}-bin.tar.gz"
ANT_LIB_DIR="%{_baseline_workspace}/installers/RPMs/ant/lib"
ANT_SCRIPTS_DIR="%{_baseline_workspace}/installers/RPMs/ant/scripts"

# Will Be Extracted Into apache-ant-%{version}
tar -xf ${ANT_BIN_DIR}/${ANT_TAR_FILE} \
   -C %{_build_root}/awips2
# Move Files From %{version} To The Generic Directory
cp -r %{_build_root}/awips2/apache-ant-%{version}/* \
   %{_build_root}/awips2/ant 
rm -rf %{_build_root}/awips2/apache-ant-%{version}

cp ${ANT_LIB_DIR}/* %{_build_root}/awips2/ant/lib

cp ${ANT_SCRIPTS_DIR}/profile.d/* %{_build_root}/etc/profile.d

copyLegal "awips2/ant"

%pre
if [ "${1}" = "2" ]; then
   exit 0
fi

%post
if [ "${1}" = "2" ]; then
   exit 0
fi

%postun
if [ "${1}" = "1" ]; then
   exit 0
fi

%clean
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(-,awips,fxalpha,-)
%attr(755,root,root) /etc/profile.d/awips2Ant.csh
%attr(755,root,root) /etc/profile.d/awips2Ant.sh
%dir /awips2/ant
%dir /awips2/ant/bin
%attr(755,awips,fxalpha) /awips2/ant/bin/ant
%attr(644,awips,fxalpha) /awips2/ant/bin/ant.bat
%attr(644,awips,fxalpha) /awips2/ant/bin/ant.cmd
%attr(644,awips,fxalpha) /awips2/ant/bin/antenv.cmd
%attr(755,awips,fxalpha) /awips2/ant/bin/antRun
%attr(644,awips,fxalpha) /awips2/ant/bin/antRun.bat
%attr(755,awips,fxalpha) /awips2/ant/bin/antRun.pl
%attr(755,awips,fxalpha) /awips2/ant/bin/complete-ant-cmd.pl
%attr(644,awips,fxalpha) /awips2/ant/bin/envset.cmd
%attr(644,awips,fxalpha) /awips2/ant/bin/lcp.bat
%attr(755,awips,fxalpha) /awips2/ant/bin/runant.pl
%attr(755,awips,fxalpha) /awips2/ant/bin/runant.py
%attr(644,awips,fxalpha) /awips2/ant/bin/runrc.cmd
%docdir /awips2/ant/manual
/awips2/ant/manual
/awips2/ant/etc
/awips2/ant/fetch.xml
/awips2/ant/get-m2.xml
%doc /awips2/ant/INSTALL
%doc /awips2/ant/KEYS
/awips2/ant/lib
%doc /awips2/ant/LICENSE
%docdir /awips2/ant/licenses
/awips2/ant/licenses
%doc /awips2/ant/NOTICE
%doc /awips2/ant/README
%doc /awips2/ant/WHATSNEW
%doc /awips2/ant/CONTRIBUTORS
%doc /awips2/ant/contributors.xml
%doc /awips2/ant/patch.xml
