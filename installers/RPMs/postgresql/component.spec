Name: awips2-postgresql
Summary: AWIPS II PostgreSQL compatibility package
Version: 12
Release: %{_component_version}.%{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: noarch
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
BuildRequires: rsync
Requires: libpq >= 12
Requires: postgresql >= 12
Requires: postgresql-server >= 12
Requires: postgresql-contrib >= 12
Requires: postgresql-upgrade >= 12

BuildRequires: readline-devel

%description
Provides symlinks in /awips2/postgresql and /awips2/psql that link to
PostgreSQL executables in /usr/bin and profile.d scripts

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

mkdir --parents %{_build_root} || exit 1

%build

%install
mkdir --parents "%{_build_root}/etc/profile.d"
cp "%{_baseline_workspace}/installers/RPMs/postgresql/profile.d/"* \
    "%{_build_root}/etc/profile.d"

mkdir --parents "%{_build_root}/awips2/psql/bin"
ln --symbolic /usr/bin/psql "%{_build_root}/awips2/psql/bin/psql"

bindir="%{_build_root}/awips2/postgresql/bin"
mkdir --parents "$bindir"
ln --symbolic /usr/bin/clusterdb "$bindir/clusterdb"
ln --symbolic /usr/bin/createdb "$bindir/createdb"
ln --symbolic /usr/bin/createuser "$bindir/createuser"
ln --symbolic /usr/bin/dropdb "$bindir/dropdb"
ln --symbolic /usr/bin/dropuser "$bindir/dropuser"
ln --symbolic /usr/bin/initdb "$bindir/initdb"
ln --symbolic /usr/bin/pg_archivecleanup "$bindir/pg_archivecleanup"
ln --symbolic /usr/bin/pg_basebackup "$bindir/pg_basebackup"
ln --symbolic /usr/bin/pg_config "$bindir/pg_config"
ln --symbolic /usr/bin/pg_controldata "$bindir/pg_controldata"
ln --symbolic /usr/bin/pg_ctl "$bindir/pg_ctl"
ln --symbolic /usr/bin/pg_dump "$bindir/pg_dump"
ln --symbolic /usr/bin/pg_dumpall "$bindir/pg_dumpall"
ln --symbolic /usr/bin/pg_isready "$bindir/pg_isready"
ln --symbolic /usr/bin/pg_receivewal "$bindir/pg_receivewal"
ln --symbolic /usr/bin/pg_recvlogical "$bindir/pg_recvlogical"
ln --symbolic /usr/bin/pg_resetwal "$bindir/pg_resetwal"
ln --symbolic /usr/bin/pg_restore "$bindir/pg_restore"
ln --symbolic /usr/bin/pg_rewind "$bindir/pg_rewind"
ln --symbolic /usr/bin/pg_test_fsync "$bindir/pg_test_fsync"
ln --symbolic /usr/bin/pg_test_timing "$bindir/pg_test_timing"
ln --symbolic /usr/bin/pg_upgrade "$bindir/pg_upgrade"
ln --symbolic /usr/bin/pg_waldump "$bindir/pg_waldump"
ln --symbolic /usr/bin/pgbench "$bindir/pgbench"
ln --symbolic /usr/bin/pgsql2shp "$bindir/pgsql2shp"
ln --symbolic /usr/bin/postgres "$bindir/postgres"
ln --symbolic /usr/bin/postmaster "$bindir/postmaster"
ln --symbolic /usr/bin/psql "$bindir/psql"
ln --symbolic /usr/bin/raster2pgsql "$bindir/raster2pgsql"
ln --symbolic /usr/bin/reindexdb "$bindir/reindexdb"
ln --symbolic /usr/bin/shp2pgsql "$bindir/shp2pgsql"
ln --symbolic /usr/bin/vacuumdb "$bindir/vacuumdb"

%files
%defattr(-,awips,fxalpha,-)
/awips2/postgresql/bin/*

%defattr(644,root,root,755)
/etc/profile.d/awips2PSQL.sh
/etc/profile.d/awips2PSQL.csh

%package -n awips2-psql

Summary: AWIPS II PSQL compatibility package
Group: AWIPSII
# This gets us /usr/bin/psql
Requires: postgresql >= 12

%description -n awips2-psql
Provides the /awips2/psql/bin/psql symlink 

%files -n awips2-psql
%defattr(-,awips,fxalpha,-)
/awips2/psql/bin/psql
