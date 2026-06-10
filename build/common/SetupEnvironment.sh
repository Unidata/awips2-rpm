#!/bin/bash

#
# This script will check if the environment packages required
# during the build process are installed on the building system.
# If not, this script will build the missing or updated packages
# and cache them for future builds.
#
# SCRIPT HISTORY
#
# Date          Ticket#  Engineer    Description
# ------------- -------- ----------- -----------------------------
# Mar 10, 2016  4734     dlovely     Initial creation
# Jul 13, 2016  4684     dlovely     Updated to support Python upgrades
# Dec 08, 2016  19264    shooper     Moved eclipse after python in build order
# May 07, 2018  6448     dlovely     Added HDF5 and NetCDF to build. Moved Postgresql to build after NetCDF.
# Sep 10, 2018  6448     dlovely     Added HDF5 and NetCDF to Python cache dir since search paths were added.
# Apr 30, 2018  7825     dgilling    Added cython to Python cache dir as needed by h5py.
# May 06, 2019  7842     dgilling    Added cftime to Python cache dir as needed by netcdf4-python.
# May 08, 2019  7829     dgilling    Added cycler, kiwisolver, subprocess32 and backports.functools_lru_cache to Python cache dir as needed by matplotlib.
# May 17, 2019  7830     dgilling    Added cheroot, contextlib2, jaraco.functools, more-itertools, portend,
#                                    setuptools_scm_git_archive, tempora and zc.lockfile to Python cache dir as needed
#                                    by CherryPy.
# May 22, 2019  7808     dgilling    Remove nose.
# Jun 01, 2019  7862     dlovely     Added support for Local Apps Foss to the build process.
# Jun 17, 2019  7837     dgilling    Added funcsigs, mock, numexpr and pbr to Python cache dir as needed by tables.
# Jun 25, 2019  7861     dgilling    Sym-link and source profile script for postgreSQL.
# Apr 03, 2020  8128     randerso    Remove subprocess32
# Aug 19, 2020  8216     tgurney     Get the Java version from the spec file
#                                    instead of package directory name (since
#                                    we are not packaging Java itself anymore)
# Sep 10, 2020  8218     tgurney     Remove setuptools build. (The package is
#                                    now included with Python itself). Get the
#                                    Python version from the spec file instead
#                                    of from a package directory name.
# Feb 22, 2021  8373     dgilling    Added cached-property.
# Mar 19, 2021  8371     dgilling    Added zipp.
# May 25, 2021  8460     tgurney     Add gdal, geos, proj, sqlite3
# May 26, 2021  8460     tgurney     Move NetCDF to build before Python
# Sep 10, 2020  8218     tgurney     Remove setuptools build. (The package is
#                                    now included with Python itself). Get the
#                                    Python version from the spec file instead
#                                    of from a package directory name.
# Jul 16, 2021  8518     mrichardson Added dependency importlib-resources required by jaraco.text
# Jul 20, 2021  8501     njensen     Removed numpy as it will be provided by RedHat
# Jul 22, 2021  8516     mrichardson Removed cheroot as it will be provided
#                                    by a Python wheel and no longer needs to be built.
# Jul 22, 2021  8538     mrichardson Removed pbr, contextlib2, and zipp as they are no longer
#                                    needed for building other packages or at runtime
# Jul 22, 2021  8502     njensen     Removed pytz as it will be be provided by RedHat
# Aug 09, 2021  8619     dgilling    Removed backports.lru-cache as it is obsolete.
# Jul 14, 2021  8437     tgurney     Rewrite. Replace fake RPM install with
#                                    real RPM install. Remove support for
#                                    multiple cached Python builds
# Jul 16, 2021  8518     mrichardson Added dependency importlib-resources required by jaraco.text
# Jul 20, 2021  8501     njensen     Removed numpy as it will be provided by RedHat
# Jul 22, 2021  8516     mrichardson Removed cheroot as it will be provided
#                                    by a Python wheel and no longer needs to be built.
# Jul 22, 2021  8538     mrichardson Removed pbr, contextlib2, and zipp as they are no longer
#                                    needed for building other packages or at runtime
# Jul 22, 2021  8502     njensen     Removed pytz as it will be be provided by RedHat
# Aug 04, 2021  8599     dgilling    Removed pyparsing as it will be be provided by RedHat
# Aug 05, 2021  8598     dgilling    Removed more-itertools as it will be be provided by RedHat.
# Aug 09, 2021  8619     dgilling    Removed backports.lru-cache as it is obsolete.
# Aug 30, 2021  8437     tgurney     Switch from rpm to yum for RPM installs.
#                                    (It handles upgrades automatically)
# Oct 01, 2021  8669     njensen     Added support for awips2-netcdf.i386
# Oct 13, 2021  8566     njensen     Added netcdf-cxx.i686 and udunits.i686
# May 17, 2022  8799     dgilling    Remove thrift from list of prebuilt python FOSS libs.
# May 26, 2022  8799     dgilling    Pre-install awips2-thrift to support
#                                    AWIPS2_nativelib build.
# Jul 30, 2022  8900     dgilling    Pre-install awips2-boost to support
#                                    awips2-thrift build.
# Oct 06, 2022  8063     dgilling    Remove boost for RHEL8.
# Nov 16, 2022  8975     dgilling    Build werkzeug dependency MarkupSafe.
# Nov 09, 2022  8941     thuggins    Switch to Redhat-provided Maven
# Mar 03, 2023  9060     dgilling    Add python package tomli which is a dependency for
#                                    setuptools_scm version 7.1.0.
# Mar 03, 2023  9041     dgilling    Add python package typing_extensions to python build
#                                    which is a dependency for setuptools_scm version
#                                    7.1.0.
# Mar 03, 2023  9036     dgilling    Add python package pytz to python build
#                                    which is a dependency for tempora and matplotlib.
# Mar 10, 2023  9040     dgilling    Remove python package setuptools_scm_git_archive
#                                    from python build as functionality is now part of
#                                    setuptools_scm.
# Mar 10, 2023  9039     dgilling    Remove python package cached-property from python 
#                                    build as it is no longer required by h5py.
# Mar 14, 2023  9058     dgilling    Re-ordering cython and numpy in Python FOSS build so
#                                    they are built before shapely.
# Mar 15, 2023  XXXX     dgilling    Add python package cppy to python build
#                                    which is a build-time dependency for 
#                                    kiwisolver.
# Jun 05, 2023  2034253  dgilling    Add python package more_itertools to python build
#                                    which is a build-time dependency for 
#                                    jaraco.functools, cherrypy and others.
# Jun 05, 2023  2035792  tgurney     Add --cacheonly and --noplugins options
#                                    to yum for speed
# Jun 07, 2023  2034280  dgilling    Add meson package after python build, which is a 
#                                    build dependency of contourpy.
# Jun 09, 2023  2035800  dgilling    Add pyproject-metadata package to python build, 
#                                    which is a build dependency of meson_python.
# Jun 09, 2023  2034281  dgilling    Add meson_python package to python build, 
#                                    which is a build dependency of ContourPy.
# Jun 09, 2023  2034277  dgilling    Add ContourPy package to python build, 
#                                    which is a dependency of matplotlib.
# Jun 09, 2023  2034278  dgilling    Add fontTools package to python build, 
#                                    which is a dependency of matplotlib.
# Jun 15, 2023  2035790  dgilling    Add libaec and eccodes packages to local apps
#                                    FOSS builds, which is required by pygrib.
# Jun 21, 2023  2034270  jsebahar    Add python packages py_cpuinfo, msgpack and blosc2 to
#                                    python build which are build-time dependencies for tables.
# Nov 16, 2022  8975     dgilling    Build werkzeug dependency MarkupSafe.
# Oct 04, 2023  2030115  lisa.singh  Added gradle, as it is needed to build YAJSW
# Dec 18, 2023  2036747  lisa.singh  Build werkzeug dependency MarkupSafe.
# Jan 03, 2024  2036307  jsebahar    Modified yum install to install packages simultaneously
#                                    to avoid dependency issues with a -devel package.
# Dec 17, 2025  2040414  tjensen     Add python packaging to build before meson,
#                                    which is a dependency for setuptools.
# Jan 08, 2025  2040611  njensen     Added ninja-build as it is needed to build hdf5
# Apr 20, 2026  2041593  mapeters    Removed awips2-aec

