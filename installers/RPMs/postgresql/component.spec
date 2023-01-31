%define _build_arch %(uname -i)
%define _postgresql_version 11.14
%define _proj_version 6.3.2
%define _gdal_version 3.2.0
%define _geos_version 3.5.2
%define _postgis_version 2.4.9
%define _postgres_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _postgres_src_loc %{_baseline_workspace}/foss/postgresql-%{_postgresql_version}
%define _postgres_script_loc %{_baseline_workspace}/installers/RPMs/postgresql/scripts

#
# AWIPS II PostgreSQL Spec File
#

Name: awips2-postgresql
Summary: AWIPS II PostgreSQL Distribution
Version: %{_postgresql_version}
Release: %{_component_version}.%{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
BuildRequires: gcc-c++
BuildRequires: libxml2-devel
BuildRequires: make
BuildRequires: openssl-devel >= 1.0.1e
BuildRequires: readline-devel
Requires: openssl >= 1.0.1e
Requires: libjpeg-turbo
BuildRequires: readline-devel
Requires: awips2-netcdf
Requires: awips2-python
Provides: awips2-postgresql

%description
AWIPS II PostgreSQL Distribution - Contains the AWIPS II PostgreSQL Distribution.
This is just the postgresql application. There is a separate rpm that will initialize
and populate the AWIPS II databases.

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
/bin/mkdir -p %{_build_root} || exit 1

if [ -d %{_postgres_build_loc} ]; then
   rm -rf %{_postgres_build_loc}
fi

mkdir -p %{_postgres_build_loc} || exit 1
mkdir -p %{_postgres_build_loc}/awips2/postgresql || exit 1

SRC_DIR="%{_postgres_src_loc}/packaged"
POSTGRESQL_TAR_FILE="postgresql-%{_postgresql_version}.tar.gz"

# Copy our source tar file to the build directory.
cp ${SRC_DIR}/${POSTGRESQL_TAR_FILE} %{_postgres_build_loc}

# Untar the postgresql source
cd %{_postgres_build_loc}

tar -xvf ${POSTGRESQL_TAR_FILE}

%build
cd %{_postgres_build_loc}/postgresql-%{_postgresql_version}

LDFLAGS='-Wl,-rpath,/awips2/postgresql/lib,-rpath,/awips2/psql/lib,-rpath,/awips2/python/lib,-rpath,/awips2/netcdf/lib' ./configure \
   --prefix=%{_postgres_build_loc}/awips2/postgresql \
   --with-openssl \
   --with-libxml || exit 1

make clean || exit 1

make %{?_smp_mflags} || exit 1

cd %{_postgres_build_loc}/postgresql-%{_postgresql_version}/contrib/pg_freespacemap
make || exit 1

cd %{_postgres_build_loc}/postgresql-%{_postgresql_version}/contrib/xml2
make %{?_smp_mflags} || exit 1

# Make Postgresql docs
cd %{_postgres_build_loc}/postgresql-%{_postgresql_version}/doc
make || exit 1

%install
# Copies the standard %{_build_vendor} licenses into a license directory for the
# current component.
function copyLegal()
{
   # $1 == Component Build Root
   
   COMPONENT_BUILD_DIR=${1}
   
   mkdir -p ${RPM_BUILD_ROOT}/${COMPONENT_BUILD_DIR}/licenses
   
   # Create a Tar file with our FOSS licenses.
   tar -cjf %{_baseline_workspace}/rpms/legal/FOSS_licenses.tar \
      %{_baseline_workspace}/rpms/legal/FOSS_licenses/
   
   cp "%{_baseline_workspace}/rpms/legal/Master_Rights_File.pdf" \
      ${RPM_BUILD_ROOT}/${COMPONENT_BUILD_DIR}/licenses
   cp %{_baseline_workspace}/rpms/legal/FOSS_licenses.tar \
      ${RPM_BUILD_ROOT}/${COMPONENT_BUILD_DIR}/licenses
      
   rm -f %{_baseline_workspace}/rpms/legal/FOSS_licenses.tar    
}

mkdir -p %{_build_root}/awips2/postgresql
mkdir -p %{_build_root}/awips2/psql

cd %{_postgres_build_loc}/postgresql-%{_postgresql_version}

make install || exit 1

# Install Postgresql docs
cd %{_postgres_build_loc}/postgresql-%{_postgresql_version}/doc
make install || exit 1

cd %{_postgres_build_loc}/postgresql-%{_postgresql_version}/contrib/xml2

make install || exit 1

# relocate the psql executable
mkdir -p %{_build_root}/awips2/psql/bin
mv -v %{_postgres_build_loc}/awips2/postgresql/bin/psql \
   %{_build_root}/awips2/psql/bin/psql || exit 1

# relocate the psql man page
mkdir -p %{_build_root}/awips2/psql/share/man/man1
mv -v %{_postgres_build_loc}/awips2/postgresql/share/man/man1/psql.1 \
   %{_build_root}/awips2/psql/share/man/man1/ || exit 1

# remove the rest of the postgresql man pages
rm -rf %{_postgres_build_loc}/awips2/postgresql/share/man
# duplicate libpq; eventually, we should just have PostgreSQL
# reference the libpq in /awips2/psq/lib
mkdir -p %{_build_root}/awips2/psql/lib
cp -Pv %{_postgres_build_loc}/awips2/postgresql/lib/libpq.so* \
   %{_build_root}/awips2/psql/lib || exit 1


src_dir="%{_postgres_src_loc}/packaged"
sqlite_src="sqlite-autoconf-3340000"
proj_src="proj-%{_proj_version}"
gdal_src="gdal-%{_gdal_version}"
geos_src="geos-%{_geos_version}"
postgis_src="postgis-%{_postgis_version}"

cp "%{_baseline_workspace}/foss/${geos_src}/packaged/${geos_src}.tar.bz2" %{_postgres_build_loc}
cp "${src_dir}/${sqlite_src}.tar.gz" %{_postgres_build_loc}
cp "${src_dir}/${proj_src}.tar.gz" %{_postgres_build_loc}
cp "${src_dir}/${gdal_src}.tar.gz" %{_postgres_build_loc}
cp "${src_dir}/${postgis_src}.tar.gz" %{_postgres_build_loc}

cd %{_postgres_build_loc}

tar -xf "${geos_src}.tar.bz2" || exit 1
tar -xf "${sqlite_src}.tar.gz" || exit 1
tar -xf "${proj_src}.tar.gz" || exit 1
tar -xf "${gdal_src}.tar.gz" || exit 1
tar -xf "${postgis_src}.tar.gz" || exit 1

# TODO: Sometimes at runtime, postgres loads the version of GEOS installed with
# Python instead of this one, probably need to fix the Postgres library search
# path somehow.

cd "${geos_src}"
LDFLAGS='-Wl,-rpath,/awips2/postgresql/lib,-rpath,/awips2/psql/lib,-rpath,/awips2/python/lib,-rpath,/awips2/netcdf/lib' ./configure \
   --prefix=%{_postgres_build_loc}/awips2/postgresql || exit 1
make %{?_smp_mflags} || exit 1
make install || exit 1

cd "../${sqlite_src}"
./configure --prefix=%{_postgres_build_loc}/awips2/postgresql
make || exit 1
make install || exit 1

cd "../${proj_src}"
SQLITE3_CFLAGS="-I/%{_postgres_build_loc}/awips2/postgresql/include" \
SQLITE3_LIBS="-L%{_postgres_build_loc}/awips2/postgresql/lib -lsqlite3" \
LDFLAGS='-Wl,-rpath,/awips2/postgresql/lib,-rpath,/awips2/psql/lib,-rpath,/awips2/python/lib,-rpath,/awips2/netcdf/lib' ./configure \
   --prefix=%{_postgres_build_loc}/awips2/postgresql \
   --without-jni || exit 1
make %{?_smp_mflags} || exit 1
make install || exit 1

cd "../${gdal_src}"
CFLAGS=-I/awips2/netcdf/include LDFLAGS='-L/awips2/netcdf/lib -Wl,-rpath,/awips2/postgresql/lib,-rpath,/awips2/psql/lib,-rpath,/awips2/python/lib,-rpath,/awips2/netcdf/lib' ./configure \
   --prefix=%{_postgres_build_loc}/awips2/postgresql \
   --with-sqlite3="%{_postgres_build_loc}/awips2/postgresql" \
   --with-proj="%{_postgres_build_loc}/awips2/postgresql" \
   --with-expat-lib=%{_usr}/%{_lib} \
   --with-netcdf=/awips2/netcdf || exit 1
make %{?_smp_mflags} || exit 1
make install || exit 1

cd "../${postgis_src}"
postgres_root=%{_postgres_build_loc}/awips2/postgresql
postgres_bin=${postgres_root}/bin
LDFLAGS="-L/awips2/netcdf/lib -Wl,-rpath,/awips2/postgresql/lib,-rpath,/awips2/psql/lib,-rpath,/awips2/python/lib,-rpath,/awips2/netcdf/lib" ./configure \
    --with-pgconfig=${postgres_bin}/pg_config \
    --with-geosconfig=${postgres_bin}/geos-config \
    --with-projdir=${postgres_root} \
    --with-gdalconfig=${postgres_bin}/gdal-config \
    --prefix=%{_postgres_build_loc}/awips2/postgresql || exit 1

# disable doc since it attempts to download files from
# the internet
echo "#Do Nothing" > doc/Makefile.in
echo "docs:" > doc/Makefile
echo "" >> doc/Makefile
echo "docs-install:" >> doc/Makefile
echo "" >> doc/Makefile
echo "docs-uninstall:" >> doc/Makefile
echo "" >> doc/Makefile
echo "comments-install:" >> doc/Makefile
echo "" >> doc/Makefile
echo "comments-uninstall:" >> doc/Makefile
echo "" >> doc/Makefile
echo "clean:" >> doc/Makefile
echo "" >> doc/Makefile
echo "all:" >> doc/Makefile
echo "" >> doc/Makefile
echo "install:" >> doc/Makefile
echo "" >> doc/Makefile
make
# run make twice - the first time may fail due to doc
make || exit 1
make install || exit 1
/bin/cp -Rf %{_postgres_build_loc}/awips2/postgresql/* %{_build_root}/awips2/postgresql || exit 1

# Copy The Startup Script
cp -r %{_postgres_script_loc}/start_postgres.sh ${RPM_BUILD_ROOT}/awips2/postgresql/bin

copyLegal "awips2/postgresql"

mkdir -p %{_build_root}/etc/profile.d
mkdir -p %{_build_root}/etc/init.d

PROFILE_D_DIR="%{_postgres_script_loc}/profile.d"
cp ${PROFILE_D_DIR}/* %{_build_root}/etc/profile.d 

# Include the postgresql service script
cp %{_postgres_script_loc}/init.d/edex_postgres \
   %{_build_root}/etc/init.d

%post
# Register and turn on the edex_postgres service
/sbin/chkconfig --add edex_postgres
/sbin/chkconfig edex_postgres on --level 35

%pre
old_version=$(rpm -qi awips2-postgresql | grep 'Version\s*: ' | grep -Eo '[0-9.]+')
old_major_version=$(echo "${old_version}" | cut -d'.' -f1)
new_major_version=$(echo "${_postgresql_version}" | cut -d'.' -f1)
if [[ "${old_version}" != "" &&
      "${old_major_version}" != "${new_major_version}" ]]; then
    old_version_loc="/awips2/postgresql-${old_version}"
    if [[ -d "${old_version_loc}" ]]; then
        old_version_found=$("${old_version_loc}/bin/postgres" --version | cut -d' ' -f3)
        if [[ "${old_version_found}" != "${old_version}" ]]; then
            echo "ERROR: ${old_version_loc} exists but does not contain PostgreSQL ${old_version}"
            echo "This package must save the old PostgreSQL install to ${old_version_loc}"
            echo "but cannot do it because something already exists at that path."
            exit 1
        fi
    fi
    cp -a /awips2/postgresql "/awips2/postgresql-${old_version}" || exit 1
fi

%preun
if [ "${1}" = "1" ]; then
   exit 0
fi
if [ -f /etc/init.d/edex_postgres ]; then
   /sbin/service edex_postgres stop > /dev/null 2>&1
   /sbin/chkconfig --del edex_postgres
fi

%clean
rm -rf ${RPM_BUILD_ROOT}
rm -rf %{_postgres_build_loc}

%package -n awips2-psql

Summary: AWIPS II PSQL Distribution
Group: AWIPSII

provides: awips2-psql

%description -n awips2-psql
AWIPS II PSQL Distribution - Contains the AWIPS II PSQL Distribution.
This is just the postgresql application. There is a separate rpm that will initialize
and populate the AWIPS II databases.

%files
%defattr(644,awips,fxalpha,755)
%attr(755,root,root) /etc/profile.d/awips2Postgres.csh
%attr(755,root,root) /etc/profile.d/awips2Postgres.sh
%attr(744,root,root) /etc/init.d/edex_postgres
%dir /awips2/postgresql
%dir /awips2/postgresql/include
/awips2/postgresql/include/*
%dir /awips2/postgresql/lib
/awips2/postgresql/lib/*
%docdir /awips2/postgresql/licenses
%dir /awips2/postgresql/licenses
/awips2/postgresql/licenses/*
%dir /awips2/postgresql/share
/awips2/postgresql/share/*

%defattr(755,awips,fxalpha,755)
%dir /awips2/postgresql/bin
/awips2/postgresql/bin/*

%files -n awips2-psql
%defattr(755,awips,fxalpha,755)
%attr(755,root,root) /etc/profile.d/awips2PSQL.csh
%attr(755,root,root) /etc/profile.d/awips2PSQL.sh
%dir /awips2/psql
%dir /awips2/psql/bin
/awips2/psql/bin/*

%defattr(644,awips,fxalpha,755)
%docdir /awips2/psql/share
%dir /awips2/psql/share
/awips2/psql/share/*

%defattr(644,awips,fxalpha,755)
%dir /awips2/psql/lib
/awips2/psql/lib/*
