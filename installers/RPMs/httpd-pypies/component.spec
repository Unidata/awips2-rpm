%define contentdir /var/www
%define suexec_caller apache
%define mmn 20120211

%define FOSS_DIR "%{_baseline_workspace}/foss"
%define HTTP_FOSS_DIR "%{_baseline_workspace}/foss/%{HTTP_PACKAGE_NAME}/packaged/"
%define HTTP_PACKAGE_NAME "httpd-%{version}"
%define HTTP_SOURCE_TAR "%{HTTP_PACKAGE_NAME}.tar.gz"
%define RPMBUILD_PYPIES_DIR "%{_baseline_workspace}/rpmbuild/BUILD/httpd-pypies"
%define RPMBUILD_HTTP_DIR %RPMBUILD_PYPIES_DIR/%HTTP_PACKAGE_NAME
%define DISTCACHE distcache-1.4.5
%define MOD_WSGI_VERSION 3.5
%define APR_VERSION 1.6.2
%define APR_UTIL_VERSION 1.6.0

Summary: Apache HTTP Server
Name: awips2-httpd-pypies
Version: 2.4.27
Release: 1%{?dist}
URL: http://httpd.apache.org/
License: Apache License, Version 2.0
Group: AWIPSII
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: autoconf, perl, pkgconfig, findutils, lua-devel
BuildRequires: zlib-devel, libselinux-devel, libuuid-devel
BuildRequires: pcre-devel >= 5.0
Requires: initscripts >= 8.36, /etc/mime.types
Obsoletes: awips2-httpd-pypies-suexec
Requires(pre): /usr/sbin/useradd
Requires(post): chkconfig
Provides: webserver
Provides: mod_dav = %{version}-%{release}, httpd-suexec = %{version}-%{release}
Provides: %name-mmn = %{mmn}
Requires: %name-tools >= %{version}-%{release}
Requires: awips2-pypies
Requires: awips2-tools, awips2-python, awips2-python-h5py
Requires: awips2-python-numpy, awips2-python-werkzeug
Vendor: %{_build_vendor}
Packager: %{_build_site}

%description
Apache is a powerful, full-featured, efficient, and freely-available
Web server. Apache is also the most popular Web server on the
Internet.

%package -n %name-tools
Group: AWIPSII
Summary: Tools for use with the Apache HTTP Server
Requires: %name = %{version}-%{release}

%description -n %name-tools
The httpd-tools package contains tools which can be used with 
the Apache HTTP Server.

%prep

if [ "%{_build_root}" = "" ]; then
   echo "ERROR: A BuildRoot has not been specified."
   echo "FATAL: Unable to Continue ... Terminating."
   exit 1
fi

if [ -d %{_build_root} ]; then
   rm -rf %{_build_root}
fi

if [ -d %{RPMBUILD_PYPIES_DIR} ]; then
   rm -rf %{RPMBUILD_PYPIES_DIR}
fi

#create the build dir
mkdir -p %{RPMBUILD_PYPIES_DIR}
if [ $? -ne 0 ]; then
   exit 1
fi

#extract the http source
cd %RPMBUILD_PYPIES_DIR
cp -v %HTTP_FOSS_DIR/%HTTP_SOURCE_TAR .
tar xf %{HTTP_SOURCE_TAR}

pushd .

cd %{HTTP_PACKAGE_NAME}/srclib

#copy the apr and apr-util source tar to srclib directory
cp -v %{FOSS_DIR}/apr/packaged/apr-%{APR_VERSION}.tar.gz .
cp -v %{FOSS_DIR}/apr-util/packaged/apr-util-%{APR_UTIL_VERSION}.tar.gz .

#extract apr and apr-util
tar xf apr-%{APR_VERSION}.tar.gz
tar xf apr-util-%{APR_UTIL_VERSION}.tar.gz

#create symlinks for the build
ln -s apr-%{APR_VERSION} apr
ln -s apr-util-%{APR_UTIL_VERSION} apr-util

popd

cd %HTTP_PACKAGE_NAME
# Safety check: prevent build if defined MMN does not equal upstream MMN.
vmmn=`echo MODULE_MAGIC_NUMBER_MAJOR | cpp -include include/ap_mmn.h | sed -n '
/^2/p'`
if test "x${vmmn}" != "x%{mmn}"; then
   : Error: Upstream MMN is now ${vmmn}, packaged MMN is %{mmn}.
   : Update the mmn macro and rebuild.
   exit 1
