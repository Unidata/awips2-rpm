%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _qpid_proton_version 0.38.0
%define _qpid_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _prefix /awips2/qpid
%define _qpid_source_dir %{_baseline_workspace}/foss/qpid-proton-%{version}
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _build_id_links none

#
# AWIPS II Qpid Proton Python Spec File
#

Name: awips2-qpid-proton-python
Summary: AWIPS II QPID Proton Distribution
Epoch: 1
Version: %{_qpid_proton_version}
Release: %{_installed_python_short}.5%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
License:        Apache Software License
Group:          Development/Java
URL:            http://qpid.apache.org/
Packager: %{_build_site}

AutoReq: no
Provides: awips2-qpid-proton-python = %{_qpid_proton_version}
Requires: awips2-python >= %{_installed_python_short}
Requires: awips2-qpid-proton
Requires: libuuid
Requires: swig

BuildRequires: awips2-python
BuildRequires: awips2-qpid-proton
BuildRequires: make
BuildRequires: cmake >= 2.8.11
BuildRequires: gcc-c++
BuildRequires: libuuid-devel
BuildRequires: swig

Obsoletes: awips2-python-qpid

%description
AWIPS II QPID Proton Distribution - Contains the qpid proton Python
files for qpid proton %{_qpid_proton_version}.

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
if [ -d %{_qpid_build_loc} ]; then
   rm --recursive --force %{_qpid_build_loc}
fi
mkdir --parents %{_qpid_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi

QPID_SOURCE_FILE="qpid-proton-%{version}.tar.gz"

cp --verbose %{_qpid_source_dir}/${QPID_SOURCE_FILE} %{_qpid_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null 2>&1
cd %{_qpid_build_loc}
tar --extract --verbose --file=${QPID_SOURCE_FILE}
if [ $? -ne 0 ]; then
   exit 1
fi

popd > /dev/null 2>&1

%build
pushd . > /dev/null 2>&1

mkdir --parents %{_qpid_build_loc}/qpid-proton-%{version}/build
if [ $? -ne 0 ]; then
   exit 1
fi

cd %{_qpid_build_loc}/qpid-proton-%{version}/build

%cmake .. \
	-DSYSINSTALL_BINDINGS=ON \
    -DBUILD_PYTHON=ON \
    -DBUILD_CPP=OFF -DBUILD_RUBY=OFF -DBUILD_CPP_03=OFF
if [ $? -ne 0 ]; then
   exit 1
fi

LDFLAGS=-Wl,-rpath=/awips2/qpid/lib64 make
if [ $? -ne 0 ]; then
   exit 1
fi

cd %{_qpid_build_loc}/qpid-proton-%{version}/build/python/dist
PKG_CONFIG_PATH=/awips2/qpid/lib64/pkgconfig \
LDFLAGS=-Wl,-rpath=/awips2/qpid/lib64 \
/awips2/python/bin/python setup.py build
if [ $? -ne 0 ]; then
   exit 1
fi

popd > /dev/null 2>&1

%install
pushd . > /dev/null 2>&1

cd %{_qpid_build_loc}/qpid-proton-%{version}/build/python/dist
PKG_CONFIG_PATH=/awips2/qpid/lib64/pkgconfig \
LDFLAGS=-Wl,-rpath=/awips2/qpid/lib64 \
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python
if [ $? -ne 0 ]; then
   exit 1
fi

popd > /dev/null 2>&1

QPID_STAT_SCRIPT="qpid-stat"
QPID_QUEUE_COUNT_SCRIPT="qpid-queue-count"
QPID_MONITOR_SCRIPT="monitor_qpid_host.sh"
QPID_DISPLAY_FORMATTER="disp.py"

mkdir --parents %{_build_root}/awips2/python/bin
if [ $? -ne 0 ]; then
   exit 1
fi

# Copy the stats script to bin
cp --verbose %{_qpid_source_dir}/bin/${QPID_STAT_SCRIPT} \
   %{_build_root}/awips2/python/bin
if [ $? -ne 0 ]; then
   exit 1
fi

# Copy the queue-counting script to bin
cp --verbose %{_qpid_source_dir}/bin/${QPID_QUEUE_COUNT_SCRIPT} \
   %{_build_root}/awips2/python/bin
if [ $? -ne 0 ]; then
   exit 1
fi

# Copy the monitoring script to bin
cp --verbose %{_qpid_source_dir}/bin/${QPID_MONITOR_SCRIPT} \
   %{_build_root}/awips2/python/bin

# Copy the display formatter to bin
cp --verbose %{_qpid_source_dir}/bin/${QPID_DISPLAY_FORMATTER} \
   %{_build_root}/awips2/python/bin

# Merge lib64 into lib to avoid problems with installing into the virtualenv
if [ -d "%{_build_root}/awips2/python/lib64/" ]; then
    rsync --archive %{_build_root}/awips2/python/lib64/ %{_build_root}/awips2/python/lib || exit 1
    rm --recursive --force %{_build_root}/awips2/python/lib64
fi

%clean
rm --recursive --force %{_build_root}
rm --recursive --force %{_qpid_build_loc}

%files
%defattr(644,awips,fxalpha,755)
/awips2/python/lib/python%{_installed_python_short}/site-packages/*
%exclude /awips2/qpid/*
%defattr(755,awips,fxalpha,755)
/awips2/python/bin/*
