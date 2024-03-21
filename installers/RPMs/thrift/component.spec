# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _thrift_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _src_dir %{_baseline_workspace}/foss/thrift-%{version}/packaged


#
# AWIPS II Apache Thrift Spec File
#
Name: awips2-thrift
Summary: AWIPS II Thrift C++ API libraries
Epoch: 1
Version: 0.18.1
Release: %{_installed_python_short}.1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: https://thrift.apache.org/
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: zlib
Requires: glibc
Requires: openssl
Requires: boost
BuildRequires: zlib-devel
BuildRequires: glibc-devel
BuildRequires: openssl-devel
BuildRequires: boost-devel

%description
AWIPS II Thrift C++ API libraries


%package -n awips2-python-thrift
Summary: AWIPS II Python thrift Distribution
Group: AWIPSII

AutoReq: no
Requires: awips2-python >= %{_installed_python_short}
Requires: python%{_installed_python_short}-six
BuildRequires: awips2-python

%description -n awips2-python-thrift
AWIPS II Python thrift Site-Package


%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

if [ -d ${RPM_BUILD_ROOT} ]; then
   rm --recursive --force ${RPM_BUILD_ROOT}
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi

rm --recursive --force %{_build_root}
mkdir --parents %{_build_root}/awips2/thrift

if [ -d %{_build_root}/build-python ]; then
   rm --recursive --force %{_build_root}/build-python
fi
mkdir --parents %{_build_root}/build-python

if [ -d %{_thrift_build_loc} ]; then
   rm --recursive --force %{_thrift_build_loc}
fi
mkdir --parents %{_thrift_build_loc}

pushd . > /dev/null

cp --recursive --verbose %{_src_dir}/thrift-%{version}.tar.gz %{_thrift_build_loc} || exit 1
cd %{_thrift_build_loc}
tar --extract --verbose --file=thrift-%{version}.tar.gz

echo "Applying patch..."
cp --verbose %{_baseline_workspace}/installers/RPMs/thrift/patches/thrift-%{version}-chunked-encoding.patch \
             %{_thrift_build_loc}/thrift-%{version}
cd %{_thrift_build_loc}/thrift-%{version}
patch -p1 < thrift-%{version}-chunked-encoding.patch || exit 1

popd > /dev/null


%build
%ifarch x86_64
_cxxflags=-m64
_ldflags=-m64
_build_libs="--with-cpp --with-python"
%else
_cxxflags=-m32
_ldflags=-m32
_build_libs="--with-cpp --without-python"
%endif

pushd . > /dev/null

cd %{_thrift_build_loc}/thrift-%{version}
CXXFLAGS=${_cxxflags} LDFLAGS=${_ldflags} PY_PREFIX=%{_build_root}/awips2/python ./configure --prefix=/awips2/thrift \
         ${_build_libs} --without-c_glib --without-java --without-ruby \
         --without-qt5 --without-perl --without-lua --without-go --disable-tests --disable-static || exit 1
make %{?_smp_mflags} || exit 1

popd > /dev/null

%install
pushd . > /dev/null

cd %{_thrift_build_loc}/thrift-%{version}
make install prefix=%{_build_root}/awips2/thrift || exit 1

%ifarch x86_64
rsync --archive %{_build_root}/awips2/thrift/lib/ %{_build_root}/awips2/thrift/lib64 || exit 1
%endif

# profile.d scripts
THRIFT_PROFILED_DIR="%{_baseline_workspace}/installers/RPMs/thrift/scripts/profile.d"
mkdir --parents %{_build_root}/etc/profile.d
cp --verbose ${THRIFT_PROFILED_DIR}/* %{_build_root}/etc/profile.d

# Merge lib64 into lib to avoid problems with installing into the virtualenv
if [ -d "%{_build_root}/awips2/python/lib64/" ]; then
    rsync --archive %{_build_root}/awips2/python/lib64/ %{_build_root}/awips2/python/lib || exit 1
    rm --recursive --force %{_build_root}/awips2/python/lib64
fi

%clean
rm --recursive --force %{_build_root}
rm --recursive --force %{_thrift_build_loc}


%files -n awips2-thrift
%defattr(644,awips,fxalpha,755)
%dir /awips2/thrift
%exclude /awips2/thrift/bin/thrift
%dir /awips2/thrift/include
/awips2/thrift/include/*
%ifarch x86_64
%dir /awips2/thrift/lib64
/awips2/thrift/lib64/libthrift*.so
/awips2/thrift/lib64/libthrift*.la
/awips2/thrift/lib64/pkgconfig
%exclude /awips2/thrift/lib/libthrift*.la
%exclude /awips2/thrift/lib/libthrift*.so
%exclude /awips2/thrift/lib/pkgconfig
%else
%dir /awips2/thrift/lib
/awips2/thrift/lib/libthrift*.so
/awips2/thrift/lib/libthrift*.la
/awips2/thrift/lib/pkgconfig
%endif

%files -n awips2-python-thrift
%ifarch x86_64
%defattr(644,awips,fxalpha,755)
/awips2/python/lib/python%{_installed_python_short}/site-packages/thrift
/awips2/python/lib/python%{_installed_python_short}/site-packages/thrift-%{version}-py%{_installed_python_short}.egg-info
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/thrift/__pycache__
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/thrift/**/__pycache__
%attr(755,root,root)  /etc/profile.d/awips2Thrift.sh
%attr(755,root,root)  /etc/profile.d/awips2Thrift.csh
%else
%exclude /etc/profile.d/awips2Thrift.sh
%exclude /etc/profile.d/awips2Thrift.csh
%endif
