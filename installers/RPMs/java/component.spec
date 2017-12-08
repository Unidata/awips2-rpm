%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-java-repack-jars[[:space:]].*$!!g')
%define _java_major_version 1.8
%define _java_revision 101
%define _java_version %{_java_major_version}.0_%{_java_revision}
%define _build_arch %(uname -i)
%define _java_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#
# AWIPS II Java 1.8 Spec File
#
Name: awips2-java
Summary: AWIPS II Java Distribution
Version: %{_java_version}
Release: 1%{?dist}
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

%build

%install
build_arch=
arch_directory=
# determine the architecture based on the system architecture.
if [ "%{_build_arch}" = "x86_64" ]; then
   build_arch="amd64"
   arch_directory="x86_64"
   jdk_arch="x64"
else
   if [ "%{_build_arch}" = "i386" ]; then
      build_arch="i586"
      arch_directory="i386"
      jdk_arch=${build_arch}
   else
      echo "ERROR: Unrecognized architecture '%{_build_arch}."
      exit 1
   fi
fi

JDK_BIN_var_javahome="jdk%{_java_version}"
jdk_tar="jdk-8u%{_java_revision}-linux-${jdk_arch}.tar.gz"
jai_bin="jai-1_1_3-lib-linux-${build_arch}-jdk.bin"
jai_imageio_bin="jai_imageio-1_1-lib-linux-${build_arch}-jdk.bin"
jai_bin_patch="jai.patch1"
jai_imageio_bin_patch="jai_imageio.patch1"
pydev_cert="pydev_certificate.cer"
dod_cert="dod.pem"

# locate the java src.
CORE_PROJECT_DIR="%{_baseline_workspace}/foss"
INSTALLER_JAVA="${CORE_PROJECT_DIR}/java-%{_java_major_version}"
JAVA_SRC_DIR="${INSTALLER_JAVA}/common/src"
JAVA_COMMON_DIR="${INSTALLER_JAVA}/common"
JAVA_SCRIPTS_DIR="%{_baseline_workspace}/installers/RPMs/java/scripts"
JAVA_COMMON_SRC_DIR="${JAVA_COMMON_DIR}/src/${arch_directory}"
JAVA_ARCH_SRC_DIR="${JAVA_SRC_DIR}/${arch_directory}"