# Finds the version of a given FOSS package.
#   $1 - Name of the FOSS package
function getRequiredVersionFromDirName {
   local fosspackage=${1}
   local dir=`ls -d ${WORKSPACE}/git/AWIPS2_build/foss/${fosspackage}-[0-9]* 2>/dev/null`
   ver="${dir##*-}"
   [[ "$ver" == "" ]] && exit 1
   echo "$ver"
}

# Finds the version of a given FOSS package in the AWIPS2_Local_Apps_FOSS repo
#   $1 - Name of the FOSS package
function getLAFOSSVersion {
   local fosspackage=${1}
   local dir=`ls -d ${WORKSPACE}/git/AWIPS2_Local_Apps_FOSS/foss/${fosspackage}-[0-9]* 2>/dev/null`
   ver="${dir##*-}"
   [[ "$ver" == "" ]] && exit 1
   echo "$ver"
}

# Finds the version of a given RPM package by checking component.spec
#   $1 - Name of the RPM package, without awips2- prefix
function getRequiredVersionFromSpecFile { 
   local pkgdir="${WORKSPACE}/git/AWIPS2_build/installers/RPMs/${1}"
   ver=$(grep -Eio '^\s*Version: .*' "${pkgdir}/component.spec" | awk '{print $2;}')
   [[ "$ver" == "" ]] && exit 1
   echo "$ver"
}

