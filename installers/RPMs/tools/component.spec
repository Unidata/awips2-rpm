%define _build_arch %(uname -i)
#%define _hdf5_ver 1.8.4

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

#BuildRequires: awips2-python
#BuildRequires: awips2-python-h5py

%description
AWIPS II Distribution - Contains the AWIPS II Tool-Set. Presently,
the AWIPS II Tool-Set consists of simple scripts and wgrib exes.

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

%build

%install
mkdir -p %{_build_root}/awips2/tools/bin

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
#%dir /awips2/tools/include
#/awips2/tools/include/*
#%dir /awips2/tools/lib
#/awips2/tools/lib/*
%docdir /awips2/tools/licenses
%dir /awips2/tools/licenses
/awips2/tools/licenses/*

%defattr(755,awips,fxalpha,755)
%dir /awips2/tools/bin
/awips2/tools/bin/*
