%define contentdir /var/www
%define suexec_caller apache
%define mmn 20120211

%define HTTP_FOSS_DIR "%{_baseline_workspace}/foss/%{HTTP_PACKAGE_NAME}/packaged/"
%define HTTP_PACKAGE_NAME "httpd-%{version}"
%define HTTP_SOURCE_TAR "%{HTTP_PACKAGE_NAME}.tar.gz"
%define HTTP_DEPS_TAR "%{HTTP_PACKAGE_NAME}-deps.tar.gz"
%define RPMBUILD_PYPIES_DIR "%{_baseline_workspace}/rpmbuild/BUILD/httpd-pypies"
%define RPMBUILD_HTTP_DIR %RPMBUILD_PYPIES_DIR/%HTTP_PACKAGE_NAME
%define DISTCACHE distcache-1.4.5
%define MOD_WSGI_VERSION 3.5

Summary: Apache HTTP Server
Name: awips2-httpd-pypies
Version: 2.4.23
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
Requires: awips2-python-numpy, awips2-python-awips, awips2-python-werkzeug
Packager: %{_build_site}

%description
Apache is a powerful, full-featured, efficient, and freely-available
Web server. Apache is also the most popular Web server on the
Internet.

%package -n %name-devel
Group: AWIPSII
Summary: Development tools for the Apache HTTP server.
Obsoletes: secureweb-devel, apache-devel
Requires: pkgconfig, libtool
Requires: awips2-httpd-pypies = %{version}-%{release}

%description -n %name-devel
The httpd-devel package contains the APXS binary and other files
that you need to build Dynamic Shared Objects (DSOs) for the
Apache HTTP Server.

If you are installing the Apache HTTP server and you want to be
able to compile or develop additional modules for Apache, you need
to install this package.

%package -n %name-manual
Group: Documentation
Summary: Documentation for the Apache HTTP server.
Requires: awips2-httpd-pypies = :%{version}-%{release}
Obsoletes: secureweb-manual, apache-manual

%description -n %name-manual
The httpd-manual package contains the complete manual and
reference guide for the Apache HTTP server. The information can
also be found at http://httpd.apache.org/docs/.

%package -n %name-tools
Group: AWIPSII
Summary: Tools for use with the Apache HTTP Server

%description -n %name-tools
The httpd-tools package contains tools which can be used with 
the Apache HTTP Server.

%package -n %name-mod_authnz_ldap
Group: AWIPSII
Summary: LDAP modules for the Apache HTTP server
BuildRequires: openldap-devel
Requires: %name = %{version}-%{release}

%description -n %name-mod_authnz_ldap
The mod_authnz_ldap module for the Apache HTTP server provides
authentication and authorization against an LDAP server, while
mod_ldap provides an LDAP cache.

%package -n %name-mod_lua
Group: AWIPSII
Summary: Lua language module for the Apache HTTP server
BuildRequires: lua-devel
Requires: %name = %{version}-%{release}

%description -n %name-mod_lua
The mod_lua module for the Apache HTTP server allows the server to be
extended with scripts written in the Lua programming language.

%package -n %name-mod_proxy_html
Group: AWIPSII
Summary: Proxy HTML filter modules for the Apache HTTP server
Epoch: 1
BuildRequires: libxml2-devel
Requires: %name = 0:%{version}-%{release}

%description -n %name-mod_proxy_html
The mod_proxy_html module for the Apache HTTP server provides
a filter to rewrite HTML links within web content when used within
a reverse proxy environment. The mod_xml2enc module provides
enhanced charset/internationalisation support for mod_proxy_html.

%package -n %name-mod_socache_dc
Group: AWIPSII
Summary: Distcache shared object cache module for the Apache HTTP server
Requires: %name = %{version}-%{release}

%description -n %name-mod_socache_dc
The mod_socache_dc module for the Apache HTTP server allows the shared
object cache to use the distcache shared caching mechanism.

%package -n %name-mod_ssl
Group: AWIPSII
Summary: SSL/TLS module for the Apache HTTP server
Epoch: 1
BuildRequires: openssl-devel
Requires(post): openssl, /bin/cat
Requires(pre): %name
Requires: %name = 0:%{version}-%{release}

%description -n %name-mod_ssl
The mod_ssl module provides strong cryptography for the Apache Web
server via the Secure Sockets Layer (SSL) and Transport Layer
Security (TLS) protocols.

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
cp -v %HTTP_FOSS_DIR/%HTTP_DEPS_TAR .
tar xf %{HTTP_SOURCE_TAR}
tar xzf %{HTTP_DEPS_TAR}
if [ $? -ne 0 ]; then
   exit 1