# Gets the version of a currently installed RPM package
#   $1 - Name of the RPM package
function getRPMVersion {
    local rpmname="$1"
    result=$(rpm -qi "${rpmname}" | grep -Eo '^Version\s+:.*' | awk '{print $3;}')
    echo "${result}"
}

mkdir -p /awips2

# IMPORTANT NOTE:
# Due to the recursive structure of the build process, packages listed here are
# installed in reverse order from what is listed.

##################################
# QPID (64-bit)
##################################
QPID_VERSION=$(getRequiredVersionFromDirName qpid-proton)
if [[ "$(getRPMVersion awips2-qpid-proton.x86_64)" != "$QPID_VERSION" ]]; then
   export RPMS=("buildRPM awips2-qpid-proton")
   export LIB_ENV_BUILD_PACKAGE=awips2-qpid-proton
fi

##################################
# QPID (32-bit)
##################################
QPID_VERSION=$(getRequiredVersionFromDirName qpid-proton)
if [[ "$(getRPMVersion awips2-qpid-proton.i386)" != "$QPID_VERSION" ]]; then
   export RPMS=("buildRPM awips2-qpid-proton/i386")
   export LIB_ENV_BUILD_PACKAGE=awips2-qpid-proton
fi

##################################
# Apache Thrift (64-bit)
##################################
THRIFT_VERSION=$(getRequiredVersionFromDirName thrift)
if [[ "$(getRPMVersion awips2-thrift.x86_64)" != "$THRIFT_VERSION" ]]; then
   export RPMS=("buildRPM awips2-thrift")
   export LIB_ENV_BUILD_PACKAGE=awips2-thrift
fi

##################################
# Apache Thrift (32-bit)
##################################
THRIFT_VERSION=$(getRequiredVersionFromDirName thrift)
if [[ "$(getRPMVersion awips2-thrift.i386)" != "$THRIFT_VERSION" ]]; then
   export RPMS=("buildRPM awips2-thrift/i386")
   export LIB_ENV_BUILD_PACKAGE=awips2-thrift
fi

