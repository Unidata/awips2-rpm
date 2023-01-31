%define _build_arch %(uname -i)

Name: awips2-maven
Summary: AWIPS II Maven Distribution
Version: 3.8.1
Release: %{_component_version}.%{_component_release}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
Prefix: /awips2/maven
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
provides: awips2-maven = %{version}

%description
AWIPS II Maven Distribution - Contains Maven V%{version}

# disable jar repacking
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-java-repack-jars[[:space:]].*$!!g')

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

if [ -d %{_build_root} ]; then
   rm -rf %{_build_root}
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi

mkdir -p %{_build_root}

%build

%install
# Copies the standard %{_build_vendor} licenses into a license directory for the
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

mkdir -p ${RPM_BUILD_ROOT}/awips2/maven
mkdir -p ${RPM_BUILD_ROOT}/etc/profile.d


CORE_PROJECT_DIR="%{_baseline_workspace}/foss"
MAVEN_BIN_DIR="${CORE_PROJECT_DIR}/maven-%{version}/packaged"
MAVEN_TAR_FILE="apache-maven-%{version}-bin.tar.gz"
MAVEN_SCRIPTS_DIR="%{_baseline_workspace}/installers/RPMs/maven/scripts"

# Will Be Extracted Into apache-maven-%{version}
tar -xf ${MAVEN_BIN_DIR}/${MAVEN_TAR_FILE} \
   -C %{_build_root}/awips2
# Move Files From %{version} To The Generic Directory
cp -r %{_build_root}/awips2/apache-maven-%{version}/* \
   %{_build_root}/awips2/maven

rm -rf %{_build_root}/awips2/apache-maven-%{version}

cp ${MAVEN_SCRIPTS_DIR}/profile.d/* %{_build_root}/etc/profile.d 

copyLegal "awips2/maven"

%clean
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(-,awips,fxalpha,-)
%attr(755,root,root) /etc/profile.d/awips2Maven.csh
%attr(755,root,root) /etc/profile.d/awips2Maven.sh
%dir /awips2/maven
%dir /awips2/maven/bin
%attr(755,awips,fxalpha) /awips2/maven/bin/mvn
%attr(644,awips,fxalpha) /awips2/maven/bin/mvn.cmd
%attr(755,awips,fxalpha) /awips2/maven/bin/mvnDebug
%attr(644,awips,fxalpha) /awips2/maven/bin/mvnDebug.cmd
%attr(755,awips,fxalpha) /awips2/maven/bin/mvnyjp
%attr(644,awips,fxalpha) /awips2/maven/bin/m2.conf
/awips2/maven/boot
/awips2/maven/conf
/awips2/maven/lib
%doc /awips2/maven/LICENSE
%docdir /awips2/maven/licenses
/awips2/maven/licenses
%doc /awips2/maven/NOTICE
%doc /awips2/maven/README.txt
