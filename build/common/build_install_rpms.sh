#!/bin/bash -x

#
# This script moves the build artifacts to a staging area and
# creates a RPM Repo using the baselined comps.xml file.
#
# SCRIPT HISTORY
#
# Date          Ticket#  Engineer    Description
# ------------- -------- ----------- -----------------------------
# Mar 10, 2016  4734     dlovely     Initial import from awipscm

TARGET_DIR=$1
sudo mkdir -p $TARGET_DIR

source ${WORKSPACE}/git/AWIPS2_build/build/common/version_release.sh

#sync updated rpms
sudo rsync -avz --progress --delete ${WORKSPACE}/rpmbuild/RPMS/ $TARGET_DIR/v$AWIPSII_RELEASE/
if [ $? -ne 0 ]; then
   exit 1
fi

if [ -d ${WORKSPACE}/eclipse-repo ]; then
   ls -1 ${WORKSPACE}/eclipse-repo/* > /dev/null 2>&1
   if [ $? -eq 0 ]; then
      sudo mkdir -p $TARGET_DIR/v$AWIPSII_RELEASE/cave
      sudo cp -v ${WORKSPACE}/eclipse-repo/* $TARGET_DIR/v$AWIPSII_RELEASE/cave/
   fi
fi

pushd . > /dev/null
cd $TARGET_DIR
if [ -h latest ]; then
   sudo rm -fv latest
fi

time sudo /usr/bin/createrepo -c cachedir -g ${WORKSPACE}/git/AWIPS2_build/installers/Linux/comps.xml --workers=20 .
if [ $? -ne 0 ]; then
   exit 1
fi

sudo ln -sf v$AWIPSII_RELEASE latest

popd > /dev/null

