#!/bin/bash

if [ $(id -u) -eq 0 -a ! -v A2LIBS ]; then
   return;
fi

if [ -d /awips2/ninja-build ]; then
   # Update The Environment.
   export NINJA_HOME="/awips2/ninja-build"
   # Determine If Ninja Is Already Part Of The Path.
   CHECK_PATH=`echo ${PATH} | grep ${NINJA_HOME}/bin`
   if [ ! "${CHECK_PATH}" = "" ]; then
      return
   fi
   # Ninja Is Not In The Path; Add It To The Path.
   export PATH="${NINJA_HOME}/bin:${PATH}"
fi
