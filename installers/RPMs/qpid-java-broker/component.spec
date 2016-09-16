%define _qpid_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Name:           awips2-qpid-java-broker
Version:        0.32
Release:        2%{?dist}
Summary:        Java implementation of Apache Qpid Broker
License:        Apache Software License
Group:          Development/Java
URL:            http://qpid.apache.org/
BuildRoot:      %{_build_root}
BuildArch:      noarch
Provides:       awips2-base-component
Requires:       awips2-yajsw
Requires:       awips2-java
Packager: %{_build_site}

%description
Java implementation of Apache Qpid Broker.

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
if [ -d %{_qpid_build_loc} ]; then
   rm -rf %{_qpid_build_loc}
fi
mkdir -p %{_qpid_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi

QPID_SOURCE_DIR="%{_baseline_workspace}/foss/qpid-java-broker-%{version}/packaged"
QPID_SOURCE_FILE="qpid-broker-%{version}-bin.tar.gz"

cp -v ${QPID_SOURCE_DIR}/${QPID_SOURCE_FILE} %{_qpid_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null 2>&1
cd %{_qpid_build_loc}
tar -xvf ${QPID_SOURCE_FILE}
if [ $? -ne 0 ]; then
   exit 1
fi

/usr/bin/patch -p1 -i ${QPID_SOURCE_DIR}/awips.patch

popd > /dev/null 2>&1

%build

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/awips2/qpid/bin
if [ $? -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null 2>&1
cd %{_qpid_build_loc}/qpid-broker/%{version}

QPID_PATCH_DIR=%{_baseline_workspace}/foss/qpid-java-broker-%{version}/src/patch/qpid-java-broker-%{version}

/bin/cp -rv bin/* %{buildroot}/awips2/qpid/bin

mkdir -p %{buildroot}/awips2/qpid/etc
/bin/cp -rv etc/* %{buildroot}/awips2/qpid/etc

mkdir -p %{buildroot}/awips2/qpid/lib
/bin/cp -rv lib/*.jar %{buildroot}/awips2/qpid/lib
/bin/cp -rv lib/*.zip %{buildroot}/awips2/qpid/lib

/bin/cp -rv ${QPID_PATCH_DIR}/etc/* %{buildroot}/awips2/qpid/etc

mkdir -p %{buildroot}/awips2/qpid/edex/config
/bin/cp -rv ${QPID_PATCH_DIR}/base/config.json %{buildroot}/awips2/qpid
/bin/cp -rv ${QPID_PATCH_DIR}/base/edex/config/edex.json %{buildroot}/awips2/qpid/edex/config

# install the wrapper script
/bin/cp -rv ${QPID_PATCH_DIR}/wrapper/qpid-wrapper %{buildroot}/awips2/qpid/bin

# service script
mkdir -p %{buildroot}/etc/init.d
/bin/cp -rv %{_baseline_workspace}/installers/RPMs/qpid-java-broker/scripts/init.d/qpidd %{buildroot}/etc/init.d

# logs directory
mkdir -p %{buildroot}/awips2/qpid/log

%clean
rm -rf %{buildroot}

%files
%defattr(644,awips,awips,644)
/awips2/qpid/config.json
/awips2/qpid/edex/config/edex.json
%defattr(755,awips,awips,755)
%dir /awips2/qpid
%dir /awips2/qpid/log
%dir /awips2/qpid/edex
%dir /awips2/qpid/edex/config
/awips2/qpid/bin
/awips2/qpid/etc
/awips2/qpid/lib/*.jar
/awips2/qpid/lib/*.zip
%defattr(755,root,root,755)
/etc/init.d/qpidd

%changelog
* Fri Mar 20 2015 Dave Lovely <david.n.lovely@raytheon.com> - 0.32-1
- Upgrade to 0.32
* Thu Jul 31 2014 Ron Anderson <ron.anderson@raytheon.com> - 0.28-1
- Initial build.
