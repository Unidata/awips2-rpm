#!/bin/bash

if [ $(id -u) -eq 0 -a ! -v A2LIBS ]; then
   return;
fi

if [ -d /awips2/maven ]; then
   # Determine Where Maven Has Been Installed.
   MAVEN_INSTALL=/awips2/maven

   # Update The Environment.
   export M2_HOME="${MAVEN_INSTALL}"
   # Determine If Maven Is Already Part Of The Path.
   CHECK_PATH=`echo ${PATH} | grep ${MAVEN_INSTALL}`
   if [ ! "${CHECK_PATH}" = "" ]; then
      return
   fi
   # Maven Is Not In The Path; Add It To The Path.
   export M2="$M2_HOME/bin"
   export PATH="${M2}:${PATH}"
fi
