#!/bin/bash

#
# This script will sync over enabled GIT repos. Ordering of the 
# repos in this file is strict, build order is determined by this
# order. This script also handles the full and continuous builds.
#
# SCRIPT HISTORY
#
# Date          Ticket#  Engineer    Description
# ------------- -------- ----------- -----------------------------
# Mar 10, 2016  4734     dlovely     Initial creation

####################################################################
# Usage
####################################################################
# Select Git Repositories to use:
# Enable  (GIT_REPO)_BRANCH=VERSION
# Disable (GIT_REPO)_BRANCH=
#
# Sync the Zip to a central staging area:
# Enable   WINDOWS_STAGING=/home/jenkins/staging/win32-nightly
# Disable  WINDOWS_STAGING=
####################################################################

##################################
# Create workspace directory
##################################
cd ${WORKSPACE}
if [ $? -ne 0 ]; then
   exit 1
fi
if [ -d baseline ]; then
   rm -rf baseline
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi

# Set baseline directory.
baseline=${WORKSPACE}/baseline
mkdir $baseline

if [ -d win64-build ]; then
   rm -rf win64-build
fi
mkdir win64-build

# Set the repository directory.
repo_dir=$WORKSPACE/git

##################################
# Setup the build environment
##################################
$repo_dir/AWIPS2_build/build/common/SetupEnvironment.sh

# Check if all the environment packages are available.
if [ ! -z "$LIB_ENV_BUILD_PACKAGE" ]; then
   echo "ERROR: Missing Environment Package: ${LIB_ENV_BUILD_PACKAGE}!"
   echo " Run the standard Linux build to complete the required build environment."
   exit 1
fi

##################################
# sync repos to baseline directory
##################################
repo=$repo_dir/AWIPS2_baseline
parts_to_sync=( 'RadarServer/*' 'edexOsgi/*' 'cave/*' 'localization/*' 'rpms' )
$repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $AWIPSII_BRANCH $baseline ${parts_to_sync[*]}
if [ $? -ne 0 ]; then
   exit 1
fi

##################################
# Setup properties file for build
##################################
if [ "$(tail -c1 ${WORKSPACE}/baseline/build/features.txt; echo x)" != $'\nx' ]; then
   echo "" >> ${WORKSPACE}/baseline/build/features.txt
fi

touch ${WORKSPACE}/baseline/build.edex/features.txt

repo=$repo_dir/ufcore
parts_to_sync=( 'common/*' 'edex/*' 'features/*' 'viz/*' )
$repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $UFCORE_BRANCH $baseline ${parts_to_sync[*]}
if [ $? -ne 0 ]; then
   exit 1
fi

repo=$repo_dir/ufcore-foss
parts_to_sync=( 'lib/*' )
$repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $UFCORE_FOSS_BRANCH $baseline ${parts_to_sync[*]}
if [ $? -ne 0 ]; then
   exit 1
fi

repo=$repo_dir/AWIPS2_foss
parts_to_sync=( 'lib/*' )
$repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $FOSS_BRANCH $baseline ${parts_to_sync[*]}
if [ $? -ne 0 ]; then
   exit 1
fi

##################################
# Sync the AWIPS2 NWS Repo
##################################
if [ ! -z "$NWS_BRANCH" ]; then
   repo=$repo_dir/AWIPS2_NWS
   parts_to_sync=( 'common/*' 'edex/*' 'features/*')
   $repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $NWS_BRANCH $baseline ${parts_to_sync[*]}
   if [ $? -ne 0 ]; then
      exit 1
   fi

   ##################################
   # Create properties file for CRH
   ##################################
   echo "gov.noaa.nws.crh.edex.grib.decoderpostprocessor.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt

   ##################################
   # Create properties file for Binlightning
   ##################################
   echo "com.raytheon.uf.edex.binlightning.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt

   ##################################
   # Create properties file for OST
   ##################################
   echo "com.raytheon.uf.edex.ost.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt

   ##################################
   # Create properties file for MPING
   ##################################
   echo "gov.noaa.nws.sr.oun.edex.mping.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt
fi

##################################
# Sync the AWIPS2 NCEP Repo
##################################
if [ ! -z "$NCEP_BRANCH" ]; then
   repo=$repo_dir/AWIPS2_NCEP
   parts_to_sync=( 'common/*' 'edex/*' 'features/*' 'viz/*')
   $repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $NCEP_BRANCH $baseline ${parts_to_sync[*]}
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi

##################################
# Sync the OGC Repo
##################################
if [ ! -z "$OGC_BRANCH" ]; then
   repo=$repo_dir/OGC
   parts_to_sync=( 'edex/*' 'foss/*' 'features/*')
   $repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $OGC_BRANCH $baseline ${parts_to_sync[*]}
   if [ $? -ne 0 ]; then
      exit 1
   fi
   ##################################
   # Create properties file for OGC
   ##################################
   echo "com.raytheon.uf.edex.ogc.core.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt
   echo "com.raytheon.uf.edex.ogc.wfs.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt
