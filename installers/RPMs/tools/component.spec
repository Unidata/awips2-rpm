%define _build_arch %(uname -i)
%define _tools_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _hdf5_ver 1.8.4

#
# AWIPS II Tools Spec File
#

Name: awips2-tools
Summary: AWIPS II Tools Distribution
Version: %{_component_version}
Release: %{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
Provides: awips2-tools

BuildRequires: awips2-python
BuildRequires: awips2-python-h5py

%description
AWIPS II Python Distribution - Contains the AWIPS II Tool-Set. Presently,
the AWIPS II Tool-Set consists of various hdf5 utilities.

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "An Actual BuildRoot Must Be Specified. Use The --buildroot Parameter."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm -rf %{_build_root}
mkdir -p %{_build_root}
# The temporary build location of hdf5 and lzf
if [ -d %{_tools_build_loc} ]; then
   rm -rf %{_tools_build_loc}
fi
mkdir -p %{_tools_build_loc}

%build
HDF5_SOURCE_DIR="%{_baseline_workspace}/foss/hdf5-%{_hdf5_ver}/packaged"
HDF5_TAR_FILE="hdf5-%{_hdf5_ver}-patch1.tar.gz"
LZF_TAR_FILE="lzf.tar.gz"

# Copy the hdf5 source tar files to our temporary build directory
cp ${HDF5_SOURCE_DIR}/* %{_tools_build_loc}

cd %{_tools_build_loc}

# Untar both tar files.
tar -xf ${HDF5_TAR_FILE}
tar -xf ${LZF_TAR_FILE}

pushd . > /dev/null 2>&1
# Apply the patch.
cd hdf5-1.8.4-patch1
patch -p2 -i ../hdf5-1.8.4-patch1.patch0
if [ $? -ne 0 ]; then
   exit 1
fi

export AM_CPPFLAGS="-I%{_tools_build_loc}/lzf/include"

# run configure to generate the auto-generated hdf5 headers
LDFLAGS='-Wl,-rpath,/awips2/tools/lib,-rpath,/awips2/python/lib/' ./configure --prefix=%{_build_root}/awips2/tools
if [ $? -ne 0 ]; then
   exit 1
fi
popd > /dev/null 2>&1

pushd . > /dev/null 2>&1
# build lzf
cd lzf
gcc -O2 -I%{_tools_build_loc}/hdf5-%{_hdf5_ver}-patch1/src \
   -fPIC -shared lzf/*.c lzf_filter.c \
   -L /awips2/python/lib -lhdf5 \
   -Wl,-rpath,/awips2/tools/lib,-rpath,/awips2/python/lib \
   -o liblzf_filter.so
if [ $? -ne 0 ]; then
   exit 1
fi
popd > /dev/null

cd hdf5-%{_hdf5_ver}-patch1
export AM_LDFLAGS="-L%{_tools_build_loc}/lzf"
export LIBS="-llzf_filter"

# re-configure to include the lzf_filter library that was built previously
LDFLAGS='-Wl,-rpath,/awips2/tools/lib,-rpath,/awips2/python/lib/' ./configure --prefix=/awips2/tools
if [ $? -ne 0 ]; then
   exit 1
fi

make %{?_smp_mflags}
if [ $? -ne 0 ]; then
   exit 1
fi

%install
mkdir -p %{_build_root}/awips2/tools

cd %{_tools_build_loc}/hdf5-%{_hdf5_ver}-patch1
make install prefix=%{_build_root}/awips2/tools

# Copy the lzf library to tools/lib
cp %{_tools_build_loc}/lzf/*.so \
   %{_build_root}/awips2/tools/lib

# Copies the standard Raytheon licenses into a license directory for the
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

copyLegal "awips2/tools"

# wgrib programs
TOOLS_DIR="%{_baseline_workspace}/installers/RPMs/tools/programs"
/bin/cp -r ${TOOLS_DIR}/* ${RPM_BUILD_ROOT}/awips2/tools/bin/

%clean
rm -rf ${RPM_BUILD_ROOT}
rm -rf %{_tools_build_loc}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/tools
%dir /awips2/tools/include
/awips2/tools/include/*
%dir /awips2/tools/lib
/awips2/tools/lib/*
%docdir /awips2/tools/licenses
%dir /awips2/tools/licenses
/awips2/tools/licenses/*

%defattr(755,awips,fxalpha,755)
%dir /awips2/tools/bin
/awips2/tools/bin/*