fi

%build

cd %RPMBUILD_HTTP_DIR

# do not remove srclib, using included apr and apr-util
#rm -rf srclib/{apr,apr-util,pcre}

echo -e "\n***Building %{DISTCACHE}***\n\n"
## Not installing dc client or server init.d
/bin/cp %{_baseline_workspace}/foss/distcache/%{DISTCACHE}-21.src.rpm .
rpm2cpio %{DISTCACHE}-21.src.rpm | cpio -id
tar xjf %{DISTCACHE}.tar.bz2 
cp -v *patch* %{DISTCACHE}
pushd .
cd %{DISTCACHE}

#apply patch files
for patchFile in *patch*
do
    patch -p1 -b -i $patchFile
done

./configure --prefix=/awips2/httpd_pypies/usr/distcache --enable-shared --disable-static 
make %{?_smp_mflags} 

if [ $? -ne 0 ]; then
   exit 1
fi

# Temp install for httpd
make DESTDIR=%RPMBUILD_PYPIES_DIR install
if [ $? -ne 0 ]; then
   exit 1
fi

popd

echo -e "\n***Building %{HTTP_PACKAGE_NAME}***\n\n"
./configure \
        --prefix=/awips2/httpd_pypies%{_sysconfdir}/httpd \
        --exec-prefix=/awips2/httpd_pypies%{_prefix} \
        --bindir=/awips2/httpd_pypies%{_bindir} \
        --sbindir=/awips2/httpd_pypies%{_sbindir} \
        --mandir=/awips2/httpd_pypies%{_mandir} \
        --libdir=/awips2/httpd_pypies%{_libdir} \
        --sysconfdir=/awips2/httpd_pypies%{_sysconfdir}/httpd/conf \
        --includedir=/awips2/httpd_pypies%{_includedir}/httpd \
        --libexecdir=/awips2/httpd_pypies%{_libdir}/httpd/modules \
        --datadir=/awips2/httpd_pypies%{contentdir} \
        --with-installbuilddir=/awips2/httpd_pypies%{_libdir}/httpd/build \
        --with-distcache=%RPMBUILD_PYPIES_DIR/awips2/httpd_pypies/usr/distcache \
        --enable-suexec --with-suexec \
        --with-suexec-caller=%{suexec_caller} \
        --with-suexec-docroot=/awips2/httpd_pypies%{contentdir} \
        --with-suexec-logfile=/awips2/httpd_pypies%{_localstatedir}/log/httpd/suexec.log \
        --with-suexec-bin=/awips2/httpd_pypies%{_sbindir}/suexec \
        --with-suexec-uidmin=500 --with-suexec-gidmin=100 \
        --with-included-apr \
        --with-ldap \
        --with-crypto \
        --enable-pie \
        --with-pcre \
        --enable-mods-shared=all \
        --enable-mpms-shared=all \
        --enable-ssl \
        --with-ssl \
        --enable-socache-dc \
        --enable-bucketeer \
        --enable-case-filter \
        --enable-case-filter-in \
        --enable-layout=RPM \
        --disable-imagemap \
        --enable-mods-shared=all \
        --enable-ssl \
        --with-ssl \
        --enable-proxy \
        --enable-cache \
        --enable-disk-cache \
        --enable-ldap \
        --enable-authnz-ldap \
        --enable-cgid \
        --enable-authn-anon \
        --enable-authn-alias \
        --enable-session-crypto \
        $*

make %{?_smp_mflags} 
if [ $? -ne 0 ]; then
   exit 1
fi

# Temp install for mod wsgi
make DESTDIR=%RPMBUILD_PYPIES_DIR install
if [ $? -ne 0 ]; then
   exit 1
fi

###########
#BEGIN MOD WSGI
###########

# build mod_wsgi.so
/bin/cp %{_baseline_workspace}/foss/mod_wsgi/mod_wsgi-%{MOD_WSGI_VERSION}.tar.gz \
   %{_topdir}/BUILD
