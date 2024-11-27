# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _build_id_links none
%define _setuptools_version 70.0.0

# Update this as necessary when Python is upgraded.  Also update
# the Version line with this information.
# The Version cannot refer to these variables since the Version line is read by
# the build script SetupEnvironment.sh to determine the Python version.
%define _python_short_version 3.11

#
# AWIPS II Python Spec File
#
Name: awips2-python
Summary: AWIPS II Python Distribution

# Epoch was incremented to 1 (default is 0) to reset the versioning scheme
# after we switched from packaging our own Python to depending on the system
# Python package.
#
# DO NOT remove or decrement the Epoch. Do not change the Epoch as part of
# normal Python upgrades or other routine changes to this package.
# 
# The only acceptable change to the Epoch is to increment it if and when the
# version numbering scheme needs to be changed again.
Epoch: 1

Version: 3.11

Release: %{_component_version}.%{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
Provides: awips2-python = %{version}
Provides: awips2-python-setuptools = %{_setuptools_version}

Requires: python3.11
Requires: python3.11-devel
Requires: python3.11-pip
Requires: python3.11-setuptools
Requires: python3.11-six
Requires: python3.11-tkinter
Requires: python3.11-wheel

BuildRequires: python3.11
BuildRequires: python3.11-devel

%description
AWIPS II Python Distribution - Provides dependencies on Python %{_python_short_version}
and modules required for AWIPS II, and creates a virtualenv for awips2-python modules.

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm --recursive --force %{_build_root}
mkdir --parents %{_build_root}/awips2/python
if [ -d %{_python_build_loc} ]; then
   rm --recursive --force %{_python_build_loc}
fi
mkdir --parents %{_python_build_loc}

%install
# Copies the standard Raytheon licenses into a license directory for the
# current component.
function copyLegal()
{
   # $1 == Component Build Root

   COMPONENT_BUILD_DIR=${1}

   mkdir --parents %{_build_root}/${COMPONENT_BUILD_DIR}/licenses

   cp "%{_baseline_workspace}/rpms/legal/Master_Rights_File.pdf" \
      %{_build_root}/${COMPONENT_BUILD_DIR}/licenses
}

# Create the virtual environment
"/usr/bin/python%{_python_short_version}" -m venv --system-site-packages %{_build_root}/awips2/python

# Install our newer version of setuptools into the virtual environment. We have
# to activate the virtual environment before doing this, otherwise we screw up
# the build environment's setuptools installation. Note that awips2-python-setuptools
# is not in its own RPM because the virtualenv places files down that setuptools
# also places, and then the two RPMs would conflict as providing the same files.
# So we install it as part of awips2-python to get around that.
setuptools_src_dir="%{_baseline_workspace}/foss/setuptools-%{_setuptools_version}/packaged"
setuptools_package_file="setuptools-%{_setuptools_version}-py3-none-any.whl"

source %{_build_root}/awips2/python/bin/activate
pip3 install "${setuptools_src_dir}/${setuptools_package_file}" || exit 1
deactivate

# Our profile.d scripts.
mkdir --parents %{_build_root}/etc/profile.d
PYTHON_PROJECT_DIR="%{_baseline_workspace}/installers/RPMs/python"
PYTHON_PROJECT_SRC_DIR="${PYTHON_PROJECT_DIR}/src"
PYTHON_SCRIPTS_DIR="${PYTHON_PROJECT_DIR}/scripts"
PYTHON_PROFILED_DIR="${PYTHON_SCRIPTS_DIR}/profile.d"
cp --verbose ${PYTHON_PROFILED_DIR}/* %{_build_root}/etc/profile.d
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

copyLegal "awips2/python"

# Python virtualenvs are not ready for distribution when created. There are
# hardcoded absolute paths inside. The below command updates those paths to
# point to where the virtualenv will be installed on the target system.
grep --fixed-strings --recursive --null --files-with-matches \
    --binary-files=without-match \
    '%{_build_root}/awips2/python' \
    '%{_build_root}/awips2/python/bin' '%{_build_root}/awips2/python/pyvenv.cfg' \
    | xargs --null sed -i 's|%{_build_root}/awips2/python|/awips2/python|g'

%clean
rm --recursive --force %{_build_root}
rm --recursive --force %{_python_build_loc}

%files
%attr(755,root,root) /etc/profile.d/awips2Python.csh
%attr(755,root,root) /etc/profile.d/awips2Python.sh
%defattr(-,awips,fxalpha,-)
/awips2/python

%changelog
* Thu Sep 12 2024 Howard Van Dam <howard.vandam@rtx.com>
- Upgrade setuptools to version 70.0.0
* Wed May 24 2023 Tom Gurney <thomas.gurney@rtx.com>
- Upgrade to Python 3.11
* Fri Apr 21 2023 Tom Gurney <thomas.gurney@rtx.com>
- Do grep/sed only on scripts in bin dir. Stops corrupting pyc files
* Wed Mar 01 2023 David Gillingham <david.gillingham@rtx.com>
- Move to python version 3.9
- Cleanup dependency lists to remove obsolete items.
* Wed Jul 06 2022 Lisa Singh <lisa.e.singh@raytheon.com>
- Use Redhat lapack instead of packaged lapack.
- Remove lapack dependency blas
* Fri Mar 04 2022 Nate Jensen <nate.jensen@raytheon.com>
- Removed packaging of gridslice.so and grib2.so
* Tue Mar 01 2022 Tom Gurney <tom.gurney@raytheon.com>
- Add links to RH-provided shared library
* Wed Feb 02 2022 Tom Gurney <tom.gurney@raytheon.com>
- Switch to Python provided by RH software collection
* Mon Jul 26 2021 Matt Richardson <matthew.richardson@raytheon.com>
- Add python38-six package to dependencies, use long form of command options
* Fri Jul 16 2021 Nate Jensen <nate.jensen@raytheon.com>
- Switch to python38, use --system-site-packages when creating venv
* Wed Jul 07 2021 Tom Gurney <tom.gurney@raytheon.com>
- Add python3-tkinter as a dependency
* Mon Jun 28 2021 David Gillingham <david.gillingham@raytheon.com> 
- Updates for RHEL8, move to system libjasper.
* Mon Feb 22 2021 David Gillingham <david.gillingham@raytheon.com> 
- Add "--with-ensurepip" configure flag to python build.
* Tue Oct 06 2020 Ron Anderson <ron.anderson@raytheon.com> 
- Added obsoletes for pmw
