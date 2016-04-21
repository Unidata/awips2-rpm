#!/bin/bash -x

#
# Creates empty dirs required for the build.
#
# SCRIPT HISTORY
#
# Date          Ticket#  Engineer    Description
# ------------- -------- ----------- -----------------------------
# Mar 10, 2016  4734     dlovely     Initial import from awipscm

mkdir -p ${WORKSPACE}/baseline/build.edex/esb/logs
if [ $? -ne 0 ]; then
   exit 1
fi
mkdir -p ${WORKSPACE}/baseline/build.edex/esb/data/manual
if [ $? -ne 0 ]; then
   exit 1
fi
mkdir -p ${WORKSPACE}/baseline/build.edex/esb/data/uEngine
if [ $? -ne 0 ]; then
   exit 1
fi