##################################
# Eclipse
##################################
ECLIPSE_VERSION=$(getRequiredVersionFromDirName eclipse)
if [[ "$(getRPMVersion awips2-eclipse)" != "$ECLIPSE_VERSION" ]]; then
   export RPMS=("buildRPM awips2-eclipse")
   export LIB_ENV_BUILD_PACKAGE=awips2-eclipse
fi

##################################
# Local Apps FOSS
##################################
if [ ! -z "$LOCAL_APPS_FOSS_BRANCH" ]; then
   # packages are built in reverse order from what is listed here
   for item in pygobject pycairo; do
        pypkg_version=$(getLAFOSSVersion $item)
        if [[ "$(getRPMVersion awips2-python-$item)" != "$pypkg_version" ]]; then
            export RPMS=("buildRPM awips2-python-$item")
            export LIB_ENV_BUILD_PACKAGE=awips2-python-$item
        fi
   done

   pkg_version=$(getLAFOSSVersion eccodes)
   if [[ "$(getRPMVersion awips2-eccodes)" != "$pkg_version" ]]; then
      export RPMS=("buildRPM awips2-eccodes")
      export LIB_ENV_BUILD_PACKAGE=awips2-eccodes
   fi
fi

##################################
# Python packages
##################################
# Packages are built in reverse order from what is listed here.
pypackages=(
py_cpuinfo
blosc2
msgpack
markupsafe
gdal
proj
sqlite3
importlib-resources
numexpr
matplotlib
fonttools
contourpy
pillow
certifi
portend
tempora
pytz
jaraco.functools
more_itertools
kiwisolver
cycler
cftime
dateutil
h5py
scipy
zc.lockfile
pkgconfig
shapely
numpy
cppy
cython
setuptools_scm
typing_extensions
tomli
geos
meson_python
pyproject_metadata
packaging
)

for item in "${pypackages[@]}"; do
    pypkg_version=$(getRequiredVersionFromDirName $item)
    if [[ "$(getRPMVersion awips2-python-$item)" != "$pypkg_version" ]]; then
        export RPMS=("buildRPM awips2-python-$item")
        export LIB_ENV_BUILD_PACKAGE=awips2-python-$item
    fi
done

##################################
# Meson
##################################
MESON_VERSION="$(getRequiredVersionFromSpecFile meson)"
if [[ "$(getRPMVersion awips2-meson)" != "$MESON_VERSION" ]]; then
   export RPMS=("buildRPM awips2-meson")
   export LIB_ENV_BUILD_PACKAGE=awips2-meson
fi

##################################
# Python Packaging
##################################
PACKAGING_VERSION="$(getRequiredVersionFromSpecFile packaging)"
if [[ "$(getRPMVersion awips2-python-packaging)" != "$PACKAGING_VERSION" ]]; then
   export RPMS=("buildRPM awips2-python-packaging")
   export LIB_ENV_BUILD_PACKAGE=awips2-python-packaging
fi

##################################
# Python
##################################
PYTHON_VERSION="$(getRequiredVersionFromSpecFile python)"
if [[ "$(getRPMVersion awips2-python)" != "$PYTHON_VERSION" ]]; then
   export RPMS=("buildRPM awips2-python")
   export LIB_ENV_BUILD_PACKAGE=awips2-python
else
   source /etc/profile.d/awips2Python.sh || exit 1
fi

##################################
# NetCDF
##################################
NETCDF_CXX_VERSION=$(getRequiredVersionFromDirName netcdf-cxx)
if [[ "$(getRPMVersion awips2-netcdf-cxx.i686)" != "$NETCDF_CXX_VERSION" ]]; then
   export RPMS=("buildRPM awips2-netcdf-cxx/i686")
   export LIB_ENV_BUILD_PACKAGE=awips2-netcdf-cxx
fi

NETCDF_VERSION=$(getRequiredVersionFromDirName netcdf)
if [[ "$(getRPMVersion awips2-netcdf.x86_64)" != "$NETCDF_VERSION" ]]; then
   export RPMS=("buildRPM awips2-netcdf")
   export LIB_ENV_BUILD_PACKAGE=awips2-netcdf
fi

