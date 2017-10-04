%define _qpid_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Name:           awips2-qpid-java
Version:        6.1.4
Release:        1%{?dist}
Summary:        Java implementation of Apache Qpid
License:        Apache Software License
Group:          Development/Java
URL:            http://qpid.apache.org/
Packager: %{_build_site}

BuildRoot:      %{_build_root}
BuildArch:      noarch

%description
Java implementation of Apache Qpid.

%package common
Summary:	Java implementation of Apache Qpid - common files
Group: 		Development/Java
BuildArch:	noarch

%description common
Java implementation of Apache Qpid - common files

%package client
Summary:	Java implementation of Apache Qpid - client
Group: 		Development/Java
BuildArch:	noarch
Requires:	awips2-qpid-java-common = %{version}-%{release}
Requires:	log4j >= 1.2.12

%description client
Java implementation of Apache Qpid - client

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

QPID_SOURCE_DIR="%{_baseline_workspace}/foss/qpid-lib/"
QPID_SOURCE_FILE="qpid-client-%{version}-bin.tar.gz"

cp -v ${QPID_SOURCE_DIR}${QPID_SOURCE_FILE} %{_qpid_build_loc}
if [ $? -ne 0 ]; then
    exit 1
fi

pushd . > /dev/null 2>&1
cd %{_qpid_build_loc}
tar -xvf ${QPID_SOURCE_FILE}
if [ $? -ne 0 ]; then
    exit 1
fi
popd > /dev/null 2>&1


%build

%install
/bin/mkdir -p %{_qpid_build_loc}/awips2/qpid
if [ $? -ne 0 ]; then
    exit 1
fi
/bin/mkdir -p %{_build_root}/awips2/qpid
if [ $? -ne 0 ]; then
    exit 1
fi

pushd . > /dev/null 2>&1
cd %{_qpid_build_loc}/qpid-client/%{version}

install -dm 755 %{buildroot}/awips2/qpid/lib/opt
/bin/cp -rv lib/qpid-client-%{version}.jar \
    %{buildroot}/awips2/qpid/lib/opt
/bin/cp -rv lib/qpid-common-%{version}.jar \
    %{buildroot}/awips2/qpid/lib/opt
/bin/cp -rv lib/geronimo-jms_1.1_spec-1.1.1.jar \
    %{buildroot}/awips2/qpid/lib/opt
/bin/cp -rv lib/slf4j-api-1.7.25.jar \
    %{buildroot}/awips2/qpid/lib/opt

# license & notice
/bin/cp -rv LICENSE %{buildroot}/awips2/qpid
/bin/cp -rv NOTICE %{buildroot}/awips2/qpid

%clean
rm -rf %{buildroot}

%files common
%defattr(644,awips,fxalpha,644)
%dir /awips2/qpid
%dir /awips2/qpid/lib
%doc /awips2/qpid/LICENSE
%doc /awips2/qpid/NOTICE
%defattr(644,awips,fxalpha,755)
%dir /awips2/qpid/lib/opt
/awips2/qpid/lib/opt/qpid-common-%{version}.jar
/awips2/qpid/lib/opt/geronimo-jms_1.1_spec-1.1.1.jar
/awips2/qpid/lib/opt/slf4j-api-1.7.25.jar 


%files client
%defattr(644,awips,fxalpha,755)
%dir /awips2/qpid
%dir /awips2/qpid/lib
%dir /awips2/qpid/lib/opt
/awips2/qpid/lib/opt/qpid-client-%{version}.jar

