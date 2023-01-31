# disable jar repacking
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-java-repack-jars[[:space:]].*$!!g')
%define _java_version 11.0.13+8
%define _java_version_file 11.0.13_8
%define _build_arch %(uname -i)
%define _java_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#
# AWIPS II Java 11 Spec File
#
Name: awips2-java
Summary: AWIPS II Java Distribution
# Moved to AdoptOpenJDK that changed version scheme.
Epoch: 1
Version: %{_java_version}
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
Provides: awips2-java = %{version}

%description
AWIPS II Java Distribution - Contains Java SE Development Kit (JDK) %{_java_version}
plus additional libraries used by AWIPS II.

%prep
# Ensure that a "buildroot" has been specified.
if [ "%{_build_root}" = "" ]; then
   echo "ERROR: A BuildRoot has not been specified."
   echo "FATAL: Unable to Continue ... Terminating."
   exit 1
fi

if [ -d %{_build_root} ]; then
   rm -rf %{_build_root}
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi
if [ -d %{_java_build_loc} ]; then
   rm -rf %{_java_build_loc}
fi
mkdir -p %{_java_build_loc}

%install

JDK_BIN_var_javahome="jdk-%{_java_version}"
jdk_tar="OpenJDK11U-jdk_x64_linux_hotspot_%{_java_version_file}.tar.gz"
pydev_cert="pydev_certificate.cer"
dod_cert="dod.pem"

# locate the java src.
CORE_PROJECT_DIR="%{_baseline_workspace}/foss"
INSTALLER_JAVA="${CORE_PROJECT_DIR}/java"
JAVA_SRC_DIR="${INSTALLER_JAVA}/packaged"
JAVA_COMMON_DIR="${INSTALLER_JAVA}/common"
JAVA_SCRIPTS_DIR="%{_baseline_workspace}/installers/RPMs/java/scripts"

pushd . > /dev/null
cd ${JAVA_SRC_DIR}
/bin/tar -xvf /awips2/repo/awips2-static/java/${jdk_tar} -C %{_java_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi
popd > /dev/null

mkdir -p %{_build_root}/awips2/java
if [ $? -ne 0 ]; then
   exit 1
fi
mkdir -p %{_build_root}/etc/profile.d
if [ $? -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null
cd %{_build_root}/awips2/java

/bin/mv %{_java_build_loc}/${JDK_BIN_var_javahome}/* .
if [ $? -ne 0 ]; then
   exit 1
fi
popd > /dev/null

# Our profile.d scripts.
JAVA_PROFILED_DIR="${JAVA_SCRIPTS_DIR}/profile.d"
cp -v ${JAVA_PROFILED_DIR}/* %{_build_root}/etc/profile.d
if [ $? -ne 0 ]; then
   exit 1
fi

# The pydev certificate.
# Install the self-signed pydev certificate to avoid dialog popups when running scripts.
# http://pydev.org/manual_101_install.html
cp -v ${JAVA_COMMON_DIR}/src/${pydev_cert} \
   %{_build_root}/awips2/java/lib/security
if [ $? -ne 0 ]; then
   exit 1
fi

# Install the signed DoD certificate needed for Thin Client
cp -v ${JAVA_COMMON_DIR}/src/${dod_cert} \
   %{_build_root}/awips2/java/lib/security
if [ $? -ne 0 ]; then
   exit 1
fi

touch changeit.txt
echo "changeit" > changeit.txt
chmod 666 %{_build_root}/awips2/java/lib/security/cacerts
if [ $? -ne 0 ]; then
   exit 1
fi

%{_build_root}/awips2/java/bin/keytool -import \
   -file %{_build_root}/awips2/java/lib/security/${pydev_cert} \
   -keystore %{_build_root}/awips2/java/lib/security/cacerts \
   -noprompt < changeit.txt
if [ $? -ne 0 ]; then
   exit 1
fi

%{_build_root}/awips2/java/bin/keytool -import \
   -file %{_build_root}/awips2/java/lib/security/${dod_cert} \
   -keystore %{_build_root}/awips2/java/lib/security/cacerts \
   -alias dod -noprompt < changeit.txt
if [ $? -ne 0 ]; then
   exit 1
fi

rm -fv changeit.txt
if [ $? -ne 0 ]; then
   exit 1
fi

# The licenses
mkdir -p %{_build_root}/awips2/java/licenses
LEGAL_DIR="%{_baseline_workspace}/rpms/legal"
cp -v ${LEGAL_DIR}/*.pdf \
   %{_build_root}/awips2/java/licenses
if [ $? -ne 0 ]; then
   exit 1
fi

%pre
if [ "${1}" = "2" ]; then
   # Upgrade. Removing the existing /awips2/java/man
   # directory to prevent conflicts.
   if [ -d /awips2/java/man ]; then
      rm -rf /awips2/java/man
      if [ $? -ne 0 ]; then
         echo "ERROR: The awips2-java upgrade has FAILED."
         exit 1
      fi
   fi
fi

%clean
rm -rf ${RPM_BUILD_ROOT}
rm -rf %{_java_build_loc}

%files
%defattr(644,awips,fxalpha,755)
%attr(755,root,root) /etc/profile.d/awips2Java.csh
%attr(755,root,root) /etc/profile.d/awips2Java.sh
%dir /awips2/java
%dir /awips2/java/bin

%dir /awips2/java/conf
%config /awips2/java/conf/*

%docdir /awips2/java/man
%dir /awips2/java/man
/awips2/java/man/*

%docdir /awips2/java/licenses
%dir /awips2/java/licenses
/awips2/java/licenses/*
%docdir /awips2/java/legal
%dir /awips2/java/legal
/awips2/java/legal/*
%doc /awips2/java/release
%doc /awips2/java/NOTICE

%dir /awips2/java/include
/awips2/java/include/*

%dir /awips2/java/lib
%dir /awips2/java/jmods

%defattr(755,awips,fxalpha,755)
/awips2/java/bin/*
/awips2/java/lib/*
/awips2/java/jmods/*
