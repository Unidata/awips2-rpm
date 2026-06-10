%define contentdir /var/www

%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)

Summary: Apache HTTP Server Configured for PyPIES
Name: awips2-httpd-pypies
Version: 2.4.58
Release: 7%{?dist}
URL: http://httpd.apache.org/
License: Apache License, Version 2.0
Group: AWIPSII
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Requires: /etc/mime.types
Obsoletes: awips2-httpd-pypies-suexec
Requires(pre): /usr/sbin/useradd
Requires(post): chkconfig
Requires: awips2-pypies
Requires: awips2-hdf5, awips2-python, awips2-python-dynamicserialize, awips2-python-h5py
Requires: awips2-python-thrift, awips2-python-ufpy, awips2-python-werkzeug
Requires: awips2-python-numpy
Requires: httpd, httpd-tools, mod_ldap, mod_proxy_html, mod_ssl, python%{_installed_python_short}-mod_wsgi
Requires: awips2-watchdog
Packager: %{_build_site}

%description
Apache is a powerful, full-featured, efficient, and freely-available
Web server. Apache is also the most popular Web server on the
Internet.

%prep

%install
HTTPD_PYPIES_DIR=awips2/httpd_pypies
mkdir --parents $RPM_BUILD_ROOT/$HTTPD_PYPIES_DIR/bin
mkdir --parents $RPM_BUILD_ROOT/$HTTPD_PYPIES_DIR/etc/httpd/conf
mkdir --parents $RPM_BUILD_ROOT/$HTTPD_PYPIES_DIR/etc/httpd/conf.d
mkdir --parents $RPM_BUILD_ROOT/$HTTPD_PYPIES_DIR/etc/httpd/run
mkdir --parents $RPM_BUILD_ROOT/$HTTPD_PYPIES_DIR/var/www/html
mkdir --parents $RPM_BUILD_ROOT/$HTTPD_PYPIES_DIR/var/www/wsgi
mkdir --parents $RPM_BUILD_ROOT/$HTTPD_PYPIES_DIR/var/log/httpd
mkdir --parents $RPM_BUILD_ROOT/usr/lib/systemd/system
mkdir --parents $RPM_BUILD_ROOT/etc/cron.daily
mkdir --parents $RPM_BUILD_ROOT/etc/watchdog.d

# install systemd unit files
install -m644 %{_baseline_workspace}/installers/RPMs/httpd-pypies/configuration/systemd/httpd-pypies.service \
   $RPM_BUILD_ROOT/usr/lib/systemd/system

install -m644 %{_baseline_workspace}/installers/RPMs/httpd-pypies/configuration/systemd/httpd-pypies-logging.service \
   $RPM_BUILD_ROOT/usr/lib/systemd/system

# install environment file for systemd unit file
install -m644 %{_baseline_workspace}/installers/RPMs/httpd-pypies/configuration/bin/httpd_pypies_env \
   $RPM_BUILD_ROOT/$HTTPD_PYPIES_DIR/bin

# install pypies logging service script
install -m755 %{_baseline_workspace}/installers/RPMs/httpd-pypies/configuration/bin/pypies_logging_service.sh \
   $RPM_BUILD_ROOT/$HTTPD_PYPIES_DIR/bin

# install the watchdog test/repair script
install -m755 %{_baseline_workspace}/installers/RPMs/httpd-pypies/configuration/etc/watchdog.d/pypies_watchdog.sh \
   $RPM_BUILD_ROOT/etc/watchdog.d/pypies_watchdog.sh

# install cron job
install -m755 %{_baseline_workspace}/installers/RPMs/httpd-pypies/configuration/etc/cron.daily/pypiesLogCleanup.sh \
   ${RPM_BUILD_ROOT}/etc/cron.daily

# Install the pypies configuration.
install -m644 %{_baseline_workspace}/installers/RPMs/httpd-pypies/configuration/apache/pypies.conf \
   ${RPM_BUILD_ROOT}/awips2/httpd_pypies/etc/httpd/conf.d

# install the pypies wsgi
install -m644 %{_baseline_workspace}/installers/RPMs/httpd-pypies/configuration/apache/pypies.wsgi \
    ${RPM_BUILD_ROOT}/awips2/httpd_pypies/var/www/wsgi

# Install & Override the httpd configuration.
install -m644 %{_baseline_workspace}/installers/RPMs/httpd-pypies/configuration/conf/httpd.conf \
   ${RPM_BUILD_ROOT}/awips2/httpd_pypies/etc/httpd/conf

%pre
# Add the "apache" user
/usr/sbin/useradd -c "Apache" -u 48 \
    -s /sbin/nologin -r -d %{contentdir} apache 2> /dev/null || :

%post
# Register the httpd service
/bin/systemctl enable httpd-pypies.service

# create the hdf5_locks dir
if [ ! -d /awips2/hdf5_locks ]; then
    mkdir /awips2/hdf5_locks
fi

# create ram drive
hasRamdrive=$( grep -c hdf5_locks /etc/fstab )
if [ $hasRamdrive == 0 ]; then
    echo "tmpfs       /awips2/hdf5_locks/ tmpfs   nodev,nosuid,noexec,size=10M,nofail    0 0" >> /etc/fstab
fi

# mount and fix perms
mount /awips2/hdf5_locks
chown awips:fxalpha /awips2/hdf5_locks
chmod 755 /awips2/hdf5_locks

%preun
if [ $1 = 0 ]; then
    /bin/systemctl stop httpd-pypies.service > /dev/null 2>&1
    /bin/systemctl disable httpd-pypies.service

    # clean up ramdrive
    umount -l /awips2/hdf5_locks
    rm -rf /awips2/hdf5_locks
    sed -i '/hdf5_locks/d' /etc/fstab
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,awips,fxalpha)
%dir /awips2/httpd_pypies
%dir /awips2/httpd_pypies/etc
%dir /awips2/httpd_pypies/etc/httpd
%dir /awips2/httpd_pypies/etc/httpd/conf
%dir /awips2/httpd_pypies/etc/httpd/conf.d
%dir /awips2/httpd_pypies/etc/httpd/run
%dir /awips2/httpd_pypies/var
%dir /awips2/httpd_pypies/var/www
%dir /awips2/httpd_pypies/var/www/html
%dir /awips2/httpd_pypies/var/www/wsgi
%{_sysconfdir}/cron.daily/pypiesLogCleanup.sh
%attr(744,root,root) /etc/watchdog.d/pypies_watchdog.sh
/awips2/httpd_pypies/var/www/wsgi/pypies.wsgi
/awips2/httpd_pypies/bin/httpd_pypies_env
/awips2/httpd_pypies/bin/pypies_logging_service.sh
/awips2/httpd_pypies/etc/httpd/conf/httpd.conf
/awips2/httpd_pypies/etc/httpd/conf.d/pypies.conf

%defattr(-,root,root)
/usr/lib/systemd/system/httpd-pypies.service
/usr/lib/systemd/system/httpd-pypies-logging.service
%dir /awips2/httpd_pypies/var/log/httpd
