%global _python_bytecompile_extra 0
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _build_id_links none

#
# AWIPS II Python Pillow Spec File
#
Name: awips2-python-pillow
Summary: AWIPS II Python Pillow Distribution
Epoch: 1
Version: 12.2.0
Release: %{_installed_python_short}.1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: https://pypi.python.org/pypi/Pillow
License: GNU General Public License v2
Vendor: ${_build_vendor}

AutoReq: no
Requires: awips2-python >= %{_installed_python_short}

BuildRequires: awips2-python
BuildRequires: awips2-python-setuptools

#External libraries defined from:
#https://pillow.readthedocs.io/en/stable/installation.html

#Provides compressed TIFF functionality
#Requires: libtiff
#BuildRequires: libtiff-devel

#Provides JPEG functionality
Requires: libjpeg-turbo
BuildRequires: libjpeg-turbo-devel

#Provides access to compressed PNGs
Requires: zlib
BuildRequires: zlib-devel

#Provides type related services
Requires: freetype >= 2.8
BuildRequires: freetype-devel

#Provides color management
#Requires: lcms2 
#BuildRequires: lcms2-devel

#Provides the WebP format
#Requires: libwebp
#BuildRequires: libwebp-devel

#Provides support for tkinter bitmap and photo images
Requires: tcl
Requires: tk
BuildRequires: tcl-devel
BuildRequires: tk-devel

%description
AWIPS II Python Pillow Site-Package

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm --recursive --force %{_build_root}
mkdir --parents %{_build_root}

rm --recursive --force %{_build_root}
mkdir --parents %{_build_root}
if [ -d %{_python_build_loc} ]; then
   rm --recursive --force %{_python_build_loc}
fi
mkdir --parents %{_python_build_loc}

%build
PILLOW_SRC_DIR="%{_baseline_workspace}/foss/pillow-%{version}/packaged"
PILLOW_TAR="pillow-%{version}.tar.gz"

cp --verbose ${PILLOW_SRC_DIR}/${PILLOW_TAR} %{_python_build_loc}
pushd . > /dev/null
cd %{_python_build_loc}
tar --extract --file=${PILLOW_TAR}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
rm --force --verbose ${PILLOW_TAR}
if [ ! -d pillow-%{version} ]; then
   echo "Directory pillow-%{version} not found!"
   exit 1
fi

source /etc/profile.d/awips2Python.sh
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
cd pillow-%{version}

/awips2/python/bin/python setup.py build
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%install
pushd . > /dev/null
cd %{_python_build_loc}/pillow-%{version}
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

# Merge lib64 into lib to avoid problems with installing into the virtualenv
if [ -d "%{_build_root}/awips2/python/lib64/" ]; then
    rsync --archive %{_build_root}/awips2/python/lib64/ %{_build_root}/awips2/python/lib || exit 1
    rm --recursive --force %{_build_root}/awips2/python/lib64
fi

%clean
rm --recursive --force %{_build_root}
rm --recursive --force %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
/awips2/python/lib/python%{_installed_python_short}/site-packages/PIL
/awips2/python/lib/python%{_installed_python_short}/site-packages/pillow-%{version}-py%{_installed_python_short}.egg-info/
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/PIL/__pycache__


%changelog
* Fri Jul 16 2021 Lisa Singh <lisa.e.singh@raytheon.com> 
- Moved from local apps foss to baseline.
- Cleaned up script.
