#
# AWIPS II watchdog Spec File
#

Name: awips2-watchdog
Summary: AWIPS II watchdog Distribution
Version: %{_component_version}
Release: %{_component_release}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: noarch
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no

provides: awips2-watchdog
requires: bash
requires: watchdog

%description
AWIPS II watchdog Distribution - A custom release of watchdog used
by several AWIPS II components.

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

%install
mkdir -p %{_build_root}
if [ $? -ne 0 ]; then
   exit 1
fi

mkdir -p %{_build_root}/etc/watchdog.d/utilities
if [ $? -ne 0 ]; then
   exit 1
fi

WATCHDOG_UTILITIES_DIR="%{_baseline_workspace}/installers/RPMs/watchdog/utilities"

if [ $? -ne 0 ]; then
   exit 1
fi

cp -rv ${WATCHDOG_UTILITIES_DIR}/* %{_build_root}/etc/watchdog.d/utilities
if [ $? -ne 0 ]; then
   exit 1
fi

%post
# need to make an update to the default watchdog.conf file
sed -i -e '$ainterval = 58' /etc/watchdog.conf

%clean
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(755,root,root,755)
%dir /etc/watchdog.d/utilities
/etc/watchdog.d/utilities/*
