# Default env.sh for developer builds
#
#    Date          Ticket#   Engineer     Description
#    ------------  --------  -----------  -------------------------------------
#    Aug 03, 2022  8794      sharbison    Initial copy of build container
#                                         scripts from dev_rhel8, to be
#                                         converted to rhel7.
#

# Don't change these ##########################################################
export AWIPSII_RELEASE=
export AWIPSII_VERSION=50.1.1
export AWIPSII_BUILD_SITE="Development"
export SYNC_DEST=
export WINDOWS_STAGING=
export A2LIBS=true
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"
export NO_MODIFY_GIT_REPOS=1
export WORKSPACE=/home/build/workspace
# The value of this variable is not used for developer builds. You do not need
# to change it regardless of what branch you are working on.
export AWIPSII_BRANCH=dev
###############################################################################

# Uncomment the repos which you want to include in the build
export UFCORE_BRANCH=$AWIPSII_BRANCH
export UFCORE_FOSS_BRANCH=$AWIPSII_BRANCH
export FOSS_BRANCH=$AWIPSII_BRANCH
export BUILD_BRANCH=$AWIPSII_BRANCH
export STATIC_BRANCH=$AWIPSII_BRANCH
export NCEP_BRANCH=$AWIPSII_BRANCH
export NWS_BRANCH=$AWIPSII_BRANCH
#export OGC_BRANCH=$AWIPSII_BRANCH
#export HAZARD_SERVICES_BRANCH=$AWIPSII_BRANCH
#export GOES_R_BRANCH=$AWIPSII_BRANCH
#export BMH_BRANCH=$AWIPSII_BRANCH
#export BMH_COTS_BRANCH=$AWIPSII_BRANCH
#export OHD_BRANCH=$AWIPSII_BRANCH
#export GSD_BRANCH=$AWIPSII_BRANCH
#export CIMSS_BRANCH=$AWIPSII_BRANCH
#export COLLABORATION_BRANCH=$AWIPSII_BRANCH
#export DATA_DELIVERY_BRANCH=$AWIPSII_BRANCH
#export NATIVELIB_BRANCH=$AWIPSII_BRANCH
#export RADARSERVER_BRANCH=$AWIPSII_BRANCH
#export METEOGRAM_BRANCH=$AWIPSII_BRANCH
#export BOUNDARY_BRANCH=$AWIPSII_BRANCH
#export NASA_SPORT_BRANCH=$AWIPSII_BRANCH
#export LOCAL_APPS_FOSS_BRANCH=$AWIPSII_BRANCH
#export IRT_BRANCH=$AWIPSII_BRANCH


# Example for building a single RPM package
#export RPMS="buildRPM awips2-postgresql"

# Example for building multiple RPM packages.
#export RPMS="buildRPM awips2-hdf5
#buildRPM awips2-netcdf
#buildRPM awips2-python"

# If RPMS is empty, all packages will be built
export RPMS=