if [ $? -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null
cd %{_topdir}/BUILD
if [ -d mod_wsgi-%{MOD_WSGI_VERSION} ]; then
   /bin/rm -rf mod_wsgi-%{MOD_WSGI_VERSION}
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi
/bin/tar -xvf mod_wsgi-%{MOD_WSGI_VERSION}.tar.gz
if [ $? -ne 0 ]; then
   exit 1
fi

cd mod_wsgi-%{MOD_WSGI_VERSION}
export CPPFLAGS="-I/awips2/python/include/python2.7"
export LDFLAGS="-L/awips2/python/lib"

echo -e "\n***Building mod_wsgi-%{MOD_WSGI_VERSION}***\n\n"

#copy apxs files locally
cp -v %RPMBUILD_PYPIES_DIR/awips2/httpd_pypies/usr/bin/apxs .

if [ $? -ne 0 ]; then
   exit 1
fi

cp -v %RPMBUILD_PYPIES_DIR/awips2/httpd_pypies/usr/lib64/httpd/build/config_vars.mk .

if [ $? -ne 0 ]; then
   exit 1
fi

cp -v %RPMBUILD_PYPIES_DIR/awips2/httpd_pypies/usr/bin/apr-1-config .

if [ $? -ne 0 ]; then
   exit 1
fi

#change apxs to reference local dir
sed -i "s#builddir = .*#builddir = '.';#g" apxs

if [ $? -ne 0 ]; then
   exit 1
fi

#change config_vars to reference build root
sed -i 's#/awips2/#'%RPMBUILD_PYPIES_DIR'/awips2/#g' config_vars.mk

if [ $? -ne 0 ]; then
   exit 1
fi

#change APR_CONFIG to reference local dir
sed -i 's#APR_CONFIG.*#APR_CONFIG=./apr-1-config#g' config_vars.mk

if [ $? -ne 0 ]; then
   exit 1
fi

#change apr-1-config to reference build root
sed -i 's#/awips2/#'%RPMBUILD_PYPIES_DIR'/awips2/#g' apr-1-config

if [ $? -ne 0 ]; then
   exit 1
fi

LD_PRELOAD=%RPMBUILD_PYPIES_DIR/awips2/httpd_pypies/usr/lib64/libapr-1.so:%RPMBUILD_PYPIES_DIR/awips2/httpd_pypies/usr/lib64/libaprutil-1.so.0 \
./configure --with-python=/awips2/python/bin/python --with-apxs=./apxs

if [ $? -ne 0 ]; then
   exit 1
fi

make %{?_smp_mflags} 
if [ $? -ne 0 ]; then
   exit 1
fi

unset CPPFLAGS
unset LDFLAGS
popd > /dev/null

##########
#END MOD WSGI
##########


%install
cd  %RPMBUILD_HTTP_DIR

rm -rf $RPM_BUILD_ROOT

cd %{DISTCACHE}
make DESTDIR=$RPM_BUILD_ROOT install
cd ..
make DESTDIR=$RPM_BUILD_ROOT install

# for holding mod_dav lock database
mkdir -p $RPM_BUILD_ROOT/awips2/httpd_pypies%{_localstatedir}/lib/dav

# create a prototype session cache
mkdir -p $RPM_BUILD_ROOT/awips2/httpd_pypies%{_localstatedir}/cache/mod_ssl
touch $RPM_BUILD_ROOT/awips2/httpd_pypies%{_localstatedir}/cache/mod_ssl/scache.{dir,pag,sem}

# Make the MMN accessible to module packages
echo %{mmn} > $RPM_BUILD_ROOT/awips2/httpd_pypies%{_includedir}/httpd/.mmn

# Set up /var directories
mkdir -p $RPM_BUILD_ROOT/awips2/httpd_pypies%{_localstatedir}/log/httpd
mkdir -p $RPM_BUILD_ROOT/awips2/httpd_pypies%{_localstatedir}/cache/httpd/cache-root

# symlinks for /etc/httpd
ln -s ../..%{_localstatedir}/log/httpd $RPM_BUILD_ROOT/awips2/httpd_pypies/etc/httpd/logs
ln -s ../..%{_localstatedir}/run $RPM_BUILD_ROOT/awips2/httpd_pypies/etc/httpd/run
ln -s ../..%{_libdir}/httpd/modules $RPM_BUILD_ROOT/awips2/httpd_pypies/etc/httpd/modules
mkdir -p $RPM_BUILD_ROOT/awips2/httpd_pypies%{_sysconfdir}/httpd/conf.d

# install SYSV init stuff
mkdir -p $RPM_BUILD_ROOT/awips2/httpd_pypies/etc/rc.d/init.d
mkdir -p $RPM_BUILD_ROOT/etc/rc.d/init.d

install -m755 %{_baseline_workspace}/installers/RPMs/httpd-pypies/configuration/etc/init.d/httpd-pypies \
    $RPM_BUILD_ROOT/awips2/httpd_pypies/etc/rc.d/init.d/httpd

install -m755 %{_baseline_workspace}/installers/RPMs/httpd-pypies/configuration/etc/init.d/httpd-pypies \
        $RPM_BUILD_ROOT/etc/rc.d/init.d/httpd-pypies

install -m755 ./build/rpm/htcacheclean.init \
        $RPM_BUILD_ROOT/awips2/httpd_pypies/etc/rc.d/init.d/htcacheclean

install -m755 ./build/rpm/htcacheclean.init \
        $RPM_BUILD_ROOT/etc/rc.d/init.d/htcacheclean-pypies

# install cron job
mkdir -p ${RPM_BUILD_ROOT}/etc/cron.daily
install -m755 %{_baseline_workspace}/installers/RPMs/httpd-pypies/configuration/etc/cron.daily/pypiesLogCleanup.sh \
   ${RPM_BUILD_ROOT}/etc/cron.daily

# fix man page paths
sed -e "s|/usr/local/apache2/conf/httpd.conf|/awips2/httpd_pypies/etc/httpd/conf/httpd.conf|" \
    -e "s|/usr/local/apache2/conf/mime.types|/etc/mime.types|" \
    -e "s|/usr/local/apache2/conf/magic|/etc/httpd/conf/magic|" \
    -e "s|/usr/local/apache2/logs/error_log|/var/log/httpd/error_log|" \
    -e "s|/usr/local/apache2/logs/access_log|/var/log/httpd/access_log|" \
    -e "s|/usr/local/apache2/logs/httpd.pid|/var/run/httpd/httpd.pid|" \
    -e "s|/usr/local/apache2|/etc/httpd|" < docs/man/httpd.8 \
  > $RPM_BUILD_ROOT/awips2/httpd_pypies%{_mandir}/man8/httpd.8


# install log rotation stuff
mkdir -p $RPM_BUILD_ROOT/etc/logrotate.d
install -m644 ./build/rpm/httpd.logrotate \
    $RPM_BUILD_ROOT/etc/logrotate.d/httpd_pypies

# Remove unpackaged files
rm -rf $RPM_BUILD_ROOT/awips2/httpd_pypies%{_libdir}/httpd/modules/*.exp \
       $RPM_BUILD_ROOT/awips2/httpd_pypies%{contentdir}/cgi-bin/*

# Make suexec a+rw so it can be stripped.  %%files lists real permissions
chmod 755 $RPM_BUILD_ROOT/awips2/httpd_pypies%{_sbindir}/suexec

###########
#BEGIN MOD WSGI  
###########

pushd . > /dev/null
cd %{_topdir}/BUILD/mod_wsgi-%{MOD_WSGI_VERSION}

# Install the module required by pypies.
install -m755 .libs/mod_wsgi.so \
    ${RPM_BUILD_ROOT}/awips2/httpd_pypies/etc/httpd/modules

cd ../
/bin/rm -f mod_wsgi-%{MOD_WSGI_VERSION}.tar.gz
if [ $? -ne 0 ]; then
   exit 1
fi
/bin/rm -rf mod_wsgi-%{MOD_WSGI_VERSION}
if [ $? -ne 0 ]; then
   exit 1
fi
popd > /dev/null

##########
#END MOD WSGI
##########

# Install the pypies configuration.
install -m644 %{_baseline_workspace}/installers/RPMs/httpd-pypies/configuration/apache/pypies.conf \
    ${RPM_BUILD_ROOT}/awips2/httpd_pypies/etc/httpd/conf.d
mkdir -p ${RPM_BUILD_ROOT}/awips2/httpd_pypies/var/www/wsgi
install -m644 %{_baseline_workspace}/installers/RPMs/httpd-pypies/configuration/apache/pypies.wsgi \
    ${RPM_BUILD_ROOT}/awips2/httpd_pypies/var/www/wsgi

# Install & Override the httpd configuration.
install -m644 %{_baseline_workspace}/installers/RPMs/httpd-pypies/configuration/conf/httpd.conf \
    ${RPM_BUILD_ROOT}/awips2/httpd_pypies/etc/httpd/conf

# Install docs
mkdir -p ${RPM_BUILD_ROOT}/awips2/httpd_pypies/usr/share/doc/awips2-httpd-pypies-%{version}
cp -pr ABOUT_APACHE README CHANGES LICENSE VERSIONING NOTICE ${RPM_BUILD_ROOT}/awips2/httpd_pypies/usr/share/doc/awips2-httpd-pypies-%{version}

# Create subsys
mkdir -p ${RPM_BUILD_ROOT}/awips2/httpd_pypies/var/lock/subsys

%pre
# Add the "apache" user
/usr/sbin/useradd -c "Apache" -u 48 \
    -s /sbin/nologin -r -d %{contentdir} apache 2> /dev/null || :

%post
# Register the httpd service
/sbin/chkconfig --add httpd-pypies
/sbin/chkconfig --add htcacheclean-pypies

%preun
if [ $1 = 0 ]; then
    /sbin/service httpd-pypies stop > /dev/null 2>&1
    /sbin/service htcacheclean-pypies stop > /dev/null 2>&1
    /sbin/chkconfig --del httpd-pypies
    /sbin/chkconfig --del htcacheclean-pypies
fi

%post -n %name-tools
chown -R awips:fxalpha /awips2/httpd_pypies

%check
# Check the built modules are all PIC
if readelf -d $RPM_BUILD_ROOT/awips2/httpd_pypies%{_libdir}/httpd/modules/*.so | grep TEXTREL; then
   : modules contain non-relocatable code
   exit 1
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,awips,fxalpha)
%dir /awips2/httpd_pypies
/awips2/httpd_pypies/*
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/httpd.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/magic
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/mime.types
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/extra/httpd-autoindex.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/extra/httpd-dav.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/extra/httpd-default.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/extra/httpd-info.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/extra/httpd-languages.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/extra/httpd-manual.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/extra/httpd-mpm.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/extra/httpd-multilang-errordoc.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/extra/httpd-userdir.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/extra/httpd-vhosts.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/extra/proxy-html.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/original/extra/httpd-autoindex.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/original/extra/httpd-dav.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/original/extra/httpd-default.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/original/extra/httpd-info.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/original/extra/httpd-languages.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/original/extra/httpd-manual.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/original/extra/httpd-mpm.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/original/extra/httpd-multilang-errordoc.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/original/extra/httpd-userdir.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/original/extra/httpd-vhosts.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/original/extra/proxy-html.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/original/httpd.conf
%config %{_sysconfdir}/logrotate.d/httpd_pypies
%config /awips2/httpd_pypies%{_sysconfdir}/rc.d/init.d/httpd
%config /awips2/httpd_pypies%{_sysconfdir}/rc.d/init.d/htcacheclean
%{_sysconfdir}/cron.daily/pypiesLogCleanup.sh
/etc/rc.d/init.d/htcacheclean-pypies
/etc/rc.d/init.d/httpd-pypies
%attr(0700,awips,fxalpha) %dir /awips2/httpd_pypies/var/lock/subsys
%attr(4510,awips,fxalpha) /awips2/httpd_pypies%{_sbindir}/suexec
%config(noreplace) /awips2/httpd_pypies%{contentdir}/error/*.var
%config(noreplace) /awips2/httpd_pypies%{contentdir}/error/include/*.html
%attr(0755,awips,fxalpha) %dir /awips2/httpd_pypies/%{_localstatedir}/log/httpd
%attr(0700,awips,fxalpha) %dir /awips2/httpd_pypies%{_localstatedir}/lib/dav
%attr(0700,awips,fxalpha) %dir /awips2/httpd_pypies%{_localstatedir}/cache/httpd/cache-root

%files -n %name-tools
%defattr(-,awips,fxalpha)
/awips2/httpd_pypies%{_bindir}/ab
/awips2/httpd_pypies%{_bindir}/htdbm
/awips2/httpd_pypies%{_bindir}/htdigest
/awips2/httpd_pypies%{_bindir}/htpasswd
/awips2/httpd_pypies%{_bindir}/logresolve
/awips2/httpd_pypies%{_bindir}/httxt2dbm
/awips2/httpd_pypies%{_sbindir}/rotatelogs
/awips2/httpd_pypies%{_mandir}/man1/htdbm.1*
/awips2/httpd_pypies%{_mandir}/man1/htdigest.1*
/awips2/httpd_pypies%{_mandir}/man1/htpasswd.1*
/awips2/httpd_pypies%{_mandir}/man1/httxt2dbm.1*
/awips2/httpd_pypies%{_mandir}/man1/ab.1*
/awips2/httpd_pypies%{_mandir}/man1/logresolve.1*
/awips2/httpd_pypies%{_mandir}/man8/rotatelogs.8*
