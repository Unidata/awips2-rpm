%define _build_arch %(uname -i)
%define _qpid_proton_version 0.27.1
%define _qpid_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _prefix /awips2/qpid
%define _qpid_source_dir %{_baseline_workspace}/foss/qpid-proton-%{version}

#
# AWIPS II Qpid Proton Spec File
#

Name: awips2-qpid-proton
Summary: AWIPS II QPID Proton Distribution
Version: %{_qpid_proton_version}
Release: 2%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
License:        Apache Software License
Group:          Development/Java
URL:            http://qpid.apache.org/
Packager: %{_build_site}

AutoReq: no
Provides: awips2-qpid-proton = %{_qpid_proton_version}
Requires: cyrus-sasl
Requires: libuuid
Requires: nss
Requires: nspr
Requires: openssl
Requires: swig

BuildRequires: gcc-c++
BuildRequires: make
BuildRequires: cmake >= 2.8.11
BuildRequires: cyrus-sasl-devel
BuildRequires: cyrus-sasl-plain
BuildRequires: cyrus-sasl-md5
BuildRequires: libuuid-devel
BuildRequires: nss-devel
BuildRequires: nspr-devel
BuildRequires: openssl-devel
BuildRequires: swig

Obsoletes: awips2-qpid-lib

%description
AWIPS II QPID Proton Distribution - Contains the qpid proton libraries and
header files for qpid proton %{_qpid_proton_version}.

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
if [ -d %{_qpid_build_loc} ]; then
   rm -rf %{_qpid_build_loc}
fi
mkdir -p %{_qpid_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi

QPID_SOURCE_FILE="qpid-proton-%{version}.tar.gz"

cp -v %{_qpid_source_dir}/${QPID_SOURCE_FILE} %{_qpid_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null 2>&1
cd %{_qpid_build_loc}
tar -xvf ${QPID_SOURCE_FILE}
if [ $? -ne 0 ]; then
   exit 1
fi

popd > /dev/null 2>&1

%build
pushd . > /dev/null 2>&1

mkdir -p %{_qpid_build_loc}/qpid-proton-%{version}/build
if [ $? -ne 0 ]; then
   exit 1
fi

cd %{_qpid_build_loc}/qpid-proton-%{version}/build

LIB_ARCH="lib64"
if [ ! %{_build_arch} = "x86_64" ]; then
   LIB_ARCH="lib"
fi

%cmake .. %{_qpid_build_loc}/qpid-proton-%{version} \
    -DSYSINSTALL_BINDINGS=ON  \
    -DBUILD_CPP=ON \
    -DBUILD_CPP_03=OFF -DBUILD_PYTHON=OFF -DBUILD_RUBY=OFF \
    -DSWIG_DIR=/usr/share/swig/2.0.10 \
    -DSWIG_EXECUTABLE=/usr/bin/swig \
    -DOPENSSL_CRYPTO_LIBRARY=/usr/${LIB_ARCH}/libcrypto.so \
    -DOPENSSL_SSL_LIBRARY=/usr/${LIB_ARCH}/libssl.so
if [ $? -ne 0 ]; then
   exit 1
fi

popd > /dev/null 2>&1

%install
mkdir -p %{_build_root}%{_prefix}
if [ $? -ne 0 ]; then
   exit 1
fi

mkdir -p %{_build_root}%{_prefix}%{_includedir}

if [ $? -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null 2>&1
cd %{_qpid_build_loc}/qpid-proton-%{version}/build

make DESTDIR=%{_build_root} install
if [ $? -ne 0 ]; then
   exit 1
fi
popd > /dev/null 2>&1

%clean
rm -rf %{_build_root}
rm -rf %{_qpid_build_loc}

%files
%defattr(644,awips,fxalpha,755)
%dir %{_prefix}
%dir %{_includedir}
%{_includedir}/*
%dir %{_libdir}
%{_libdir}/cmake
%{_libdir}/*.so*
%{_libdir}/pkgconfig
%exclude /awips2/qpid/share
