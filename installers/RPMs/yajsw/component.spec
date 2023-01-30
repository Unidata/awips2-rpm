%define _yajsw_version 12.16

#
# AWIPS II YAJSW Spec File
#

Name: awips2-yajsw
Summary: AWIPS II yajsw Distribution
Version: %{_yajsw_version}
Release: %{_component_version}.%{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: noarch
URL: N/A
License: N/A
Distribution: N/A
Vendor: Raytheon
Packager: %{_build_site}

AutoReq: no

provides: awips2-yajsw
requires: awips2
requires: awips2-java

%description
AWIPS II yajsw Distribution - A custom compilation of yajsw %{_yajsw_version} used
by several AWIPS II components.

# disable jar repacking
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-java-repack-jars[[:space:]].*$!!g')

%prep
# Ensure that a "buildroot" has been specified.
if [ "%{_build_root}" = "" ]; then
   echo "ERROR: A BuildRoot has not been specified."
   echo "FATAL: Unable to Continue ... Terminating."
   exit 1
fi

if [ -d %{_build_root} ]; then
   rm -rf %{_build_root}
fi
/bin/mkdir -p %{_build_root}
if [ $? -ne 0 ]; then
   exit 1
fi

%install
DIST_DIR="%{_baseline_workspace}/foss/yajsw-%{_yajsw_version}/packaged"
YAJSW_SCRIPTS_DIR="%{_baseline_workspace}/installers/RPMs/yajsw/scripts"

YAJSW_ZIP="yajsw-dist.zip"

unzip ${DIST_DIR}/${YAJSW_ZIP} -d %{_build_root}

if [ $? -ne 0 ]; then
   exit 1
fi

mkdir -p %{_build_root}/etc/profile.d
if [ $? -ne 0 ]; then
   exit 1
fi
cp -rv ${YAJSW_SCRIPTS_DIR}/profile.d/* %{_build_root}/etc/profile.d/
if [ $? -ne 0 ]; then
   exit 1
fi

%clean
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/yajsw
/awips2/yajsw/*.jar
/awips2/yajsw/*.txt
%dir /awips2/yajsw/lib
/awips2/yajsw/lib/*

%attr(744,root,root) /etc/profile.d/*
