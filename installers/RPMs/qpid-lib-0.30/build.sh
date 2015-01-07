#!/bin/bash

# Verify that the workspace has been specified
if [ -z ${WORKSPACE} ]; then
   echo "Error: the location of the baseline workspace must be specified using the WORKSPACE environment variable."
   exit 1
fi
if [ -z ${AWIPSII_BUILD_ROOT} ]; then
   export AWIPSII_BUILD_ROOT="/tmp/${USER}/awips-component"
   echo "INFO: using default build root - ${AWIPSII_BUILD_ROOT}."
fi

pushd . > /dev/null

# create the rpm directory structure
mkdir -p ${AWIPSII_TOP_DIR}/RPMS
mkdir -p ${AWIPSII_TOP_DIR}/SRPMS
mkdir -p ${AWIPSII_TOP_DIR}/BUILD
mkdir -p ${AWIPSII_TOP_DIR}/SOURCES

FOSSDIR=${WORKSPACE}/foss/qpid-lib-0.30/

cp -v ${FOSSDIR}/qpid-client-0.30-bin.tar.gz ${AWIPSII_TOP_DIR}/SOURCES
cp -v ${FOSSDIR}/qpid-cpp-0.30.tar.gz ${AWIPSII_TOP_DIR}/SOURCES

# build the rpm
rpmbuild -ba \
   --define "_topdir ${AWIPSII_TOP_DIR}" \
   --define "_baseline_workspace ${WORKSPACE}" \
   qpid-java.spec
if [ $? -ne 0 ]; then
   exit 1
fi
rpmbuild -ba \
   --define "_topdir ${AWIPSII_TOP_DIR}" \
   --define "_baseline_workspace ${WORKSPACE}" \
   --define "_build_root ${AWIPSII_BUILD_ROOT}" \
   --buildroot ${AWIPSII_BUILD_ROOT} \
   qpid-lib.spec
if [ $? -ne 0 ]; then
   exit 1
fi

popd > /dev/null

exit 0
