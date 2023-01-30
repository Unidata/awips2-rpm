#!/bin/bash

#
# This script will check if the environment pacakges required 
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

# Finds the version of a given FOSS pacakge.
#  Arg1 - The FOSS Package.
function getFOSSVersion {
   local FOSSPACKAGE=${1}

   local DIR=`ls -d ${WORKSPACE}/git/AWIPS2_build/foss/${FOSSPACKAGE}-[0-9]* 2>/dev/null`
   echo ${DIR##*-}
}
function getLAFOSSVersion {
   local FOSSPACKAGE=${1}

   local DIR=`ls -d ${WORKSPACE}/git/AWIPS2_local_apps_foss/foss/${FOSSPACKAGE}-[0-9]* 2>/dev/null`
   echo ${DIR##*-}
}

mkdir -p /awips2

##################################
# QPID (64-bit)
##################################
QPID_VERSION=$(getFOSSVersion qpid-proton)
sudo rm -f /awips2/qpid
if [ $? -ne 0 ]; then
   sudo rm -rf /awips2/qpid
fi
if [ -d /build/qpid/${QPID_VERSION}/lib64 ]; then
   sudo ln -sf /build/qpid/${QPID_VERSION} /awips2/qpid
else
   #DIR Not found! Lets build it.
   export RPMS=("buildRPM awips2-qpid-proton")
   export LIB_ENV_BUILD_PACKAGE=awips2-qpid-proton
   export LIB_ENV_BUILD_FOLDER=qpid
   export LIB_ENV_BUILD_VERSION=${QPID_VERSION}
fi

##################################
# QPID (32-bit)
##################################
QPID_VERSION=$(getFOSSVersion qpid-proton)
sudo rm -f /awips2/qpid
if [ $? -ne 0 ]; then
   sudo rm -rf /awips2/qpid
fi
if [ -d /build/qpid/${QPID_VERSION}/lib ]; then
   sudo ln -sf /build/qpid/${QPID_VERSION} /awips2/qpid
else
   #DIR Not found! Lets build it.
   export RPMS=("buildRPM awips2-qpid-proton/i386")
   export LIB_ENV_BUILD_PACKAGE=awips2-qpid-proton
   export LIB_ENV_BUILD_FOLDER=qpid
   export LIB_ENV_BUILD_VERSION=${QPID_VERSION}
fi

##################################
# Eclipse
##################################
ECLIPSE_VERSION=$(getFOSSVersion eclipse)
sudo rm -f /awips2/eclipse
if [ $? -ne 0 ]; then
   sudo rm -rf /awips2/eclipse
fi
if [ -d /build/eclipse/${ECLIPSE_VERSION}/ ]; then
   sudo ln -sf /build/eclipse/${ECLIPSE_VERSION} /awips2/eclipse
else
   #DIR Not found! Lets build it.
   export RPMS=("buildRPM awips2-eclipse")
   export LIB_ENV_BUILD_PACKAGE=awips2-eclipse
   export LIB_ENV_BUILD_FOLDER=eclipse
   export LIB_ENV_BUILD_VERSION=${ECLIPSE_VERSION}
fi

##################################
# Postgresql
##################################
POSTGRESQL_VERSION=$(getFOSSVersion postgresql)
sudo rm -f /awips2/postgresql
if [ $? -ne 0 ]; then
   sudo rm -rf /awips2/postgresql
fi
sudo rm -f /etc/profile.d/awips2Postgres.sh
if [ $? -ne 0 ]; then
   sudo rm -rf /etc/profile.d/awips2Postgres.sh
fi
if [ -d /build/postgresql/${POSTGRESQL_VERSION}/ ]; then
   sudo ln -sf /build/postgresql/${POSTGRESQL_VERSION} /awips2/postgresql
   sudo ln -sf ${WORKSPACE}/git/AWIPS2_build/installers/RPMs/postgresql/scripts/profile.d/awips2Postgres.sh /etc/profile.d/awips2Postgres.sh
   source ${WORKSPACE}/git/AWIPS2_build/installers/RPMs/postgresql/scripts/profile.d/awips2Postgres.sh
else
   #DIR Not found! Lets build it.
   export RPMS=("buildRPM awips2-postgresql")
   export LIB_ENV_BUILD_PACKAGE=awips2-postgresql
   export LIB_ENV_BUILD_FOLDER=postgresql
   export LIB_ENV_BUILD_VERSION=${POSTGRESQL_VERSION}
fi

##################################
# NetCDF
##################################
NETCDF_VERSION=$(getFOSSVersion netcdf)
sudo rm -f /awips2/netcdf
if [ $? -ne 0 ]; then
   sudo rm -rf /awips2/netcdf
fi
if [ -d /build/netcdf/${NETCDF_VERSION}/ ]; then
   sudo ln -sf /build/netcdf/${NETCDF_VERSION} /awips2/netcdf
else
   #DIR Not found! Lets build it.
   export RPMS=("buildRPM awips2-netcdf")
   export LIB_ENV_BUILD_PACKAGE=awips2-netcdf
   export LIB_ENV_BUILD_FOLDER=netcdf
   export LIB_ENV_BUILD_VERSION=${NETCDF_VERSION}
fi

##################################
# Python
##################################
# Keep track of all the version combinations we could have with the pre-installed Python packages.
PYTHON_VERSION="$(getFOSSVersion python)-0.0.0-$(getFOSSVersion numpy)-$(getFOSSVersion setuptools)-\
$(getFOSSVersion thrift)-$(getFOSSVersion h5py)-$(getFOSSVersion python-dateutil)-$(getFOSSVersion pytz)-\
$(getFOSSVersion six)-$(getFOSSVersion pyparsing)-$(getFOSSVersion netcdf)-$(getFOSSVersion hdf5)-\
$(getFOSSVersion setuptools_scm)-$(getFOSSVersion pkgconfig)-$(getFOSSVersion cython)-$(getFOSSVersion cftime)-\
$(getFOSSVersion cycler)-$(getFOSSVersion kiwisolver)-\
$(getFOSSVersion backports-lru_cache)-$(getFOSSVersion cheroot)-$(getFOSSVersion contextlib2)-\
$(getFOSSVersion jaraco.functools)-$(getFOSSVersion more-itertools)-$(getFOSSVersion portend)-\
$(getFOSSVersion setuptools_scm_git_archive)-$(getFOSSVersion tempora)-$(getFOSSVersion zc.lockfile)-\
$(getFOSSVersion shapely)-$(getFOSSVersion matplotlib)-$(getFOSSVersion funcsigs)-$(getFOSSVersion mock)-\
$(getFOSSVersion numexpr)-$(getFOSSVersion pbr)"
if [ ! -z "$LOCAL_APPS_FOSS_BRANCH" ]; then
    PYTHON_VERSION="$PYTHON_VERSION"-$(getLAFOSSVersion pygobject)-$(getLAFOSSVersion pycairo)
fi

sudo rm -f /etc/profile.d/awips2Python.sh
if [ $? -ne 0 ]; then
   sudo rm -rf /etc/profile.d/awips2Python.sh
fi
if [ -d /build/python/${PYTHON_VERSION} ]; then
   sudo rsync -a --delete /build/python/${PYTHON_VERSION}/ /awips2/python/
   BUILDUSER=`whoami`
   sudo chown -R ${BUILDUSER}.fxalpha /awips2/python
   sudo chmod -R 777 /awips2/python
   sudo ln -sf ${WORKSPACE}/git/AWIPS2_build/installers/RPMs/python/scripts/profile.d/awips2Python.sh /etc/profile.d/awips2Python.sh
   source ${WORKSPACE}/git/AWIPS2_build/installers/RPMs/python/scripts/profile.d/awips2Python.sh
   python --version
else
   #DIR Not found! Lets build it.
   export RPMS=("buildRPM awips2-python")
   export LIB_ENV_BUILD_PACKAGE=awips2-python
   export LIB_ENV_BUILD_FOLDER=python
   export LIB_ENV_BUILD_VERSION=${PYTHON_VERSION}
fi
# Update the version decoder
sudo cp ${WORKSPACE}/git/AWIPS2_build/build/common/python_cached_versions.sh /build/python/
sudo chmod a+x /build/python/python_cached_versions.sh

##################################
# HDF5
##################################
HDF5_VERSION=$(getFOSSVersion hdf5)-$(getFOSSVersion szip)

function linkHDF5Version {
   sudo ln -sf /build/hdf5/${HDF5_VERSION} /awips2/hdf5
   sudo ln -sf ${WORKSPACE}/git/AWIPS2_build/installers/RPMs/hdf5/scripts/profile.d/awips2HDF5.sh /etc/profile.d/awips2HDF5.sh
   source ${WORKSPACE}/git/AWIPS2_build/installers/RPMs/hdf5/scripts/profile.d/awips2HDF5.sh
}

sudo rm -f /awips2/hdf5
if [ $? -ne 0 ]; then
   sudo rm -rf /awips2/hdf5
fi
if [ -d /build/hdf5/${HDF5_VERSION}/ ]; then
   linkHDF5Version
else
   #DIR Not found! Lets build it.
   export RPMS=("buildRPM awips2-hdf5")
   export LIB_ENV_BUILD_PACKAGE=awips2-hdf5
   export LIB_ENV_BUILD_FOLDER=hdf5
   export LIB_ENV_BUILD_VERSION=${HDF5_VERSION}
fi

##################################
# ANT
##################################
ANT_VERSION=$(getFOSSVersion ant)
sudo rm -f /awips2/ant
if [ $? -ne 0 ]; then
   sudo rm -rf /awips2/ant
fi
sudo rm -f /etc/profile.d/awips2Ant.sh
if [ $? -ne 0 ]; then
   sudo rm -rf /etc/profile.d/awips2Ant.sh
fi
if [ -d /build/ant/${ANT_VERSION}/ ]; then
   sudo ln -sf /build/ant/${ANT_VERSION}/ /awips2/ant
   sudo ln -sf ${WORKSPACE}/git/AWIPS2_build/installers/RPMs/ant/scripts/profile.d/awips2Ant.sh /etc/profile.d/awips2Ant.sh
   source ${WORKSPACE}/git/AWIPS2_build/installers/RPMs/ant/scripts/profile.d/awips2Ant.sh
   ant -version
else
   #DIR Not found! Lets build it.
   export RPMS=("buildRPM awips2-ant")
   export LIB_ENV_BUILD_PACKAGE=awips2-ant
   export LIB_ENV_BUILD_FOLDER=ant
   export LIB_ENV_BUILD_VERSION=${ANT_VERSION}
fi

##################################
# Maven
##################################
MAVEN_VERSION=$(getFOSSVersion maven)
sudo rm -f /awips2/maven
if [ $? -ne 0 ]; then
   sudo rm -rf /awips2/maven
fi
sudo rm -f /etc/profile.d/awips2Maven.sh
if [ $? -ne 0 ]; then
   sudo rm -rf /etc/profile.d/awips2Maven.sh
fi
if [ -d /build/maven/${MAVEN_VERSION}/ ]; then
   sudo ln -sf /build/maven/${MAVEN_VERSION}/ /awips2/maven
   sudo ln -sf ${WORKSPACE}/git/AWIPS2_build/installers/RPMs/maven/scripts/profile.d/awips2Maven.sh /etc/profile.d/awips2Maven.sh
   source ${WORKSPACE}/git/AWIPS2_build/installers/RPMs/maven/scripts/profile.d/awips2Maven.sh
   mvn -version
else
   #DIR Not found! Lets build it.
   export RPMS=("buildRPM awips2-maven")
   export LIB_ENV_BUILD_PACKAGE=awips2-maven
   export LIB_ENV_BUILD_FOLDER=maven
   export LIB_ENV_BUILD_VERSION=${MAVEN_VERSION}
fi

##################################
# Java
##################################
JAVA_VERSION=$(getFOSSVersion java)
sudo rm -f /awips2/java
if [ $? -ne 0 ]; then
   sudo rm -rf /awips2/java
fi
sudo rm -f /etc/profile.d/awips2Java.sh
if [ $? -ne 0 ]; then
   sudo rm -rf /etc/profile.d/awips2Java.sh
fi
if [ -d /build/java/${JAVA_VERSION}/ ]; then
   sudo ln -sf /build/java/${JAVA_VERSION} /awips2/java
   sudo ln -sf ${WORKSPACE}/git/AWIPS2_build/installers/RPMs/java/scripts/profile.d/awips2Java.sh /etc/profile.d/awips2Java.sh
   source ${WORKSPACE}/git/AWIPS2_build/installers/RPMs/java/scripts/profile.d/awips2Java.sh
   java -version
else
   #DIR Not found! Lets build it.
   export RPMS=("buildRPM awips2-java")
   export LIB_ENV_BUILD_PACKAGE=awips2-java
   export LIB_ENV_BUILD_FOLDER=java
   export LIB_ENV_BUILD_VERSION=${JAVA_VERSION}
fi

# Function to build Python RPMs and stage them.
#  Arg1 - Packages to build.
function buildPythonPackage {
   local VERSION=${1}

   # Update what we have so far in the build process.
   sudo rsync -a --delete /build/python/${VERSION}/ /awips2/python/
   BUILDUSER=`whoami`
   sudo chown -R ${BUILDUSER}.fxalpha /awips2/python
   sudo chmod -R 777 /awips2/python
   sudo ln -sf ${WORKSPACE}/git/AWIPS2_build/installers/RPMs/python/scripts/profile.d/awips2Python.sh /etc/profile.d/awips2Python.sh
   source ${WORKSPACE}/git/AWIPS2_build/installers/RPMs/python/scripts/profile.d/awips2Python.sh

   pushd . > /dev/null 2>&1
   cd ${WORKSPACE}/baseline/rpms/build/x86_64
   IFS=$'\n'
   for RPM in ${ENVRPMS[@]}; do
      /bin/bash build.sh -dev "buildRPM $RPM"
      if [ $? -ne 0 ]; then
         echo "ERROR: Could not build required python packages: $ENVRPMS!"
         return 1
      fi
   done
   popd > /dev/null 2>&1

   stagePythonRPMs $VERSION
   if [ $? -ne 0 ]; then
      echo "ERROR: Could not install required python packages: $ENVRPMS!"
      return 1
   fi
}

# Remove the Python cached directory if one of the packages failed. 
#  Arg1 - Python Version.
function failPythonInstall {
   local VERSION=${1}
   echo "ERROR: Python install failed, See log above for errors. Removing invalid cached version."
   sudo rm -rf /build/python/${VERSION}/
}

# Process the RPM just built for dependencies.
#  Arg1 - The primary build script to call back.
function processBuildEnv {
   local BUILDFILE=${1}
   local ORIG_RPMS=${2}

   stageRPM $LIB_ENV_BUILD_PACKAGE $LIB_ENV_BUILD_FOLDER $LIB_ENV_BUILD_VERSION
   if [ $? -ne 0 ]; then
      echo "ERROR: Could not install required package ${LIB_ENV_BUILD_PACKAGE}! See build logs for more details."
      failPythonInstall $LIB_ENV_BUILD_VERSION
      exit 1
   fi

   if [ $LIB_ENV_BUILD_PACKAGE = "awips2-python" ]; then
      linkHDF5Version
      export ENVRPMS=("awips2-python-setuptools")
      buildPythonPackage $LIB_ENV_BUILD_VERSION
      if [ $? -ne 0 ]; then
         failPythonInstall $LIB_ENV_BUILD_VERSION
         exit 1
      fi
      export ENVRPMS=("awips2-python-setuptools_scm" "awips2-python-shapely")
      buildPythonPackage $LIB_ENV_BUILD_VERSION
      if [ $? -ne 0 ]; then
         failPythonInstall $LIB_ENV_BUILD_VERSION
         exit 1
      fi
      export ENVRPMS=("awips2-python-setuptools_scm_git_archive")
      buildPythonPackage $LIB_ENV_BUILD_VERSION
      if [ $? -ne 0 ]; then
         failPythonInstall $LIB_ENV_BUILD_VERSION
         exit 1
      fi
      export ENVRPMS=("awips2-python-numpy" "awips2-python-six" "awips2-python-pkgconfig" "awips2-python-cython" "awips2-python-zc.lockfile" "awips2-python-contextlib2")
      buildPythonPackage $LIB_ENV_BUILD_VERSION
      if [ $? -ne 0 ]; then
         failPythonInstall $LIB_ENV_BUILD_VERSION
         exit 1
      fi
      export ENVRPMS=("awips2-python-thrift" "awips2-python-h5py" "awips2-python-dateutil" "awips2-python-pytz" "awips2-python-pyparsing" "awips2-python-cftime" "awips2-python-cycler" "awips2-python-kiwisolver" "awips2-python-backports-lru_cache" "awips2-python-more-itertools")
      buildPythonPackage $LIB_ENV_BUILD_VERSION
      if [ $? -ne 0 ]; then
         failPythonInstall $LIB_ENV_BUILD_VERSION
         exit 1
      fi
      export ENVRPMS=("awips2-python-cheroot" "awips2-python-jaraco.functools")
      buildPythonPackage $LIB_ENV_BUILD_VERSION
      if [ $? -ne 0 ]; then
         failPythonInstall $LIB_ENV_BUILD_VERSION
         exit 1
      fi
      export ENVRPMS=("awips2-python-tempora")
      buildPythonPackage $LIB_ENV_BUILD_VERSION
      if [ $? -ne 0 ]; then
         failPythonInstall $LIB_ENV_BUILD_VERSION
         exit 1
      fi
      export ENVRPMS=("awips2-python-portend" "awips2-python-funcsigs" "awips2-python-pbr")
      buildPythonPackage $LIB_ENV_BUILD_VERSION
      if [ $? -ne 0 ]; then
         failPythonInstall $LIB_ENV_BUILD_VERSION
         exit 1
      fi
      export ENVRPMS=("awips2-python-matplotlib" "awips2-python-mock" "awips2-python-numexpr")
      buildPythonPackage $LIB_ENV_BUILD_VERSION
      if [ $? -ne 0 ]; then
         failPythonInstall $LIB_ENV_BUILD_VERSION
         exit 1
      fi
      if [ ! -z "$LOCAL_APPS_FOSS_BRANCH" ]; then
         export ENVRPMS=("awips2-python-pycairo")
         buildPythonPackage $LIB_ENV_BUILD_VERSION
         if [ $? -ne 0 ]; then
            failPythonInstall $LIB_ENV_BUILD_VERSION
            exit 1
         fi
         export ENVRPMS=("awips2-python-pygobject")
         buildPythonPackage $LIB_ENV_BUILD_VERSION
         if [ $? -ne 0 ]; then
            failPythonInstall $LIB_ENV_BUILD_VERSION
            exit 1
         fi
      fi
   fi

   # Make the original build request now that we have the required deps installed.
   unset RPMS
   export RPMS=${ORIG_RPMS}
   unset LIB_ENV_BUILD_PACKAGE
   unset LIB_ENV_BUILD_FOLDER
   unset LIB_ENV_BUILD_VERSION
   $BUILDFILE
   exit $?
}


# Extract the contents of an RPM and install it into the build 
# staging area for use.
#  Arg1 - The package to stage.
#  Arg2 - The package folder.
#  Arg3 - The package version.
function stageRPM {
   local PACKAGE=${1}
   local FOLDER=${2}
   local VERSION=${3}

   pushd . > /dev/null 2>&1
   local BUILD_TMP=/tmp/build.rpmstage/
   mkdir -p $BUILD_TMP
   if [ $? -ne 0 ]; then
      return 1
   fi
   cd $BUILD_TMP
   local RPMLIST=`ls ${WORKSPACE}/rpmbuild/RPMS/*/${PACKAGE}-{devel-,}[0-9]*.rpm`
   if [ $? -ne 0 ]; then
      return 1
   fi

   for RPM in $RPMLIST; do
      rpm2cpio $RPM | cpio -idmv
      if [ $? -ne 0 ]; then
         return 1
      fi
   done
   sudo mkdir -p /build/${FOLDER}/${VERSION}
   if [ $? -ne 0 ]; then
      return 1
   fi
   sudo cp -r awips2/${FOLDER}/* /build/${FOLDER}/${VERSION}/
   if [ $? -ne 0 ]; then
      return 1
   fi

   # Install RPM Record only.
   sudo rpm -ivh --justdb $RPMLIST
   if [ $? -ne 0 ]; then
      # Attempt to install one more time before failing...
      # Remove the links so cached files are not removed.
      find -L /awips2 -maxdepth 1 -xtype l -exec sudo rm -vf {} \;
      # Remove the package (* is to remove the additional Python packages)
      sudo yum remove ${PACKAGE}\* -y
      # Try the install again
      sudo rpm -ivh --justdb $RPMLIST
      if [ $? -ne 0 ]; then
         return 1
      fi
   fi
   sudo rm -f $RPMLIST
   popd > /dev/null 2>&1
   rm -rf $BUILD_TMP
   return 0
}

# Extract the contents of an RPM and install it into the build 
# staging area for use.
#  Arg1 - Python Version.
function stagePythonRPMs {
   local VERSION=${1}

   pushd . > /dev/null 2>&1
   local BUILD_TMP=/tmp/build.rpmstage/
   mkdir -p $BUILD_TMP
   if [ $? -ne 0 ]; then
      return 1
   fi
   cd $BUILD_TMP
   local RPMLIST=`ls ${WORKSPACE}/rpmbuild/RPMS/*/awips2-python-*.rpm`
   if [ $? -ne 0 ]; then
      return 1
   fi
   for RPM in $RPMLIST; do
      rpm2cpio $RPM | cpio -idmv
      if [ $? -ne 0 ]; then
         return 1
      fi
      # Install RPM Record only.
      sudo rpm -ivh --justdb $RPM
      if [ $? -ne 0 ]; then
         return 1
      fi
      sudo rm -f $RPM
   done
   sudo cp -r awips2/python/* /build/python/${VERSION}/
   if [ $? -ne 0 ]; then
      return 1
   fi
   popd > /dev/null 2>&1
   rm -rf $BUILD_TMP
   return 0
}