pushd . > /dev/null
cd ${JAVA_ARCH_SRC_DIR}
cp %{_static_files}/java/${jdk_tar} .
/bin/tar -xvf ${jdk_tar} -C %{_java_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi
popd > /dev/null

pushd . > /dev/null
cd ${JAVA_COMMON_SRC_DIR}
/usr/bin/patch -i ${jai_bin_patch} \
   -o %{_java_build_loc}/${jai_bin}
if [ $? -ne 0 ]; then
   exit 1
fi
/usr/bin/patch -i ${jai_imageio_bin_patch} \
   -o %{_java_build_loc}/${jai_imageio_bin}
if [ $? -ne 0 ]; then
   exit 1
fi
popd > /dev/null

mkdir -p %{_build_root}/awips2/java
if [ $? -ne 0 ]; then
   exit 1
fi

chmod a+x %{_java_build_loc}/*.bin
pushd . > /dev/null
cd %{_build_root}/awips2/java
# Used to automatically agree to software licenses.
touch yes.txt
echo "yes" > yes.txt

/bin/mv %{_java_build_loc}/${JDK_BIN_var_javahome}/* .
if [ $? -ne 0 ]; then
   exit 1
fi

# The following commands will return success even on failure.
%{_java_build_loc}/${jai_bin} < yes.txt
%{_java_build_loc}/${jai_imageio_bin} < yes.txt

rm -fv yes.txt
if [ $? -ne 0 ]; then
   exit 1
fi
popd > /dev/null

# The pydev certificate.
# Install the self-signed pydev certificate to avoid dialog popups when running scripts.
# http://pydev.org/manual_101_install.html
cp -v ${JAVA_COMMON_DIR}/src/${pydev_cert} \
   %{_build_root}/awips2/java/jre/lib/security
if [ $? -ne 0 ]; then
   exit 1
fi

# Install the signed DoD certificate needed for Thin Client
cp -v ${JAVA_COMMON_DIR}/src/${dod_cert} \
   %{_build_root}/awips2/java/jre/lib/security
if [ $? -ne 0 ]; then
   exit 1
fi

touch changeit.txt
echo "changeit" > changeit.txt
chmod 666 %{_build_root}/awips2/java/jre/lib/security/cacerts
if [ $? -ne 0 ]; then
   exit 1
fi

%{_build_root}/awips2/java/bin/keytool -import \
   -file %{_build_root}/awips2/java/jre/lib/security/${pydev_cert} \
   -keystore %{_build_root}/awips2/java/jre/lib/security/cacerts \
   -noprompt < changeit.txt
if [ $? -ne 0 ]; then
   exit 1
fi

%{_build_root}/awips2/java/bin/keytool -import \
   -file %{_build_root}/awips2/java/jre/lib/security/${dod_cert} \
   -keystore %{_build_root}/awips2/java/jre/lib/security/cacerts \
   -alias dod -noprompt < changeit.txt
if [ $? -ne 0 ]; then
   exit 1
fi

rm -fv changeit.txt
if [ $? -ne 0 ]; then
   exit 1
fi

# Remove jrockit missioncontrol - #3035
rm -rf %{_build_root}/awips2/java/lib/missioncontrol
rm -f %{_build_root}/awips2/java/bin/jmc.ini
rm -f %{_build_root}/awips2/java/bin/jmc

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

%post
%preun
%postun

%clean
rm -rf ${RPM_BUILD_ROOT}
rm -rf %{_java_build_loc}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/java
%dir /awips2/java/bin

%doc /awips2/java/COPYRIGHT
%doc /awips2/java/COPYRIGHT-jai_imageio.txt
%doc /awips2/java/COPYRIGHT-jai.txt
%doc /awips2/java/DISTRIBUTIONREADME-jai_imageio.txt
%doc /awips2/java/DISTRIBUTIONREADME-jai.txt
%doc /awips2/java/ENTITLEMENT-jai_imageio.txt
%doc /awips2/java/jre/README
%doc /awips2/java/jre/THIRDPARTYLICENSEREADME.txt
%doc /awips2/java/jre/Welcome.html
%doc /awips2/java/jre/LICENSE
%doc /awips2/java/LICENSE
%doc /awips2/java/LICENSE-jai_imageio.txt
%doc /awips2/java/LICENSE-jai.txt
%docdir /awips2/java/licenses
%dir /awips2/java/licenses
/awips2/java/licenses/*
%docdir /awips2/java/man
%dir /awips2/java/man
/awips2/java/man/*
%doc /awips2/java/README.html
%doc /awips2/java/THIRDPARTYLICENSEREADME-jai_imageio.txt
%doc /awips2/java/THIRDPARTYLICENSEREADME-jai.txt
%doc /awips2/java/THIRDPARTYLICENSEREADME.txt
%doc /awips2/java/THIRDPARTYLICENSEREADME-JAVAFX.txt
%doc /awips2/java/jre/THIRDPARTYLICENSEREADME-JAVAFX.txt
%doc /awips2/java/release
%doc /awips2/java/UNINSTALL-jai
%doc /awips2/java/UNINSTALL-jai_imageio
%doc /awips2/java/jre/COPYRIGHT

%dir /awips2/java/db
/awips2/java/db/*
%dir /awips2/java/include
/awips2/java/include/*
%dir /awips2/java/jre
#/awips2/java/jre/.systemPrefs/.systemRootModFile
%dir /awips2/java/jre/bin

%dir /awips2/java/jre/lib

%dir /awips2/java/jre/plugin
/awips2/java/jre/plugin/*
%dir /awips2/java/lib

/awips2/java/src.zip
/awips2/java/javafx-src.zip

%defattr(755,awips,fxalpha,755)
/awips2/java/bin/*
/awips2/java/lib/*
/awips2/java/jre/bin/*
/awips2/java/jre/lib/*