fi

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
/bin/cp %{_baseline_workspace}/foss/%{DISTCACHE}/packaged/%{DISTCACHE}-21.src.rpm .
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
/bin/cp %{_baseline_workspace}/foss/mod_wsgi-%{MOD_WSGI_VERSION}/packaged/mod_wsgi-%{MOD_WSGI_VERSION}.tar.gz \
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

LD_LIBRARY_PATH=%RPMBUILD_PYPIES_DIR/awips2/httpd_pypies/usr/lib64/:/awips2/python/lib:$LD_LIBRARY_PATH \
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

ln -sf /awips2/httpd_pypies/etc/rc.d/init.d/httpd $RPM_BUILD_ROOT/etc/rc.d/init.d/httpd-pypies
install -m755 ./build/rpm/htcacheclean.init \
        $RPM_BUILD_ROOT/awips2/httpd_pypies/etc/rc.d/init.d/htcacheclean
ln -sf /awips2/httpd_pypies/etc/rc.d/init.d/htcacheclean $RPM_BUILD_ROOT/etc/rc.d/init.d/htcacheclean-pypies

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
mkdir -p ${RPM_BUILD_ROOT}/awips2/httpd_pypies/usr/share/doc/awips2-httpd-pypies-2.4.23
cp -pr ABOUT_APACHE README CHANGES LICENSE VERSIONING NOTICE ${RPM_BUILD_ROOT}/awips2/httpd_pypies/usr/share/doc/awips2-httpd-pypies-2.4.23

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

%post -n %name-mod_ssl
umask 077

if [ ! -f/awips2/httpd_pypies%{_sysconfdir}/httpd/conf/server.key ] ; then
%{_bindir}/openssl genrsa -rand /proc/apm:/proc/cpuinfo:/proc/dma:/proc/filesystems:/proc/interrupts:/proc/ioports:/proc/pci:/proc/rtc:/proc/uptime 1024 >/awips2/httpd_pypies%{_sysconfdir}/httpd/conf/server.key 2> /dev/null
fi

FQDN=`hostname`
if [ "x${FQDN}" = "x" ]; then
   FQDN=localhost.localdomain
fi

if [ ! -f/awips2/httpd_pypies%{_sysconfdir}/httpd/conf/server.crt ] ; then
cat << EOF | %{_bindir}/openssl req -new -key/awips2/httpd_pypies%{_sysconfdir}/httpd/conf/server.key -x509 -days 365 -out/awips2/httpd_pypies%{_sysconfdir}/httpd/conf/server.crt 2>/dev/null
--
SomeState
SomeCity
SomeOrganization
SomeOrganizationalUnit
${FQDN}
root@${FQDN}
EOF
fi

