#!/bin/bash

if [ -z ${AWIPSII_BUILD_ROOT} ]; then
   export AWIPSII_BUILD_ROOT="/tmp/${USER}/awips2-qpid-java-broker"
   echo "INFO: using default build root - ${AWIPSII_BUILD_ROOT}."
fi

path_to_script=`readlink -f $0`
dir=$(dirname $path_to_script)

__SPECS=qpid-java-broker.spec

export TOPDIR=${AWIPSII_BUILD_ROOT}

# create the rpm directory structure
if [ -d ${TOPDIR}/BUILD ]; then
   rm -rf ${TOPDIR}/BUILD
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi
mkdir ${TOPDIR}/BUILD

if [ -d ${TOPDIR}/SOURCES ]; then
   rm -rf ${TOPDIR}/SOURCES
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi
mkdir ${TOPDIR}/SOURCES

FOSSDIR=${dir}/../../../foss/qpid-java-broker/

cp ${FOSSDIR}/packaged/qpid-java-broker-0.28.tar.gz ${TOPDIR}/SOURCES

if [ -d ${TOPDIR}/RPMS ]; then
   rm -rf ${TOPDIR}/RPMS
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi
mkdir ${TOPDIR}/RPMS

if [ -d ${TOPDIR}/SRPMS ]; then
   rm -rf ${TOPDIR}/SRPMS
   if [ $? -ne 0 ]; then
      exit 1
   fi
fi
mkdir ${TOPDIR}/SRPMS

# build the rpm
rpmbuild -bb \
   --define "_topdir ${TOPDIR}" \
   --define "_patchdir ${FOSSDIR}/src/patch" \
   ${__SPECS}
if [ $? -ne 0 ]; then
   exit 1
fi

exit 0
