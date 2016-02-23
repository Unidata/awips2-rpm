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
# Select Build Style (Continuous or Nightly Build)
# Nightly RPMS=
# Continuous RPMS=("buildRPM awips2-common-base" "buildRPM awips2" "buildCAVE" "buildEDEX" "buildRPM awips2-alertviz")
#
# Select Git Repositories to use:
# Enable  (GIT_REPO)_BRANCH=VERSION
# Disable (GIT_REPO)_BRANCH=
#
# Sync the RPMs to a central repository:
# Enable   SYNC_DEST=/install/repository/${AWIPSII_BRANCH}-x86_64-RHEL6
# Disable  SYNC_DEST=
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

# Set the repository directory.
repo_dir=$WORKSPACE/git

##################################
# Setup the build environment
##################################
source $repo_dir/AWIPS2_build/build/common/SetupEnvironment.sh

##################################
# Create empty, expected directories due to git limitations.
##################################
$repo_dir/AWIPS2_build/build/common/createEmptyBuildDirectories.sh

$repo_dir/AWIPS2_build/build/common/makeRPMBuildStructure.sh
if [ $? -ne 0 ]; then
   exit 1
fi

##################################
# sync repos to baseline directory
##################################
repo=$repo_dir/AWIPS2_baseline
parts_to_sync=( 'build/*' 'RadarServer/*' 'edexOsgi/*' 'cave/*' 'localization/*' \
   'javaUtilities/*' 'rpms' 'pythonPackages' 'nativeLib/*' 'ost/*' 'crh/*')
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

repo=$repo_dir/AWIPS2_build
parts_to_sync=( 'foss' 'installers')
$repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $BUILD_BRANCH $baseline ${parts_to_sync[*]}
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
# Sync the Hazard Services Repo
##################################
if [ ! -z "$HAZARD_SERVICES_BRANCH" ]; then
   repo=$repo_dir/18-Hazard_Services
   parts_to_sync=( 'common/*' 'edex/*' 'viz/*' 'tools')
   $repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $HAZARD_SERVICES_BRANCH $baseline ${parts_to_sync[*]}
   if [ $? -ne 0 ]; then
      exit 1
   fi
   ##################################
   # Create properties file for Hazard Services
   ##################################
   echo "gov.noaa.gsd.viz.hazards.feature" >> ${WORKSPACE}/baseline/build/features.txt
   echo "com.raytheon.uf.edex.hazards.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt
fi

##################################
# Sync the 13.3 GEOS-R Repo
##################################
if [ ! -z "$GOES_R_BRANCH" ]; then
   repo=$repo_dir/13.3-GOES-R
   parts_to_sync=( 'cave/*' 'cots/*' 'edexOsgi/*')
   $repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $GOES_R_BRANCH $baseline ${parts_to_sync[*]}
   if [ $? -ne 0 ]; then
      exit 1
   fi
   ##################################
   # Create properties file for GOES-R
   ##################################
   echo "com.raytheon.uf.viz.satellite.goesr.feature" >> ${WORKSPACE}/baseline/build/features.txt
   echo "com.raytheon.uf.edex.goesr.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt
fi

##################################
# Sync the BMH Repo
##################################
if [ ! -z "$BMH_BRANCH" ]; then
   repo=$repo_dir/BMH
   parts_to_sync=( 'cave/*' 'common/*' 'cots/*' 'edex/*' 'features/*' 'foss/*' 'rpms-BMH' 'test/*' )
   $repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $BMH_BRANCH $baseline ${parts_to_sync[*]}
   if [ $? -ne 0 ]; then
      exit 1
   fi
   ##################################
   # Create properties file for BMH
   ##################################
   echo "com.raytheon.uf.viz.bmh.feature" >> ${WORKSPACE}/baseline/build/features.txt
   echo "com.raytheon.uf.common.bmh.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt
   echo "com.raytheon.uf.edex.bmh.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt
   echo "com.raytheon.uf.edex.request.bmh.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt
fi

##################################
# Sync the BMH_cots Repo
##################################
if [ ! -z "$BMH_COTS_BRANCH" ]; then
   repo=$repo_dir/BMH_cots
   parts_to_sync=( 'neospeech' 'foss' )
   $repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $BMH_COTS_BRANCH $baseline ${parts_to_sync[*]}
   if [ $? -ne 0 ]; then
      exit 1
   fi
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

##################################
# Sync the AWIPS2 GSD Repo
##################################
if [ ! -z "$GSD_BRANCH" ]; then
   repo=$repo_dir/AWIPS2_GSD
   parts_to_sync=( 'features/*' 'viz/*')
   $repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $GSD_BRANCH $baseline ${parts_to_sync[*]}
   if [ $? -ne 0 ]; then
      exit 1
   fi
   ##################################
   # Create properties file for GSD
   ##################################
   echo "gov.noaa.gsd.viz.ensemble.feature" >> ${WORKSPACE}/baseline/build/features.txt
fi

##################################
# Sync the X Band Radar Repo
##################################
if [ ! -z "$X_BAND_RADAR_BRANCH" ]; then
   repo=$repo_dir/X-Band_Radar
   parts_to_sync=( 'cave/*' 'edexOsgi/*')
   $repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $X_BAND_RADAR_BRANCH $baseline ${parts_to_sync[*]}
   if [ $? -ne 0 ]; then
      exit 1
   fi
   ##################################
   # Create properties file for X-Band-Radar
   ##################################
   echo "com.raytheon.uf.viz.dataplugin.nswrc.feature" >> ${WORKSPACE}/baseline/build/features.txt
   echo "com.raytheon.uf.edex.nswrc.radar.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt
