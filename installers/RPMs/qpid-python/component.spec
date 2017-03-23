%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#
# AWIPS II Python qpid Spec File
#
Name: awips2-python-qpid
Summary: AWIPS II Python qpid Distribution
Version: 0.32
Release: 3%{?dist}
BuildArch: noarch
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: noarch
License:        Apache Software License
Group:          Development/Java
URL:            http://qpid.apache.org/
Packager: %{_build_site}

AutoReq: no
requires: awips2-python
provides: awips2-python-qpid = %{version}

BuildRequires: awips2-python

%description
AWIPS II Python qpid Site-Package

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm -rf %{_build_root}
mkdir -p %{_build_root}
if [ -d %{_python_build_loc} ]; then
   rm -rf %{_python_build_loc}
fi
mkdir -p %{_python_build_loc}

%build
QPID_SRC_DIR="%{_baseline_workspace}/foss/qpid-python-%{version}"
QPID_TAR="qpid-python-%{version}.tar.gz"

cp -rv ${QPID_SRC_DIR}/${QPID_TAR} \
   %{_python_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi
      
pushd . > /dev/null
cd %{_python_build_loc}
tar -xvf ${QPID_TAR}
rm -f ${QPID_TAR}
popd > /dev/null

%install
QPID_SRC_DIR="%{_baseline_workspace}/foss/qpid-python-%{version}"
QPID_SRC="qpid-python-%{version}"
QPID_STAT_SCRIPT="qpid-stat"
QPID_QUEUE_COUNT_SCRIPT="qpid-queue-count"
QPID_MONITOR_SCRIPT="monitor_qpid_host.sh"

pushd . > /dev/null
cd %{_python_build_loc}/${QPID_SRC}
mkdir -p %{_build_root}/awips2/python
/awips2/python/bin/python setup.py build
if [ $? -ne 0 ]; then
make install PREFIX=%{_build_root}/awips2/python DATA_DIR=/awips2/python
fi
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python
if [ $? -ne 0 ]; then
   exit 1
fi
popd > /dev/null

# Copy the stats script to bin
cp -v ${QPID_SRC_DIR}/bin/${QPID_STAT_SCRIPT} \
   %{_build_root}/awips2/python/bin
if [ $? -ne 0 ]; then
   exit 1
fi
   
# Copy the queue-counting script to bin
cp -v ${QPID_SRC_DIR}/bin/${QPID_QUEUE_COUNT_SCRIPT} \
   %{_build_root}/awips2/python/bin
if [ $? -ne 0 ]; then
   exit 1
fi
   
# Copy the monitoring script to bin
cp -v ${QPID_SRC_DIR}/bin/${QPID_MONITOR_SCRIPT} \
   %{_build_root}/awips2/python/bin

%preun

%postun

%clean
rm -rf ${RPM_BUILD_ROOT}
rm -rf %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/python/lib/python2.7/site-packages
/awips2/python/lib/python2.7/site-packages/*
%defattr(755,awips,fxalpha,755)
%dir /awips2/python/bin
/awips2/python/bin/*
