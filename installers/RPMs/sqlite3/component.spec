# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'; else echo 0; fi)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _sqlite_version_formatted 3500400
%define _build_id_links none

Name: awips2-python-sqlite3
Summary: AWIPS II sqlite3 Site-Package
Epoch: 1
Version: 3.50.4
Release: %{_installed_python_short}.2%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: ${_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: awips2-python
BuildRequires: awips2-python

%description
AWIPS II sqlite3 Site-Package

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm -rf %{_build_root}
mkdir -p %{_build_root} || exit 1

if [ -d %{_python_build_loc} ]; then
   rm -rf %{_python_build_loc}
fi
mkdir -p %{_python_build_loc}

%build

python_staging="%{_python_build_loc}/awips2/python"
mkdir -p "${python_staging}"

sqlite_src="sqlite-autoconf-%{_sqlite_version_formatted}"
sqlite_src_dir="%{_baseline_workspace}/foss/sqlite3-%{version}/packaged/"

cp "${sqlite_src_dir}/${sqlite_src}.tar.gz" %{_python_build_loc} || exit 1

cd %{_python_build_loc}
tar -xf "${sqlite_src}.tar.gz" || exit 1
cd "${sqlite_src}"

./configure --prefix=/awips2/python || exit 1
make || exit 1
make install prefix="${python_staging}" || exit 1

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