NETCDF_VERSION=$(getRequiredVersionFromDirName netcdf)
if [[ "$(getRPMVersion awips2-netcdf.i386)" != "$NETCDF_VERSION" ]]; then
   export RPMS=("buildRPM awips2-netcdf/i386")
   export LIB_ENV_BUILD_PACKAGE=awips2-netcdf
fi

##################################
# UDUnits
##################################
UDUNITS_VERSION=$(getRequiredVersionFromDirName udunits)
if [[ "$(getRPMVersion awips2-udunits.i686)" != "$UDUNITS_VERSION" ]]; then
   export RPMS=("buildRPM awips2-udunits/i686")
   export LIB_ENV_BUILD_PACKAGE=awips2-udunits
fi

##################################
# HDF5
##################################
HDF5_VERSION="$(getRequiredVersionFromSpecFile hdf5)"
if [[ "$(getRPMVersion awips2-hdf5)" != "$HDF5_VERSION" ]]; then
   export RPMS=("buildRPM awips2-hdf5")
   export LIB_ENV_BUILD_PACKAGE=awips2-hdf5
else
   source /etc/profile.d/awips2HDF5.sh || exit 1
fi

##################################
# NINJA-BUILD
##################################
NINJA_VERSION="$(getRequiredVersionFromDirName ninja-build)"
if [[ "$(getRPMVersion awips2-ninja-build)" != "$NINJA_VERSION" ]]; then
   export RPMS=("buildRPM awips2-ninja-build")
   export LIB_ENV_BUILD_PACKAGE=awips2-ninja-build
else
   source /etc/profile.d/awips2Ninja.sh || exit 1
fi

##################################
# ANT
##################################
ANT_VERSION=$(getRequiredVersionFromDirName ant)
if [[ "$(getRPMVersion awips2-ant)" != "$ANT_VERSION" ]]; then
   export RPMS=("buildRPM awips2-ant")
   export LIB_ENV_BUILD_PACKAGE=awips2-ant
else
   source /etc/profile.d/awips2Ant.sh || exit 1
fi

##################################
# GRADLE
##################################
GRADLE_VERSION=$(getRequiredVersionFromDirName gradle)
if [[ "$(getRPMVersion awips2-gradle)" != "$GRADLE_VERSION" ]]; then
   export RPMS=("buildRPM awips2-gradle")
   export LIB_ENV_BUILD_PACKAGE=awips2-gradle
else
   source /etc/profile.d/awips2Gradle.sh || exit 1
fi

##################################
# Java
##################################
JAVA_VERSION=$(getRequiredVersionFromSpecFile java)
if [[ "$(getRPMVersion awips2-java)" != "$JAVA_VERSION" ]]; then
   export RPMS=("buildRPM awips2-java")
   export LIB_ENV_BUILD_PACKAGE=awips2-java
else
   source /etc/profile.d/awips2Java.sh || exit 1
fi

# Process the RPM just built for dependencies.
#   $1 - The primary build script to call back.
function processBuildEnv {
   local BUILDFILE=${1}
   local ORIG_RPMS=${2}

   installRPM $LIB_ENV_BUILD_PACKAGE
   if [ $? -ne 0 ]; then
      echo "ERROR: Could not install required package ${LIB_ENV_BUILD_PACKAGE}! See build logs for more details."
      exit 1
   fi

   # Make the original build request now that we have the required deps installed.
   unset RPMS
   export RPMS=${ORIG_RPMS}
   unset LIB_ENV_BUILD_PACKAGE
   $BUILDFILE
   exit $?
}

# Install staged RPM packages including any accompanying "-devel" package
#   $1 - Base name of RPM package to install
function installRPM {
   local PACKAGE=${1}

   local RPMLIST=$(ls ${WORKSPACE}/rpmbuild/RPMS/*/${PACKAGE}-*.rpm)
   if [ $? -ne 0 ]; then
      return 1
   fi

   sudo yum --noplugins --cacheonly --disablerepo=* --assumeyes install $RPMLIST || return 1

   sudo rm -f $RPMLIST
   return 0
}