%check
# Check the built modules are all PIC
if readelf -d $RPM_BUILD_ROOT/awips2/httpd_pypies%{_libdir}/httpd/modules/*.so | grep TEXTREL; then
   : modules contain non-relocatable code
   exit 1
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,awips,awips)
/awips2/httpd_pypies/etc/
/awips2/httpd_pypies/etc/httpd/conf/extra/
/awips2/httpd_pypies/etc/httpd/conf/original/extra/
/awips2/httpd_pypies/etc/httpd/conf/original/
/awips2/httpd_pypies/etc/rc.d/init.d/
/awips2/httpd_pypies/usr/lib64/
/awips2/httpd_pypies/usr/sbin/
/awips2/httpd_pypies/usr/share/doc/awips2-httpd-pypies-2.4.23/
/awips2/httpd_pypies/usr/share/man/man1/
/awips2/httpd_pypies/usr/share/man/man8/
/awips2/httpd_pypies/var/cache/httpd/
/awips2/httpd_pypies/var/lib/
/awips2/httpd_pypies/var/lock/
/awips2/httpd_pypies/var/log/
/awips2/httpd_pypies/var/
/awips2/httpd_pypies/var/www/wsgi/
%dir /awips2/httpd_pypies%{_sysconfdir}/httpd
/awips2/httpd_pypies%{_sysconfdir}/httpd/modules
/awips2/httpd_pypies%{_sysconfdir}/httpd/logs
/awips2/httpd_pypies%{_sysconfdir}/httpd/run
%dir /awips2/httpd_pypies%{_sysconfdir}/httpd/conf
%dir /awips2/httpd_pypies%{_sysconfdir}/httpd/conf.d
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
/awips2/httpd_pypies%{_sbindir}/fcgistarter
/etc/rc.d/init.d/htcacheclean-pypies
/awips2/httpd_pypies%{_sbindir}/htcacheclean
/etc/rc.d/init.d/httpd-pypies
%attr(0700,awips,awips) %dir /awips2/httpd_pypies/var/lock/subsys
/awips2/httpd_pypies%{_sbindir}/httpd
/awips2/httpd_pypies%{_sbindir}/apachectl
%attr(4510,awips,awips) /awips2/httpd_pypies%{_sbindir}/suexec
%dir /awips2/httpd_pypies%{_libdir}/httpd
%dir /awips2/httpd_pypies%{_libdir}/httpd/modules
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_access_compat.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_actions.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_alias.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_allowmethods.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_asis.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_auth_basic.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_auth_digest.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_auth_form.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_authn_anon.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_authn_core.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_authn_dbd.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_authn_dbm.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_authn_file.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_authn_socache.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_authz_core.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_authz_dbd.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_authz_dbm.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_authz_groupfile.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_authz_host.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_authz_owner.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_authz_user.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_autoindex.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_bucketeer.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_buffer.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_cache_disk.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_cache_socache.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_cache.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_case_filter.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_case_filter_in.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_cgid.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_charset_lite.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_data.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_dav_fs.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_dav_lock.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_dav.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_dbd.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_deflate.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_dialup.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_dir.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_dumpio.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_echo.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_env.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_expires.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_ext_filter.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_file_cache.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_filter.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_headers.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_heartbeat.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_heartmonitor.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_include.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_info.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_lbmethod_bybusyness.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_lbmethod_byrequests.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_lbmethod_bytraffic.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_lbmethod_heartbeat.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_log_config.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_log_debug.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_log_forensic.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_logio.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_macro.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_mime_magic.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_mime.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_mpm_event.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_mpm_prefork.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_mpm_worker.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_negotiation.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_proxy_ajp.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_proxy_balancer.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_proxy_connect.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_proxy_express.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_proxy_fcgi.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_proxy_ftp.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_proxy_http.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_proxy_scgi.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_proxy_wstunnel.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_proxy.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_ratelimit.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_reflector.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_remoteip.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_reqtimeout.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_request.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_rewrite.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_sed.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_session_cookie.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_session_crypto.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_session_dbd.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_session.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_setenvif.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_slotmem_plain.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_slotmem_shm.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_socache_dbm.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_socache_memcache.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_socache_shmcb.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_speling.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_status.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_substitute.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_suexec.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_unique_id.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_unixd.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_userdir.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_usertrack.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_version.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_vhost_alias.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_watchdog.so
/awips2/httpd_pypies/etc/httpd/conf.d/pypies.conf
/awips2/httpd_pypies/usr/lib64/httpd/modules/mod_proxy_hcheck.so
/awips2/httpd_pypies/usr/lib64/httpd/modules/mod_wsgi.so
/awips2/httpd_pypies/var/www/wsgi/pypies.wsgi
/awips2/httpd_pypies/usr/share/doc/awips2-httpd-pypies-2.4.23/ABOUT_APACHE
/awips2/httpd_pypies/usr/share/doc/awips2-httpd-pypies-2.4.23/CHANGES
/awips2/httpd_pypies/usr/share/doc/awips2-httpd-pypies-2.4.23/LICENSE
/awips2/httpd_pypies/usr/share/doc/awips2-httpd-pypies-2.4.23/NOTICE
/awips2/httpd_pypies/usr/share/doc/awips2-httpd-pypies-2.4.23/README
/awips2/httpd_pypies/usr/share/doc/awips2-httpd-pypies-2.4.23/VERSIONING
%dir /awips2/httpd_pypies%{contentdir}
%dir /awips2/httpd_pypies%{contentdir}/cgi-bin
%dir /awips2/httpd_pypies%{contentdir}/html
%dir /awips2/httpd_pypies%{contentdir}/icons
%dir /awips2/httpd_pypies%{contentdir}/error
%dir /awips2/httpd_pypies%{contentdir}/error/include
/awips2/httpd_pypies%{contentdir}/icons/*
/awips2/httpd_pypies%{contentdir}/error/README
/awips2/httpd_pypies%{contentdir}/html/index.html
%config(noreplace) /awips2/httpd_pypies%{contentdir}/error/*.var
%config(noreplace) /awips2/httpd_pypies%{contentdir}/error/include/*.html
%attr(0755,awips,awips) %dir /awips2/httpd_pypies/%{_localstatedir}/log/httpd
%attr(0700,awips,awips) %dir /awips2/httpd_pypies%{_localstatedir}/lib/dav
%attr(0700,awips,awips) %dir /awips2/httpd_pypies%{_localstatedir}/cache/httpd/cache-root
/awips2/httpd_pypies%{_mandir}/man1/*
/awips2/httpd_pypies%{_mandir}/man8/suexec*
/awips2/httpd_pypies%{_mandir}/man8/apachectl.8*
/awips2/httpd_pypies%{_mandir}/man8/httpd.8*
/awips2/httpd_pypies%{_mandir}/man8/htcacheclean.8*
/awips2/httpd_pypies%{_mandir}/man8/fcgistarter.8*

%files -n %name-manual
%defattr(-,awips,awips)
/awips2/httpd_pypies/var/www/error/
/awips2/httpd_pypies/var/www/
/awips2/httpd_pypies%{contentdir}/manual
/awips2/httpd_pypies%{contentdir}/error/README

%files -n %name-tools
%defattr(-,awips,awips)
/awips2/httpd_pypies%{_bindir}/ab
/awips2/httpd_pypies%{_bindir}/htdbm
/awips2/httpd_pypies%{_bindir}/htdigest
/awips2/httpd_pypies%{_bindir}/htpasswd
/awips2/httpd_pypies%{_bindir}/logresolve
/awips2/httpd_pypies%{_bindir}/httxt2dbm
/awips2/httpd_pypies%{_sbindir}/rotatelogs
/awips2/httpd_pypies/usr/distcache*
/awips2/httpd_pypies/usr/include/httpd*
/awips2/httpd_pypies/usr/share
/awips2/httpd_pypies/usr/share/doc
/awips2/httpd_pypies/usr/share/man
/awips2/httpd_pypies%{_mandir}/man1/htdbm.1*
/awips2/httpd_pypies%{_mandir}/man1/htdigest.1*
/awips2/httpd_pypies%{_mandir}/man1/htpasswd.1*
/awips2/httpd_pypies%{_mandir}/man1/httxt2dbm.1*
/awips2/httpd_pypies%{_mandir}/man1/ab.1*
/awips2/httpd_pypies%{_mandir}/man1/logresolve.1*
/awips2/httpd_pypies%{_mandir}/man8/rotatelogs.8*

%files -n %name-mod_authnz_ldap
%defattr(-,awips,awips)
/awips2/httpd_pypies/usr/lib64/httpd/modules/
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_ldap.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_authnz_ldap.so

%files -n %name-mod_lua
%defattr(-,awips,awips)
/awips2/httpd_pypies/usr/lib64/httpd/modules/
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_lua.so

%files -n %name-mod_proxy_html
%defattr(-,awips,awips)
/awips2/httpd_pypies/usr/lib64/httpd/modules/
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_proxy_html.so
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_xml2enc.so

%files -n %name-mod_socache_dc
%defattr(-,awips,awips)
/awips2/httpd_pypies/usr/lib64/httpd/modules/
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_socache_dc.so

%files -n %name-mod_ssl
%defattr(-,awips,awips)
/awips2/httpd_pypies/etc/httpd/conf/extra/
/awips2/httpd_pypies/etc/httpd/conf/original/extra/
/awips2/httpd_pypies/usr/lib64/httpd/modules/
/awips2/httpd_pypies/var/cache/
/awips2/httpd_pypies%{_libdir}/httpd/modules/mod_ssl.so
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/original/extra/httpd-ssl.conf
%config(noreplace) /awips2/httpd_pypies%{_sysconfdir}/httpd/conf/extra/httpd-ssl.conf
%attr(0700,awips,awips) %dir /awips2/httpd_pypies%{_localstatedir}/cache/mod_ssl
%attr(0600,awips,awips) %ghost /awips2/httpd_pypies%{_localstatedir}/cache/mod_ssl/scache.dir
%attr(0600,awips,awips) %ghost /awips2/httpd_pypies%{_localstatedir}/cache/mod_ssl/scache.pag
%attr(0600,awips,awips) %ghost /awips2/httpd_pypies%{_localstatedir}/cache/mod_ssl/scache.sem

%files -n %name-devel
%defattr(-,awips,awips)
/awips2/httpd_pypies/usr/bin/
/awips2/httpd_pypies/usr/include/
/awips2/httpd_pypies/usr/lib64/httpd/
/awips2/httpd_pypies/usr/sbin/
/awips2/httpd_pypies/usr/share/man/man1/
/awips2/httpd_pypies%{_includedir}/httpd
/awips2/httpd_pypies%{_bindir}/apxs
/awips2/httpd_pypies%{_sbindir}/checkgid
/awips2/httpd_pypies%{_bindir}/dbmmanage
/awips2/httpd_pypies%{_sbindir}/envvars*
/awips2/httpd_pypies%{_mandir}/man1/dbmmanage.1*
/awips2/httpd_pypies%{_mandir}/man1/apxs.1*
%dir /awips2/httpd_pypies%{_libdir}/httpd/build
/awips2/httpd_pypies%{_libdir}/httpd/build/*.mk
/awips2/httpd_pypies%{_libdir}/httpd/build/instdso.sh
/awips2/httpd_pypies%{_libdir}/httpd/build/config.nice
/awips2/httpd_pypies%{_libdir}/httpd/build/mkdir.sh
