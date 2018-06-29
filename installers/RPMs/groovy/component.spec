%define _groovy_version 2.4.10
#
# AWIPS II Groovy Spec File
#
Name: awips2-groovy
Summary: AWIPS II Groovy Distribution
Version: %{_groovy_version}
Release: %{_component_version}.%{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: noarch
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{}_build_vendor
Packager: %{_build_site}

AutoReq: no
Provides: awips2-groovy
Requires: awips2-java

%description
AWIPS II Groovy Distribution - Contains Groovy %{_groovy_version}.

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
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi

%build

%install
mkdir -p %{_build_root}/awips2
if [ $? -ne 0 ]; then
   exit 1
fi

INSTALLER_GROOVY="%{_baseline_workspace}/installers/RPMs/groovy"

_foss_dir="%{_baseline_workspace}/foss/groovy
_groovy_dist="${_foss_dir}/packaged/apache-groovy-binary-%{_groovy_version}.zip"

unzip ${_groovy_dist} -d %{_build_root}/awips2
if [ $? -ne 0 ]; then
   exit 1
fi
mv  %{_build_root}/awips2/groovy-%{_groovy_version} \
   %{_build_root}/awips2/groovy
if [ $? -ne 0 ]; then
   exit 1
fi

%clean
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/groovy
%dir /awips2/groovy/conf
/awips2/groovy/conf/*
%dir /awips2/groovy/embeddable
/awips2/groovy/embeddable/*
%dir /awips2/groovy/indy
/awips2/groovy/indy/*
%dir /awips2/groovy/lib
/awips2/groovy/lib/*
%dir /awips2/groovy/grooid
/awips2/groovy/grooid/*
%dir /awips2/groovy/licenses
%dir /awips2/groovy/bin

%doc /awips2/groovy/LICENSE
%doc /awips2/groovy/NOTICE
%doc /awips2/groovy/licenses/antlr2-license.txt
%doc /awips2/groovy/licenses/asm-license.txt
%doc /awips2/groovy/licenses/hamcrest-license.txt
%doc /awips2/groovy/licenses/jline2-license.txt
%doc /awips2/groovy/licenses/jsr166y-license.txt
%doc /awips2/groovy/licenses/jsr223-license.txt
%doc /awips2/groovy/licenses/junit-license.txt
%doc /awips2/groovy/licenses/xstream-license.txt

%defattr(755,awips,fxalpha,755)
/awips2/groovy/bin/*
