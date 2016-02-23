#!/bin/bash -x

#
# Creates empty dirs required for the build.
#
# SCRIPT HISTORY
#
# Date          Ticket#  Engineer    Description
# ------------- -------- ----------- -----------------------------
# Mar 10, 2016  4734     dlovely     Initial import from awipscm

# Prepare to build the rpms.
if [ -d ${WORKSPACE}/rpmbuild ]; then
   sudo rm -rf ${WORKSPACE}/rpmbuild
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi
mkdir -p ${WORKSPACE}/rpmbuild/BUILD
if [ $? -ne 0 ]; then
   exit 1
fi
mkdir -p ${WORKSPACE}/rpmbuild/RPMS
if [ $? -ne 0 ]; then
   exit 1
fi
mkdir -p ${WORKSPACE}/rpmbuild/SOURCES
if [ $? -ne 0 ]; then
   exit 1
fi
mkdir -p ${WORKSPACE}/rpmbuild/SPECS
if [ $? -ne 0 ]; then
   exit 1
fi
mkdir -p ${WORKSPACE}/rpmbuild/SRPMS
if [ $? -ne 0 ]; then
   exit 1
fi

exit 0
