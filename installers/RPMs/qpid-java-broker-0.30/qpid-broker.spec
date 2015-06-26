Name:           awips2-qpid-java-broker
Version:        0.30
Release:        4%{?dist}
Summary:        Java implementation of Apache Qpid Broker
License:        Apache Software License
Group:          Development/Java
URL:            http://qpid.apache.org/
Source0:        qpid-java-%{version}.tar.gz
Source1:        mavenRepo.tar.gz
#mavenRepo does not contain maven source but is a repository of dependencies
# that are required to build QPID locally without access to external sources.
Patch0:         awips.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
Provides:       awips2-base-component
Requires:       awips2-yajsw

%description
Java implementation of Apache Qpid Broker.

%prep
#Extract the QPID Source
%setup -n qpid-java-%{version}
#Extract the Maven Repository
%setup -T -D -a 1 -n qpid-java-%{version}
%patch0 -p2

%build
#Flag '-o' is for Offline mode. While enabled Maven will not use any external sources, and
# will fail if the repository is blank. When offline you need to specify a repository that
# was built with the 'dependency:go-offline' command using '-Dmaven.repo.local='
mvn -o -DskipTests -Dmaven.repo.local=%{_topdir}BUILD/qpid-java-%{version}/.m2/repository clean install

tar -xzvf broker/target/qpid-broker-0.30-bin.tar.gz

%install
rm -rf %{buildroot}

cd qpid-broker

mkdir -p %{buildroot}/awips2/qpid/bin
install -pm 755 0.30/bin/* %{buildroot}/awips2/qpid/bin

mkdir -p %{buildroot}/awips2/qpid/etc
install -pm 755 0.30/etc/* %{buildroot}/awips2/qpid/etc

mkdir -p %{buildroot}/awips2/qpid/lib
install -pm 755 0.30/lib/*.jar %{buildroot}/awips2/qpid/lib
install -pm 755 0.30/lib/*.zip %{buildroot}/awips2/qpid/lib

install -pm 644 %{_patchdir}/qpid-java-broker-%{version}/etc/* %{buildroot}/awips2/qpid/etc

mkdir -p %{buildroot}/awips2/qpid/edex/config
install -pm 644 %{_patchdir}/qpid-java-broker-%{version}/base/config.json %{buildroot}/awips2/qpid
install -pm 644 %{_patchdir}/qpid-java-broker-%{version}/base/edex/config/edex.json %{buildroot}/awips2/qpid/edex/config

# install the wrapper script
install -pm 755 %{_patchdir}/qpid-java-broker-%{version}/wrapper/qpid-wrapper %{buildroot}/awips2/qpid/bin

# service script
mkdir -p %{buildroot}/etc/init.d
install -pm 755 %{_patchdir}/qpid-java-broker-%{version}/wrapper/qpidd %{buildroot}/etc/init.d

# logs directory
mkdir -p %{buildroot}/awips2/qpid/log

%clean
rm -rf %{buildroot}

%files
%defattr(-,awips,fxalpha,-)
/awips2/qpid
%defattr(755,root,root,755)
/etc/init.d/qpidd

%changelog
* Wed Jul 24 2015 David Lovely <david.lovely@raytheon.com> - 0.30-4
- Build from source to include a fix for BindingImpl Memory Leak
* Mon Nov 10 2014 David Lovely <david.lovely@raytheon.com> - 0.30-1
- Initial QPID 0.30
