# disable jar repacking
%global __jar_repack 0

#
# AWIPS II Java Spec File
#
Name: awips2-java
Summary: AWIPS II Java Distribution

# Version must always be an integer equal to the Java major version. This is
# used by the RPM build to locate the correct version of Java in
# /etc/alternatives.
Version: 17

# Epoch was incremented to to reset the versioning scheme after we switched
# from packaging our own Java to depending on the system Java package.
#
# DO NOT remove or decrement the Epoch. Do not change the Epoch as part of
# normal Java upgrades or other routine changes to this package.
# 
# The only acceptable change to the Epoch is to increment it if and when the
# version numbering scheme needs to be changed again.
Epoch: 2

Release: %{_component_version}.%{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
URL: N/A
License: N/A
Distribution: N/A
Vendor: ${_build_vendor}
Packager: %{_build_site}

AutoReq: no
BuildRequires: java-17-openjdk-devel
Requires: java-17-openjdk-devel
Requires: tzdata-java
Provides: awips2-java = %{version}

%description
AWIPS II Java Distribution - Contains the /awips2/java symlink plus additional
scripts used by AWIPS II

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

%install
# Install /awips2/java symlink to system JRE
mkdir -p %{_build_root}/awips2 || exit 1
ln -s /etc/alternatives/jre_%{version} %{_build_root}/awips2/java || exit 1

# Install profile.d scripts
java_scripts_dir="%{_baseline_workspace}/installers/RPMs/java/scripts/profile.d"
mkdir -p %{_build_root}/etc/profile.d || exit 1
cp -v ${java_scripts_dir}/* %{_build_root}/etc/profile.d || exit 1


%clean
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(644,awips,fxalpha,755)
%attr(755,root,root) /etc/profile.d/awips2Java.csh
%attr(755,root,root) /etc/profile.d/awips2Java.sh
/awips2/java

%changelog
* Thu Apr 04 2025 Tom Gurney <thomas.gurney@rtx.com>
- Upgrade to Java 17
* Mon Aug 28 2023 David Gillingham <david.gillingham@rtx.com>
- Add tzdata-java to dependency list to resolve central registry qpid install issues.
* Thu May 05 2022 Tom Gurney <tom.gurney@raytheon.com>
- Moved security stuff to new awips2-java-security package
* Wed Aug 19 2020 Tom Gurney <tom.gurney@raytheon.com>
- Replaced custom Java build with dependency on java-11-openjdk-devel
- Removed unneeded (and expired) PyDev certificate
- Removed expired DoD certificate (left only the root cert)
- Changed /awips2/java to a symlink into /etc/alternatives

%doc /awips2/java/NOTICE
