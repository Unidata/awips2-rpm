%define _build_arch %(uname -i)
%define _postgis_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Name: awips2-postgis
Summary: AWIPS II PostGIS Distribution
Version: 3.3.2
Release: %{_component_version}.%{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: ${_build_vendor}
Packager: %{_build_site}

AutoReq: no
BuildRequires: rsync
BuildRequires: libpq-devel >= 12
BuildRequires: postgresql-devel >= 12
BuildRequires: awips2-python
BuildRequires: awips2-python-gdal >= 3.2.2
BuildRequires: awips2-python-geos >= 3.5.2
BuildRequires: awips2-python-proj >= 6.3.2
BuildRequires: awips2-python-sqlite3 >= 3.34.0
BuildRequires: qhull-devel
Requires: awips2-python
Requires: awips2-python-gdal >= 3.2.2
Requires: awips2-python-geos >= 3.5.2
Requires: awips2-python-proj >= 6.3.2
Requires: awips2-python-sqlite3 >= 3.34.0
Requires: libjpeg-turbo
Requires: libqhull_r
Requires: libpq >= 12
Requires: postgresql >= 12
Requires: postgresql-server >= 12
Requires: postgresql-contrib >= 12

%description
AWIPS II PostGIS distribution

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
/bin/mkdir --parents %{_build_root} || exit 1

if [ -d %{_postgis_build_loc} ]; then
   rm --recursive --force %{_postgis_build_loc}
fi

mkdir --parents %{_postgis_build_loc} || exit 1


%build

postgis_src="postgis-%{version}"
src_dir=%{_baseline_workspace}/foss/postgis-%{version}/packaged
cd "%{_postgis_build_loc}"
tar --extract --file="${src_dir}/${postgis_src}.tar.gz" || exit 1
cd "${postgis_src}"

# We're not using --prefix here. Need to install to the /usr hierarchy where
# PostgreSQL is installed. PostGIS doesn't respect the --prefix anyway, see
# this bug: https://trac.osgeo.org/postgis/ticket/635

# --enable-lto was added in PostGIS 3.3 to support link-time optimization.
# This improves the performance of math computations.
#
# --without-protobuf is required to get this to compile.
#
LDFLAGS="-L/awips2/netcdf/lib -Wl,-rpath,/awips2/python/lib,-rpath,/awips2/netcdf/lib" \
./configure \
    --with-geosconfig=/awips2/python/bin/geos-config \
    --with-projdir=/awips2/python \
    --with-gdalconfig=/awips2/python/bin/gdal-config \
    --without-protobuf \
    --enable-lto || exit 1

make || exit 1

%install
cd "%{_postgis_build_loc}/postgis-%{version}"
make install DESTDIR="%{_postgis_build_loc}" || exit 1
rsync --archive "%{_postgis_build_loc}/usr" "%{_build_root}"

# symlinks in /awips2/postgresql/share for backward compatibility
mkdir --parents "%{_build_root}/awips2/postgresql/share"
ln --symbolic /awips2/python/share/gdal "%{_build_root}/awips2/postgresql/share/gdal"
ln --symbolic /awips2/python/share/proj "%{_build_root}/awips2/postgresql/share/proj"

# symlinks in /awips2/postgresql/bin for backward compatibility
bindir="%{_build_root}/awips2/postgresql/bin"
mkdir --parents "$bindir"
ln --symbolic /awips2/python/bin/cct "$bindir/cct"
ln --symbolic /awips2/python/bin/cs2cs "$bindir/cs2cs"
ln --symbolic /awips2/python/bin/gdal-config "$bindir/gdal-config"
ln --symbolic /awips2/python/bin/gdal_contour "$bindir/gdal_contour"
ln --symbolic /awips2/python/bin/gdal_create "$bindir/gdal_create"
ln --symbolic /awips2/python/bin/gdal_grid "$bindir/gdal_grid"
ln --symbolic /awips2/python/bin/gdal_rasterize "$bindir/gdal_rasterize"
ln --symbolic /awips2/python/bin/gdal_translate "$bindir/gdal_translate"
ln --symbolic /awips2/python/bin/gdal_viewshed "$bindir/gdal_viewshed"
ln --symbolic /awips2/python/bin/gdaladdo "$bindir/gdaladdo"
ln --symbolic /awips2/python/bin/gdalbuildvrt "$bindir/gdalbuildvrt"
ln --symbolic /awips2/python/bin/gdaldem "$bindir/gdaldem"
ln --symbolic /awips2/python/bin/gdalenhance "$bindir/gdalenhance"
ln --symbolic /awips2/python/bin/gdalinfo "$bindir/gdalinfo"
ln --symbolic /awips2/python/bin/gdallocationinfo "$bindir/gdallocationinfo"
ln --symbolic /awips2/python/bin/gdalmanage "$bindir/gdalmanage"
ln --symbolic /awips2/python/bin/gdalmdiminfo "$bindir/gdalmdiminfo"
ln --symbolic /awips2/python/bin/gdalmdimtranslate "$bindir/gdalmdimtranslate"
ln --symbolic /awips2/python/bin/gdalsrsinfo "$bindir/gdalsrsinfo"
ln --symbolic /awips2/python/bin/gdaltindex "$bindir/gdaltindex"
ln --symbolic /awips2/python/bin/gdaltransform "$bindir/gdaltransform"
ln --symbolic /awips2/python/bin/gdalwarp "$bindir/gdalwarp"
ln --symbolic /awips2/python/bin/geod "$bindir/geod"
ln --symbolic /awips2/python/bin/geos-config "$bindir/geos-config"
ln --symbolic /awips2/python/bin/gie "$bindir/gie"
ln --symbolic /awips2/python/bin/gnmanalyse "$bindir/gnmanalyse"
ln --symbolic /awips2/python/bin/gnmmanage "$bindir/gnmmanage"
ln --symbolic /awips2/python/bin/invgeod "$bindir/invgeod"
ln --symbolic /awips2/python/bin/invproj "$bindir/invproj"
ln --symbolic /awips2/python/bin/nearblack "$bindir/nearblack"
ln --symbolic /awips2/python/bin/ogr2ogr "$bindir/ogr2ogr"
ln --symbolic /awips2/python/bin/ogrinfo "$bindir/ogrinfo"
ln --symbolic /awips2/python/bin/ogrlineref "$bindir/ogrlineref"
ln --symbolic /awips2/python/bin/ogrtindex "$bindir/ogrtindex"
ln --symbolic /awips2/python/bin/proj "$bindir/proj"
ln --symbolic /awips2/python/bin/projinfo "$bindir/projinfo"
ln --symbolic /awips2/python/bin/sqlite3 "$bindir/sqlite3"
ln --symbolic /awips2/python/bin/testepsg "$bindir/testepsg"

%clean
rm --recursive --force %{_postgis_build_loc}

%files
%defattr(644,root,root,755)
/usr/lib64/pgsql/*
/usr/share/*

%defattr(-,awips,fxalpha,-)
/awips2/postgresql/*

%defattr(755,root,root,755)
/usr/bin/*
