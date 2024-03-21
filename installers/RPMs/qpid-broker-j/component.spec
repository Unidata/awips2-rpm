%define _qpid_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Name:           awips2-qpid-broker-j
Version:        7.1.12
Release:        9%{?dist}
Summary:        Java implementation of Apache Qpid Broker
License:        Apache Software License
Group:          Development/Java
URL:            http://qpid.apache.org/
BuildRoot:      %{_build_root}
BuildArch:      noarch
Requires:       awips2-yajsw
Requires:       awips2-java
Requires:       awips2-java-security
Requires:       awips2-watchdog
BuildRequires:  awips2-ant
Packager:       %{_build_site}
Obsoletes:      awips2-qpid-java-broker
Obsoletes:      awips2-qpid-java-common
Obsoletes:      awips2-qpid-java-client

# These obsoletes are for RPMs that were part of early 20.1.1 builds.
# They were added to allow this RPM to install over earlier builds.
# They can be removed after all 20.1.1/20.3.1 installations have
# installed awips2-qpid-broker-j 7.1.4-1 or higher.
Obsoletes:      awips2-qpid-jms-client
Obsoletes:      awips2-qpid-jms-common

%description
Java implementation of Apache Qpid Broker.

%package -n %name-alr
Group: AWIPSII
Summary: ALR configuration for the Apache Qpid Broker.
Requires: awips2-qpid-broker-j = %{version}-%{release}

%description -n %name-alr
The Qpid Broker-J ALR package contains the necessary qpid
broker configuration files for SJU hydro processing.

If you desire to enable SJU hydro processing, you need to
install this package on top of the base broker package.

# disable jar repacking
%global __jar_repack 0

%prep
# Ensure that a "buildroot" has been specified.
if [ "%{_build_root}" = "" ]; then
   echo "ERROR: A BuildRoot has not been specified."
   echo "FATAL: Unable to Continue ... Terminating."
   exit 1
fi

if [ -d %{_build_root} ]; then
   rm --recursive --force %{_build_root}
fi
if [ -d %{_qpid_build_loc} ]; then
   rm --recursive --force %{_qpid_build_loc}
