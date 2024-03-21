#!/bin/bash
#
# This script will verify that the necessary environment variables are set for
# the rehost build.
#
# SCRIPT HISTORY
#
# Date          Ticket#  Engineer    Description
# ------------- -------- ----------- -----------------------------
# Dec 15, 2021  8404     njensen     Initial creation
#

set -x

if [[ -z "${REHOST_BRANCH}" ]]; then
   echo "Environment variable REHOST_BRANCH must be set to the branch you'd like to build."
   exit 1
fi

if [[ -z "${WORKSPACE}" ]]; then
   echo "Environment variable WORKSPACE must be set to the directory you want to run the build in."
   exit 1
fi

if [[ -z "${GIT_REPOS_DIR}" ]]; then
   echo "Environment variable GIT_REPOS_DIR must be set to the directory containing the git repositories."
   exit 1
fi

