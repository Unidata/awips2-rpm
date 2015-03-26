#!/bin/bash

path_to_script=`readlink -f $0`
dir=$(dirname $path_to_script)

__SPECS=qpid-broker.spec

mkdir -p ${AWIPSII_TOP_DIR}/RPMS
mkdir -p ${AWIPSII_TOP_DIR}/SRPMS
mkdir -p ${AWIPSII_TOP_DIR}/BUILD
mkdir -p ${AWIPSII_TOP_DIR}/SOURCES

FOSSDIR=${WORKSPACE}/foss/qpid-java-broker-0.32/

cp -v ${FOSSDIR}/packaged/qpid-broker-0.32-bin.tar.gz ${AWIPSII_TOP_DIR}/SOURCES
cp -v ${FOSSDIR}/packaged/awips.patch ${AWIPSII_TOP_DIR}/SOURCES


# build the rpm
 rpmbuild -bb \
   --define "_topdir ${AWIPSII_TOP_DIR}"/ \
   --define "_patchdir ${FOSSDIR}/src/patch" \
   ${__SPECS}
if [ $? -ne 0 ]; then
   exit 1
fi

exit 0
