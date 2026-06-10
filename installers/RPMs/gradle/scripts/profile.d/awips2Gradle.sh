#!/bin/bash

if [ $(id -u) -eq 0 -a ! -v A2LIBS ]; then
   return;
fi

if [ -d /awips2/gradle ]; then
   # Update The Environment.
   export GRADLE_HOME="/awips2/gradle"
   # Determine If Gradle Is Already Part Of The Path.
   CHECK_PATH=`echo ${PATH} | grep ${GRADLE_HOME}/bin`
   if [ ! "${CHECK_PATH}" = "" ]; then
      return
   fi
   # Gradle Is Not In The Path; Add It To The Path.
   export PATH="${GRADLE_HOME}/bin:${PATH}"
fi
