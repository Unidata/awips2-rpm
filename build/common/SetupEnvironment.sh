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

#Save the previous build state
LIB_ENV_BUILD_RPMS=$RPMS

# Finds the version of a given FOSS pacakge.
#  Arg1 - The FOSS Package.
function getFOSSVersion {
   local FOSSPACKAGE=${1}

   local DIR=`ls -d ${WORKSPACE}/git/AWIPS2_build/foss/${FOSSPACKAGE}-[0-9]*`
   echo ${DIR##*-}
}

##################################
# QPID
##################################
QPID_VERSION=$(getFOSSVersion qpid-lib)
sudo rm -f /awips2/qpid
if [ $? -ne 0 ]; then
   sudo rm -rf /awips2/qpid
fi
if [ -d /build/qpid/${QPID_VERSION}/ ]; then
   sudo ln -sf /build/qpid/${QPID_VERSION} /awips2/qpid
else
   #DIR Not found! Lets build it.
   export RPMS=("buildRPM awips2-qpid-lib")
   export LIB_ENV_BUILD_PACKAGE=awips2-qpid-lib
   export LIB_ENV_BUILD_FOLDER=qpid
   export LIB_ENV_BUILD_VERSION=${QPID_VERSION}
fi

##################################
# Python
##################################
# Keep track of all the version combinations we could have with the pre-installed Python packages.
PYTHON_VERSION=$(getFOSSVersion python)-$(getFOSSVersion nose)-$(getFOSSVersion numpy)-$(getFOSSVersion setuptools)-$(getFOSSVersion thrift)-$(getFOSSVersion h5py)-$(getFOSSVersion python-dateutil)-$(getFOSSVersion pytz)-$(getFOSSVersion six)-$(getFOSSVersion pyparsing)

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
# Check if the version decoder is already installed, if not install it.
if [ ! -f /build/python/python_cached_versions.sh ]; then
   sudo cp ${WORKSPACE}/git/AWIPS2_build/build/common/python_cached_versions.sh /build/python/
   sudo a+x /build/python/python_cached_versions.sh
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
if [ -d /build/postgresql/${POSTGRESQL_VERSION}/ ]; then
   sudo ln -sf /build/postgresql/${POSTGRESQL_VERSION} /awips2/postgresql
else
   #DIR Not found! Lets build it.
   export RPMS=("buildRPM awips2-postgresql")
   export LIB_ENV_BUILD_PACKAGE=awips2-postgresql
   export LIB_ENV_BUILD_FOLDER=postgresql
   export LIB_ENV_BUILD_VERSION=${POSTGRESQL_VERSION}
fi

##################################
# Java
##################################
JAVA_VERSION=`ls -d ${WORKSPACE}/git/AWIPS2_build/foss/java-*/src/x86_64/jdk*`
JAVA_VERSION=${JAVA_VERSION##*jdk-}
JAVA_VERSION=${JAVA_VERSION%%-*}
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

# Process the RPM just built for dependancies.
#  Arg1 - The primary build script to call back.
function processBuildEnv {
   local BUILDFILE=${1}

   stageRPM $LIB_ENV_BUILD_PACKAGE $LIB_ENV_BUILD_FOLDER $LIB_ENV_BUILD_VERSION
   if [ $? -ne 0 ]; then
      echo "ERROR: Could not install required package ${LIB_ENV_BUILD_PACKAGE}! See build logs for more details."
      failPythonInstall $LIB_ENV_BUILD_VERSION
      exit 1
   fi

   if [ $LIB_ENV_BUILD_PACKAGE = "awips2-python" ]; then
      export ENVRPMS=("awips2-python-nose" "awips2-python-setuptools")
      buildPythonPackage $LIB_ENV_BUILD_VERSION
      if [ $? -ne 0 ]; then
         failPythonInstall $LIB_ENV_BUILD_VERSION
         exit 1
      fi
      export ENVRPMS=("awips2-python-numpy" "awips2-python-six")
      buildPythonPackage $LIB_ENV_BUILD_VERSION
      if [ $? -ne 0 ]; then
         failPythonInstall $LIB_ENV_BUILD_VERSION
         exit 1
      fi
      export ENVRPMS=("awips2-python-thrift" "awips2-python-h5py" "awips2-python-dateutil" "awips2-python-pytz" "awips2-python-pyparsing" )
      buildPythonPackage $LIB_ENV_BUILD_VERSION
      if [ $? -ne 0 ]; then
         failPythonInstall $LIB_ENV_BUILD_VERSION
         exit 1
      fi
   fi

   # Make the original build request now that we have the required deps installed.
   export RPMS=$LIB_ENV_BUILD_RPMS
   unset LIB_ENV_BUILD_PACKAGE
   unset LIB_ENV_BUILD_FOLDER
   unset LIB_ENV_BUILD_VERSION
   unset LIB_ENV_BUILD_RPMS
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
   local RPM=`ls ${WORKSPACE}/rpmbuild/RPMS/*/${PACKAGE}-[0-9]*.rpm`
   if [ $? -ne 0 ]; then
      return 1
   fi
   rpm2cpio $RPM | cpio -idmv
   if [ $? -ne 0 ]; then
      return 1
   fi
   sudo mkdir -p /build/${FOLDER}/${VERSION}
   if [ $? -ne 0 ]; then
      return 1
   fi
   sudo cp -r awips2/${FOLDER}/* /build/${FOLDER}/${VERSION}/
   if [ $? -ne 0 ]; then
      return 1
   fi

   # Install RPM Record only.
   sudo rpm -ivh --justdb $RPM

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
      sudo rm -rf $RPM
   done
   sudo cp -r awips2/python/* /build/python/${VERSION}/
   if [ $? -ne 0 ]; then
      return 1
   fi
   popd > /dev/null 2>&1
   rm -rf $BUILD_TMP
   return 0
}