fi
mkdir --parents %{_qpid_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi

QPID_SOURCE_DIR="%{_baseline_workspace}/foss/qpid-broker-j-%{version}/packaged"
QPID_SOURCE_FILE="apache-qpid-broker-j-%{version}-bin.tar.gz"

/bin/cp --verbose ${QPID_SOURCE_DIR}/${QPID_SOURCE_FILE} %{_qpid_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi

%build
QPID_SOURCE_DIR="%{_baseline_workspace}/foss/qpid-broker-j-%{version}/packaged"
QPID_SOURCE_FILE="apache-qpid-broker-j-%{version}-bin.tar.gz"

pushd . > /dev/null 2>&1
cd %{_qpid_build_loc}
tar --extract --verbose --file="${QPID_SOURCE_FILE}"
if [ $? -ne 0 ]; then
   exit 1
fi

cd "${QPID_SOURCE_DIR}/../src/patch/qpid-broker-j/extensions/org.apache.qpid.server.derby.repack" || exit 1
/awips2/ant/bin/ant jar || exit 1
/bin/cp qpid-broker-plugins-derby-repacking-store.jar %{_qpid_build_loc}/qpid-broker/%{version}/lib/ || exit 1
popd > /dev/null 2>&1

%install
rm --recursive --force %{buildroot}

mkdir --parents %{buildroot}/awips2/qpid/bin
if [ $? -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null 2>&1
cd %{_qpid_build_loc}/qpid-broker/%{version}

QPID_PATCH_DIR=%{_baseline_workspace}/foss/qpid-broker-j-%{version}/src/patch/qpid-broker-j

/bin/cp --recursive --verbose bin/* %{buildroot}/awips2/qpid/bin

mkdir --parents %{buildroot}/awips2/qpid/lib
/bin/cp --recursive --verbose lib/*.jar %{buildroot}/awips2/qpid/lib
/bin/cp --recursive --verbose lib/*.zip %{buildroot}/awips2/qpid/lib

#Apply derby patch
/bin/rm %{buildroot}/awips2/qpid/lib/derby-10.13.1.1.jar
/bin/cp ${QPID_PATCH_DIR}/lib/derby-10.15.2.0.jar %{buildroot}/awips2/qpid/lib
/bin/cp ${QPID_PATCH_DIR}/lib/derbyshared-10.15.2.0.jar %{buildroot}/awips2/qpid/lib
/bin/cp ${QPID_PATCH_DIR}/lib/derbytools-10.15.2.0.jar %{buildroot}/awips2/qpid/lib

#Remove deprecated bonecp jars
/bin/rm %{buildroot}/awips2/qpid/lib/bonecp-0.7.1.RELEASE.jar
/bin/rm %{buildroot}/awips2/qpid/lib/qpid-broker-plugins-jdbc-provider-bone-%{version}.jar

#Apply bcel patch
/bin/rm %{buildroot}/awips2/qpid/lib/bcel-6.2.jar
/bin/cp ${QPID_PATCH_DIR}/lib/bcel-6.6.1.jar %{buildroot}/awips2/qpid/lib

#Apply guava patch
/bin/rm %{buildroot}/awips2/qpid/lib/guava-30.0-jre.jar
/bin/cp ${QPID_PATCH_DIR}/lib/guava-32.0.0-jre.jar %{buildroot}/awips2/qpid/lib

#Apply jetty patch
/bin/rm %{buildroot}/awips2/qpid/lib/jetty-continuation-9.4.35.v20201120.jar
/bin/rm %{buildroot}/awips2/qpid/lib/jetty-http-9.4.35.v20201120.jar
/bin/rm %{buildroot}/awips2/qpid/lib/jetty-io-9.4.35.v20201120.jar
/bin/rm %{buildroot}/awips2/qpid/lib/jetty-security-9.4.35.v20201120.jar
/bin/rm %{buildroot}/awips2/qpid/lib/jetty-server-9.4.35.v20201120.jar
/bin/rm %{buildroot}/awips2/qpid/lib/jetty-servlet-9.4.35.v20201120.jar
/bin/rm %{buildroot}/awips2/qpid/lib/jetty-servlets-9.4.35.v20201120.jar
/bin/rm %{buildroot}/awips2/qpid/lib/jetty-util-9.4.35.v20201120.jar
/bin/rm %{buildroot}/awips2/qpid/lib/jetty-util-ajax-9.4.35.v20201120.jar
/bin/cp ${QPID_PATCH_DIR}/lib/jetty-continuation-9.4.53.v20231009.jar %{buildroot}/awips2/qpid/lib
/bin/cp ${QPID_PATCH_DIR}/lib/jetty-http-9.4.53.v20231009.jar %{buildroot}/awips2/qpid/lib
/bin/cp ${QPID_PATCH_DIR}/lib/jetty-io-9.4.53.v20231009.jar %{buildroot}/awips2/qpid/lib
/bin/cp ${QPID_PATCH_DIR}/lib/jetty-security-9.4.53.v20231009.jar %{buildroot}/awips2/qpid/lib
/bin/cp ${QPID_PATCH_DIR}/lib/jetty-server-9.4.53.v20231009.jar %{buildroot}/awips2/qpid/lib
/bin/cp ${QPID_PATCH_DIR}/lib/jetty-servlet-9.4.53.v20231009.jar %{buildroot}/awips2/qpid/lib
/bin/cp ${QPID_PATCH_DIR}/lib/jetty-servlets-9.4.53.v20231009.jar %{buildroot}/awips2/qpid/lib
/bin/cp ${QPID_PATCH_DIR}/lib/jetty-util-9.4.53.v20231009.jar %{buildroot}/awips2/qpid/lib
/bin/cp ${QPID_PATCH_DIR}/lib/jetty-util-ajax-9.4.53.v20231009.jar %{buildroot}/awips2/qpid/lib

#Apply jackson patch
/bin/rm %{buildroot}/awips2/qpid/lib/jackson-annotations-2.12.1.jar
/bin/rm %{buildroot}/awips2/qpid/lib/jackson-core-2.12.1.jar
/bin/rm %{buildroot}/awips2/qpid/lib/jackson-databind-2.12.1.jar
/bin/cp ${QPID_PATCH_DIR}/lib/jackson-annotations-2.15.2.jar %{buildroot}/awips2/qpid/lib
/bin/cp ${QPID_PATCH_DIR}/lib/jackson-core-2.15.2.jar %{buildroot}/awips2/qpid/lib
/bin/cp ${QPID_PATCH_DIR}/lib/jackson-databind-2.15.2.jar %{buildroot}/awips2/qpid/lib

mkdir -p %{buildroot}/awips2/qpid/etc
/bin/cp -rv ${QPID_PATCH_DIR}/etc/* %{buildroot}/awips2/qpid/etc


mkdir --parents %{buildroot}/awips2/qpid/tls
/bin/cp --recursive --verbose ${QPID_PATCH_DIR}/base/root.crt %{buildroot}/awips2/qpid/tls
/bin/cp --recursive --verbose ${QPID_PATCH_DIR}/base/root.key %{buildroot}/awips2/qpid/tls
/bin/cp --recursive --verbose ${QPID_PATCH_DIR}/base/initialConfig.json %{buildroot}/awips2/qpid
/bin/cp --recursive --verbose ${QPID_PATCH_DIR}/base/initialConfigAlr.json %{buildroot}/awips2/qpid

# license & notice
/bin/cp --recursive --verbose LICENSE %{buildroot}/awips2/qpid
/bin/cp --recursive --verbose NOTICE %{buildroot}/awips2/qpid

# install the wrapper script
/bin/cp --recursive --verbose ${QPID_PATCH_DIR}/wrapper/qpid-wrapper %{buildroot}/awips2/qpid/bin

# service script
mkdir --parents ${RPM_BUILD_ROOT}/%{_unitdir}/
/bin/cp --verbose %{_baseline_workspace}/installers/RPMs/qpid-broker-j/scripts/systemd/qpidd.service ${RPM_BUILD_ROOT}/%{_unitdir}/ 

# watchdog test/repair script
mkdir --parents %{buildroot}/etc/watchdog.d
/bin/cp --recursive --verbose %{_baseline_workspace}/installers/RPMs/qpid-broker-j/scripts/watchdog.d/qpid_watchdog.sh %{buildroot}/etc/watchdog.d

# logs directory
mkdir --parents %{buildroot}/awips2/qpid/log

mkdir --parents %{buildroot}/data/fxa/qpid
if [ $? -ne 0 ]; then
   exit 1
fi


%post
# Register and turn on the qpidd service
/bin/systemctl enable --quiet qpidd.service

tls_dir="/awips2/qpid/tls"
if [ ! -e "${tls_dir}/server.crt" ]; then
  cn=$(hostname -s)

  names[0]=$cn
  names[1]=$( echo $cn | cut -d- -f1  )
  names[2]=$(hostname)
  names[3]=localhost
  names=($(echo "${names[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))

  echo "subjectAltName = @alt_names" >> "${tls_dir}/server.ext"
  echo "[ alt_names ]" >> "${tls_dir}/server.ext"
  i=1
  for name in ${names[@]}; do
    echo "DNS.$((i++)) = $name" >> "${tls_dir}/server.ext"
  done

  openssl req -new -nodes \
              -subj "/O=AWIPS/OU=Testing/CN=$cn" \
              -keyout "${tls_dir}/server.key" \
              -out "${tls_dir}/server.req"
  openssl x509 -req -days 1825 \
               -in "${tls_dir}/server.req" \
               -CA "${tls_dir}/root.crt" \
               -CAkey "${tls_dir}/root.key" \
               -set_serial 0x$(openssl rand -hex 8) \
               -out "${tls_dir}/server.crt" \
               -extfile "${tls_dir}/server.ext"

  chmod g=,o= "${tls_dir}/server.key"
  chown awips:fxalpha "${tls_dir}/server.key"
  chown awips:fxalpha "${tls_dir}/server.crt"

  rm "${tls_dir}/server.req" "${tls_dir}/server.ext"
fi

rm "${tls_dir}/root.key"

%preun
if [ ${1} = 0 ]; then
    # stop the service and disable the service script
    /bin/systemctl disable --now --quiet qpidd.service
fi

%post -n %name-alr
sed --in-place --expression="s/initialConfig.json/initialConfigAlr.json/" /awips2/qpid/etc/wrapper.conf

%clean
rm --recursive --force %{buildroot}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/qpid
%doc /awips2/qpid/LICENSE
%doc /awips2/qpid/NOTICE
/awips2/qpid/initialConfig.json
%dir /data/fxa/qpid

%defattr(600,awips,fxalpha,700)
%dir /awips2/qpid/tls
%config(noreplace)/awips2/qpid/tls/root.crt
%config(noreplace)/awips2/qpid/tls/root.key

%defattr(644,awips,fxalpha,755)
%dir /awips2/qpid/etc
/awips2/qpid/etc/wrapper.conf

%dir /awips2/qpid/lib
/awips2/qpid/lib/*.jar
/awips2/qpid/lib/*.zip

%dir /awips2/qpid/log

%defattr(755,awips,fxalpha,755)
%dir /awips2/qpid/bin
/awips2/qpid/bin/*

%attr(644,root,root) %{_unitdir}/qpidd.service

%attr(744,root,root) /etc/watchdog.d/qpid_watchdog.sh

%files -n %name-alr
%defattr(644,awips,fxalpha,755)
/awips2/qpid/initialConfigAlr.json

%changelog
* Wed Dec 07 2023 Freddy Camacho <freddy.camacho@noaa.gov> - 7.1.12-8
- Updated spec to manually patch jetty-continuation-9.4.53.v20231009.jar, jetty-http-9.4.53.v20231009.jar, jetty-io-9.4.53.v20231009.jar, jetty-security-9.4.53.v20231009.jar, jetty-server-9.4.53.v20231009.jar, jetty-servlet-9.4.53.v20231009.jar, jetty-servlets-9.4.53.v20231009.jar, jetty-util-9.4.53.v20231009.jar, jetty-util-ajax-9.4.53.v20231009.jar
* Wed Oct 03 2023 Sarah Johnston <sarah.johnston@noaa.gov> - 7.1.12-8
- Updated spec to manually patch jetty-continuation-9.4.52.v20230823.jar, jetty-http-9.4.52.v20230823.jar, jetty-io-9.4.52.v20230823.jar, jetty-security-9.4.52.v20230823.jar, jetty-server-9.4.52.v20230823.jar, jetty-servlet-9.4.52.v20230823.jar, jetty-servlets-9.4.52.v20230823.jar, jetty-util-9.4.52.v20230823.jar, jetty-util-ajax-9.4.52.v20230823.jar
* Wed Sep 06 2023 Ada Lockleigh <ada.lockleigh@noaa.gov> - 7.1.12-7
- Updated spec to manually patch jetty-continuation-9.4.51.v20230217.jar, jetty-http-9.4.51.v20230217.jar, jetty-io-9.4.51.v20230217.jar, jetty-security-9.4.51.v20230217.jar, jetty-server-9.4.51.v20230217.jar, jetty-servlet-9.4.51.v20230217.jar, jetty-servlets-9.4.51.v20230217.jar, jetty-util-9.4.51.v20230217.jar, jetty-util-ajax-9.4.51.v20230217.jar
* Thu Aug 31 2023 Mark Peters <mark.a.peters@rtx.com> - 7.1.12-6
- Remove central registry configuration
* Mon Aug 07 2023 Zachary Alberts <zachary.alberts@raytheon.com> - 7.1.12-6
- Updated spec to manually patch jackson-annotations-2.15.2.jar, jackson-core-2.15.2.jar, jackson-databind-2.15.2.jar
* Tue Jun 06 2023 Sarah Johnston <sarah.johnston@raytheon.com> - 7.1.12-5
- Updated spec to manually patch guava 32.0.0-jre jar
* Wed May 17 2023 Nate Jensen <nate.jensen@raytheon.com> - 7.1.12-4
- Updated spec to manually patch guava 31.1-jre jar
* Wed Dec 14 2022 Derek Haines <derek.haines@noaa.gov> - 7.1.12-4
- Updated spec to manually patch bcel 6.6.1 jar
* Tue Nov 25 2022 Tom Huggins <thomas.huggins@raytheon.com> - 7.1.12-3
- Updated spec to remove deprecated bonecp jars.
* Thu Sep 22 2022 Nate Jensen <nate.jensen@raytheon.com> - 7.1.12-2
- Add in derby repacking message store jar
* Wed May 25 2022 Lisa Singh <lisa.e.singh@raytheon.com> - 7.1.12
- Updated spec to manually patch derby 10.15.2.0 jars.
* Fri May 06 2022 Tom Gurney <tom.gurney@raytheon.com> 7.1.8-8
- Add dependency on awips2-java-security package
* Thu Jan 27 2022 David Gillingham <david.gillingham@raytheon.com> 7.1.8-8
- Migrated to systemd service units.
- Expanded command arguments for readability.
* Tue Aug 24 2021 Srinivas Moorthy <srinivas.moorthy@noaa.gov> 7.1.8-6
- within apache-qpid-broker-j-7.1.8-bin.tar.gz, added derbyshared-10.15.2.0.jar, derby-10.15.2.0.jar, and derbytools-10.15.2.0.jar
- removed derby-10.13.1.1.jar
- modified NOTICE with Derby copyright info from 10.15.2.0
* Tue Apr 20 2021 David Gillingham <david.gillingham@raytheon.com> 7.1.8-5
- Set ownership of /data/fxa/qpid/ to awips:fxalpha.
* Thu Dec 10 2020 Tom Gurney <tom.gurney@raytheon.com> 7.1.8-3
- Move TLS-related stuff to /awips2/qpid/tls
* Mon Jul 27 2020 Ron Anderson <ron.anderson@raytheon.com> - 7.1.8-2
- Specify initial configuration in initialConfig.json
- Specify virtualHostInitialConfiguration in initialConfig.json files
* Tue Mar 17 2020 Ron Anderson <ron.anderson@raytheon.com> - 7.1.8-1
- Mark root.crt and root.key as %config(noreplace)
* Fri Feb 14 2020 Matt Richardson <matthew.richardson@raytheon.com> - 7.1.8-0
- Upgrade to version 7.1.8 with certificate and web console fixes
* Thu Jan 30 2020 Ron Anderson <ron.anderson@raytheon.com> - 7.1.4-1
- Remove unnecessary dependency on qpid-jms-common
* Wed Jan 22 2020 Matt Richardson <matthew.richardson@raytheon.com> - 7.1.4-0
- Ugrade to version 7.1.4
* Fri Jul 26 2019 Matt Richardson <matthew.richardson@raytheon.com> - 7.1.0-0
- Upgrade to latest version of Broker-J for Qpid Proton.
* Tue Jul 25 2017 Ben Steffensmeier <ben.steffensmeier@raytheon.com> - 0.32-9
- Use secure file permissions in derby. 
* Mon Feb 27 2017 Ben Steffensmeier <ben.steffensmeier@raytheon.com> - 0.32-7
- Only allow SSL connections
* Wed Jan 25 2017 Ben Steffensmeier <ben.steffensmeier@raytheon.com> - 0.32-6
- Include SSL ports in default config, generate test server certificates.
* Wed Oct 19 2016 Richard Peter <richard.peter@raytheon.com> - 0.32-3
- Update memory settings (Originally from #5927)
* Fri Mar 20 2015 Dave Lovely <david.n.lovely@raytheon.com> - 0.32-1
- Upgrade to 0.32
* Thu Jul 31 2014 Ron Anderson <ron.anderson@raytheon.com> - 0.28-1
- Initial build.
