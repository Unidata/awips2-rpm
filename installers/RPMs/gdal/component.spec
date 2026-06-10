# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _build_id_links none

Name: awips2-python-gdal
Summary: AWIPS II GDAL Distribution
Epoch: 1
Version: 3.5.3
Release: %{_installed_python_short}.3%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: ${_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: libqhull_r
Requires: awips2-hdf5
Requires: awips2-netcdf
Requires: awips2-python
Requires: awips2-python-geos
Requires: awips2-python-proj

BuildRequires: awips2-hdf5
BuildRequires: awips2-python
BuildRequires: awips2-netcdf
BuildRequires: awips2-python-geos
BuildRequires: awips2-python-proj
BuildRequires: jasper-devel
BuildRequires: qhull-devel

%description
AWIPS II GDAL Site-Package

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

if [ -d ${RPM_BUILD_ROOT} ]; then
   rm -rf ${RPM_BUILD_ROOT}
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi

rm -rf %{_build_root}
mkdir -p %{_build_root}
if [ -d %{_build_root}/build-python ]; then
   rm -rf %{_build_root}/build-python
fi
mkdir -p %{_build_root}/build-python
if [ -d %{_python_build_loc} ]; then
   rm -rf %{_python_build_loc}
fi
mkdir -p %{_python_build_loc}

%build

python_staging="%{_python_build_loc}/awips2/python"
mkdir -p "${python_staging}"

gdal_src="gdal-%{version}"
gdal_src_dir="%{_baseline_workspace}/foss/${gdal_src}/packaged"

cp ${gdal_src_dir}/${gdal_src}.tar.gz %{_python_build_loc} || exit 1

cd %{_python_build_loc}
tar -xf "${gdal_src}.tar.gz" || exit 1
cd "${gdal_src}"

CFLAGS=-I/awips2/netcdf/include LDFLAGS='-L/awips2/netcdf/lib -Wl,-rpath,/awips2/python/lib,-rpath,/awips2/netcdf/lib' ./configure \
   --prefix=/awips2/python \
   --with-sqlite3=/awips2/python \
   --with-proj=/awips2/python \
   --with-expat-lib=%{_usr}/%{_lib} \
   --with-python=/awips2/python/bin/python \
   --with-geos=/awips2/python/bin/geos-config \
   --with-netcdf=/awips2/netcdf || exit 1
make %{?_smp_mflags} || exit 1
make install prefix=${python_staging} || exit 1

%install

mkdir -p %{_build_root}/awips2 || exit 1
cp -rf %{_python_build_loc}/awips2/* %{_build_root}/awips2 || exit 1

# Merge lib64 into lib to avoid problems with installing into the virtualenv
if [ -d "%{_build_root}/awips2/python/lib64/" ]; then
    rsync --archive %{_build_root}/awips2/python/lib64/ %{_build_root}/awips2/python/lib || exit 1
    rm --recursive --force %{_build_root}/awips2/python/lib64
fi

%clean
rm -rf %{_build_root}
rm -rf %{_python_build_loc}

%files
%defattr(755,awips,fxalpha,755)
/awips2/python/bin/*
%defattr(644,awips,fxalpha,755)
/awips2/python/lib/*
/awips2/python/include/*
/awips2/python/share/*
