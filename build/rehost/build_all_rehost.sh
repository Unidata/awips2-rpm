#!/bin/bash

#
# This script expects to be run from inside the build container. It attempts to
# build all the rehost git repositories.
#
# SCRIPT HISTORY
#
# Date          Ticket#  Engineer    Description
# ------------- -------- ----------- -----------------------------
# Dec 09, 2021  8404     njensen     Initial creation
# Feb 02, 2022  8763     njensen     Added rehost-laps-msas
# Feb 09, 2022  8769     njensen     Disable rehost-laps-msas as the code has
#                                    been consolidated into rehost-wfoa
# Jun 13, 2023  2029637  njensen     Require env var REHOST_BRANCH to be set
# Jun 27, 2023  2034286  njensen     Rename rehost-ohd repo to AWIPS2_Rehost_OHD
#

if [[ -z "${GIT_REPOS_DIR}" ]]; then
    export GIT_REPOS_DIR=/home/build/git
fi

if [[ -z "${WORKSPACE}" ]]; then
    export WORKSPACE=/home/build/rehost-workspace
fi

if [[ -z "${REHOST_BRANCH}" ]]; then
   echo "Environment variable REHOST_BRANCH must be set to the branch you'd like to build."
   exit 1
fi

"${GIT_REPOS_DIR}"/AWIPS2_build/build/rehost/install_a2_dependencies.sh
if [ $? -ne 0 ]; then
   echo "Failed to install required awips2 RPMs"
   exit 1
fi

mkdir --parents ${WORKSPACE}

# rehost-wfoa must be built before rehost-ldad
"${GIT_REPOS_DIR}"/rehost-wfoa/build.sh
if [ $? -ne 0 ]; then
   echo "Failed to build rehost-wfoa"
   exit 1
fi

# build rehost adapt after rehost wfoa
"${GIT_REPOS_DIR}"/rehost-adapt/build.sh
if [ $? -ne 0 ]; then
   echo "Failed to build rehost-adapt"
   exit 1
fi


"${GIT_REPOS_DIR}"/rehost-ldad/build.sh
if [ $? -ne 0 ]; then
   echo "Failed to build rehost-ldad"
   exit 1
fi

#"${GIT_REPOS_DIR}"/rehost-laps-msas/build.sh
#if [ $? -ne 0 ]; then
#   echo "Failed to build rehost-laps-msas"
#   exit 1
#fi

"${GIT_REPOS_DIR}"/rehost-ncf-comms/build.sh
if [ $? -ne 0 ]; then
   echo "Failed to build rehost-ncf-comms"
   exit 1
fi

"${GIT_REPOS_DIR}"/AWIPS2_Rehost_OHD/build/build.sh
if [ $? -ne 0 ]; then
   echo "Failed to build AWIPS2_Rehost_OHD"
   exit 1
fi