fi

##################################
# Sync the AWIPS2 CIMSS Repo
##################################
if [ ! -z "$CIMSS_BRANCH" ]; then
   repo=$repo_dir/AWIPS2_CIMSS
   parts_to_sync=( 'common/*' 'edex/*' 'features/*' 'viz/*')
   $repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $CIMSS_BRANCH $baseline ${parts_to_sync[*]}
   if [ $? -ne 0 ]; then
      exit 1
   fi
   ##################################
   # Create properties file for CIMSS
   ##################################
   echo "edu.wisc.ssec.cimss.viz.convectprob.feature" >> ${WORKSPACE}/baseline/build/features.txt
   echo "edu.wisc.ssec.cimss.edex.convectprob.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt
fi

##################################
# Sync the Collaboration Repo
##################################
if [ ! -z "$COLLABORATION_BRANCH" ]; then
   repo=$repo_dir/Collaboration
   parts_to_sync=( 'viz/*' 'features/*' 'common/*' 'openfire/*' 'rpms-Collaboration' 'foss')
   $repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $COLLABORATION_BRANCH $baseline ${parts_to_sync[*]}
   if [ $? -ne 0 ]; then
      exit 1
   fi
   ##################################
   # Create properties file for Collaboration
   ##################################
   echo "com.raytheon.uf.viz.collaboration.feature" >> ${WORKSPACE}/baseline/build/features.txt
fi

##################################
# Sync the Data Delivery Repo
##################################
if [ ! -z "$DATA_DELIVERY_BRANCH" ]; then
   repo=$repo_dir/Data_Delivery
   parts_to_sync=( 'common/*' 'edex/*' 'features/*' 'viz/*')
   $repo_dir/AWIPS2_build/build/common/sync_workspace.sh $repo $DATA_DELIVERY_BRANCH $baseline ${parts_to_sync[*]}
   if [ $? -ne 0 ]; then
      exit 1
   fi
   ##################################
   # Add properties for datadelivery
   ##################################
   echo "com.raytheon.uf.viz.datadelivery.feature" >> ${WORKSPACE}/baseline/build/features.txt
   echo "com.raytheon.uf.edex.datadelivery.client.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt
   echo "com.raytheon.uf.edex.datadelivery.core.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt
   echo "com.raytheon.uf.edex.datadelivery.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt
   echo "com.raytheon.uf.edex.dataprovideragent.feature" >> ${WORKSPACE}/baseline/build.edex/features.txt
fi

export _component_release=$BUILD_NUMBER
export _component_version=$AWIPSII_VERSION

##################################
# Build the rpms.
##################################

##################################
# Set Build Envrionment Variables
##################################
$repo_dir/AWIPS2_build/build/common/setup_build_environment.sh

##################################
# Allow execution of the cave rpm build build.sh script.
##################################
cd ${WORKSPACE}/baseline/rpms/build/x86_64
chmod a+x build.sh
if [ $? -ne 0 ]; then
   exit 1
fi

##################################
# Continuous or Nightly Build
##################################
if [ ! -z "$RPMS" ]; then
   IFS=$'\n'
   for RPM in ${RPMS[@]}; do
      /bin/bash build.sh -dev $RPM
      if [ $? -ne 0 ]; then
         exit 1
      fi
   done

   # Return back to SetupEnvironment.sh if building dependant packages
   if [ ! -z "$LIB_ENV_BUILD_PACKAGE" ]; then
      processBuildEnv ${WORKSPACE}/git/AWIPS2_build/build/linux/build.sh
      if [ $? -ne 0 ]; then
         exit 1
      fi
   fi
else
   /bin/bash build.sh -rh6
   if [ $? -ne 0 ]; then
      exit 1
   fi
   /bin/bash build.sh -WA
   if [ $? -ne 0 ]; then
      exit 1
   fi
   ##################################
   # Actions for the Omaha Build
   ##################################
   if [ $AWIPSII_BUILD_SITE = "Raytheon Omaha" ]; then
      ##################################
      # Add revision info
      ##################################
      pushd .
      cd $WORKSPACE/rpmbuild/RPMS/
      export http_proxy=
      export HTTP_PROXY=
      curl -s "$BUILD_URL/api/xml?wrapper=changes&xpath=//changeSet//comment" \
         | sed -e 's/<\/comment>//g; s/<comment>//g; s/<\/*changes>//g' \
         | grep  -G '^.*#[0-9]' \
         | awk '{print $1" "$2}' \
         | sed ':a;N;$!ba;s/\n/, /g' > $WORKSPACE/rpmbuild/RPMS/build_log
      find . -type f -iname "awips2-1*" -exec rpmrebuild -d /tmp/rebuilt -vnp --change-spec-description="cat $WORKSPACE/rpmbuild/RPMS/build_log" {} \;
      find . -type f -iname "awips2-1*" -exec mv -v {} {}.orig \;
      find /tmp/rebuilt/ -iname "awips2-1*" -exec mv -v {} noarch/ \;
      rm $WORKSPACE/rpmbuild/RPMS/build_log
      popd
   fi
fi

##################################
# Install the rpms in the repo
##################################
if [ ! -z "$SYNC_DEST" ]; then
   $repo_dir/AWIPS2_build/build/common/build_install_rpms.sh ${SYNC_DEST}
   # Cleanup the rpmbuild directory after we copy over the RPMs.
   sudo rm -rf ${WORKSPACE}/rpmbuild
   sudo rm -rf ${WORKSPACE}/eclipse-repo
fi

# Cleanup the baseline directory
sudo rm -rf ${WORKSPACE}/baseline

