#!/bin/bash -x

#
# Sets the build version. 
#
# SCRIPT HISTORY
#
# Date          Ticket#  Engineer    Description
# ------------- -------- ----------- -----------------------------
# Mar 10, 2016  4734     dlovely     Initial import from awipscm

export _architecture=`uname -i`

# Determine the version
if [ "${AWIPSII_VERSION}" = "" ]; then
   export AWIPSII_VERSION=`date +'%y.%-m.0'`
fi

echo AWIPSII_VERSION is: ${AWIPSII_VERSION}

# Determine the release
if [ "${AWIPSII_RELEASE}" = "" ]; then
   export AWIPSII_RELEASE=`date +"%Y%m%d%H"`
fi

echo AWIPSII_RELEASE is: ${AWIPSII_RELEASE}