fi

##################################
# Sync the OHD Repo
##################################
if [ ! -z "$OHD_BRANCH" ]; then
   repo=$repo_dir/OHD
   parts_to_sync=( 'lib/*' 'edex/*' 'features/*' )
   $repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $OHD_BRANCH $baseline ${parts_to_sync[*]}
   if [ $? -ne 0 ]; then
      exit 1
   fi
   rsync -a $repo/apps/ $baseline/hydro/
   if [ $? -ne 0 ]; then
      exit 1
   fi
   ##################################
   # Create properties file for OHD
   ##################################
   echo "com.raytheon.uf.viz.ohd.feature" >> ${WORKSPACE}/baseline/build/features.txt
   echo "com.raytheon.uf.edex.ohd.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt
fi

# Determine the Build Date
export BUILD_DATE=`date +"%Y%m%d"`
# Set the release to the date if empty.
if [ "${AWIPSII_RELEASE}" = "" ]; then
    AWIPSII_RELEASE=$BUILD_DATE
fi

##################################
# Add build information for tracking
##################################
if [ $AWIPSII_BUILD_SITE = "Raytheon Omaha" ]; then
   # Update the CAVE about dialog.
   BUILD_TIME=`date +"%T %Z"`
   pushd .
   cd ${WORKSPACE}/baseline/com.raytheon.viz.product.awips
   echo "caveVersion=${AWIPSII_VERSION}-${AWIPSII_RELEASE}" > plugin.properties
   echo "caveAboutText=Common AWIPS Visualization Environment (CAVE) x64\\n\\" >> plugin.properties
   echo "\\n\\" >> plugin.properties
   echo "Developed on the Raytheon Visualization Environment (viz)\\n\\" >> plugin.properties
   echo "\\tBUILD VERSION: ${AWIPSII_VERSION}\\n\\" >> plugin.properties
   echo "\\tBUILD DATE: ${BUILD_DATE}\\n\\" >> plugin.properties
   echo "\\tBUILD TIME: ${BUILD_TIME}\\n\\" >> plugin.properties
   echo "\\tBUILD SITE: ${AWIPSII_BUILD_SITE}\\n\\" >> plugin.properties
   echo "\\n\\" >> plugin.properties
   echo "Designed for Microsoft Windows 7\\n\\" >> plugin.properties
   echo "\\n\\" >> plugin.properties
   echo "Changes: \\" >> plugin.properties
   http_proxy= curl -s "$BUILD_URL/api/xml?wrapper=changes&xpath=//changeSet//comment" | sed -e 's/<\/comment>//g; s/<comment>//g; s/<\/*changes>//g' | grep  -G '^.*#[0-9]'|awk '{print $1" "$2}' | sed ':a;N;$!ba;s/\n/, /g' >> plugin.properties
   popd
fi

##################################
# Copy all the plugins to CAVE build dir
##################################
baseline=${WORKSPACE}/baseline
pluginsToCopy=( 'com.*' 'ucar.*' 'org.*' 'net.*' 'ohd.*' 'javax.*' 'gov.*' 'edu.*' 'ogc.*' 'de.*' 'ch.*' )
mkdir -p ${baseline}/build/cave/tmp/plugins
for plugin in ${pluginsToCopy[*]};
   do cp -rv ${baseline}/${plugin} ${baseline}/build/cave/tmp/plugins/
done
mkdir -p ${baseline}/build/cave/tmp/features
cp -rv ${baseline}/*.feature* ${baseline}/build/cave/tmp/features/

##################################
# Build Thinclient
##################################
/awips2/ant/bin/ant -f baseline/build/build.xml \
-Dbuild.product=${WORKSPACE}/baseline/com.raytheon.viz.product.awips/thinclient.product \
-Dbuild.os=win32 \
-Dbuild.ws=win32 \
-Dbuild.arch=x86_64 \
-Declipse.dir=/awips2/eclipse \
-Ddestination.dir=${WORKSPACE}/win64-build \
cave
if [ $? -ne 0 ]; then
   exit 1
fi

##################################
# Copy CAVE to Staging dir
##################################
if [ ! -z "$WINDOWS_STAGING" ]; then
   pushd . > /dev/null 2>&1
   cd ${WORKSPACE}/win64-build
   _zip_filename=CAVE-${AWIPSII_VERSION}-${JOB_NAME}-${BUILD_NUMBER}.zip
   rm -f ${WINDOWS_STAGING}/${_zip_filename}
   mv CAVE-win32.win32.x86_64.zip ${WINDOWS_STAGING}/${_zip_filename}
   popd > /dev/null 2>&1
fi

##################################
# Cleanup the baseline directory
##################################
sudo rm -rf ${WORKSPACE}/baseline

