Name: awips2-java-security
Summary: AWIPS II Java security configuration
Version: 1
Release: %{_component_version}.%{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
URL: N/A
License: N/A
Distribution: N/A
Vendor: ${_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: ca-certificates

%description
Contains security configuration for AWIPS II Java applications

%prep
if [ "%{_build_root}" = "" ]; then
   echo "ERROR: A buildroot has not been specified. Exiting"
   exit 1
fi

if [ -d %{_build_root} ]; then
   rm -rf %{_build_root} || exit 1
fi

%install
install -D "%{_baseline_workspace}/installers/RPMs/java-security/java.security" \
    "%{_build_root}/awips2/etc/java.security" || exit 1

install -D "%{_baseline_workspace}/installers/RPMs/java-security/java.security.allow-md5" \
    "%{_build_root}/awips2/etc/java.security.allow-md5" || exit 1

# Install the DoD root certificate needed for Thin Client.
# This certificate can be found in the bundle located here (as of Aug 2020):
# https://dl.dod.cyber.mil/wp-content/uploads/pki-pke/zip/unclass-certificates_pkcs7_v5-6_dod.zip
dod_cert="%{_baseline_workspace}/installers/RPMs/java-security/DoDRootCA2.pem"
certs_target_dir="%{_build_root}/etc/pki/ca-trust/source/anchors"
install -D "$dod_cert" "$certs_target_dir"/DoDRootCA2.pem || exit 1

%post
echo Running update-ca-trust
update-ca-trust
if [ $? -ne 0 ]; then
    echo "ERROR: 'update-ca-trust' failed."
    echo "You will need to run this command as root to add the DoD root"
    echo "certificate to the Java truststore."
    exit 1
fi

%clean
rm -rf ${_build_root}

%files
%defattr(644,awips,fxalpha,755)
/awips2/etc/java.security
/awips2/etc/java.security.allow-md5
%attr(644,root,root) /etc/pki/ca-trust/source/anchors/DoDRootCA2.pem

%changelog
* Thu May 05 2022 Tom Gurney <tom.gurney@raytheon.com>
- Initial creation
