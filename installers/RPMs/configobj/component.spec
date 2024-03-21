# Change the brp-python-bytecompile script to use the AWIPS2 version of Python. #7237
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's/\/usr\/bin\/python/\/awips2\/python\/bin\/python/g')
%define _installed_python_short %(if [ -f /awips2/python/bin/python ]; then /awips2/python/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))'; else echo 0; fi)
%define _build_arch %(uname -i)
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"

#
# AWIPS II Python configobj Spec File
#

Name: awips2-python-configobj
Summary: AWIPS II Python configobj module
Epoch: 1
Version: 5.0.6
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
Requires: awips2-python >= %{_installed_python_short}
Requires: python%{_installed_python_short}-six

BuildRequires: awips2-python
BuildRequires: awips2-python-setuptools

%description
AWIPS II Python configobj Site-Package

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
if [ -d %{_python_build_loc} ]; then
   rm --recursive --force %{_python_build_loc}
fi
mkdir --parents %{_python_build_loc}

%build
SRC_DIR="%{_baseline_workspace}/foss/configobj-%{version}/packaged"
TAR_FILE="configobj-%{version}.tar.gz"
cp --verbose ${SRC_DIR}/${TAR_FILE} \
   %{_python_build_loc}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null
cd %{_python_build_loc}
tar --extract --verbose --file=${TAR_FILE}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
rm --force --verbose ${TAR_FILE}
if [ ! -d configobj-%{version} ]; then
   echo "Directory configobj-%{version} not found!"
   exit 1
fi
source /etc/profile.d/awips2Python.sh
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
cd configobj-%{version}

# Patch CVE 2023-26112 - regex denial of service
# Description from NIST:
#
# All versions of the package configobj are vulnerable to Regular Expression
# Denial of Service (ReDoS) via the validate function, using (.+?)\((.*)\).
# **Note:** This is only exploitable in the case of a developer, putting the
# offending value in a server side configuration file.
patch validate.py << 'EOF'
545c545
<     _func_re = re.compile(r'(.+?)\((.*)\)', re.DOTALL)
---
>     _func_re = re.compile(r'([^\(\)]+?)\((.*)\)', re.DOTALL)
EOF
# end patch

/awips2/python/bin/python setup.py build
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null


%install
SRC_DIR="%{_python_pkgs_dir}/configobj"

pushd . > /dev/null
cd %{_python_build_loc}/configobj-%{version}
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
/awips2/python/lib/python%{_installed_python_short}/site-packages/configobj.py
/awips2/python/lib/python%{_installed_python_short}/site-packages/validate.py
/awips2/python/lib/python%{_installed_python_short}/site-packages/_version.py
/awips2/python/lib/python%{_installed_python_short}/site-packages/configobj-%{version}-py%{_installed_python_short}.egg-info
%exclude /awips2/python/lib/python%{_installed_python_short}/site-packages/__pycache__


%changelog
* Wed Feb 14 2024 Tom Gurney <thomas.gurney@rtx.com>
- Patch CVE 2023-26112
* Thu Jul 15 2021 Lisa Singh <lisa.e.singh@raytheon.com> 
- Initial package creation.
