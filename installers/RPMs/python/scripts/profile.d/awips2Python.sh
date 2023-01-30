#!/bin/bash

if [ $(id -u) -eq 0 -a ! -v A2LIBS ]; then
   return;
fi

if [ -d /awips2/python ]; then
   PYTHON_INSTALL="/awips2/python"
   # Update The Environment.
   AWIPS_PYTHON=${PYTHON_INSTALL}
   # Determine If Python Is Already Part Of The Path
   CHECK_PATH=`echo ${PATH} | grep ${PYTHON_INSTALL}`
   if [ "${CHECK_PATH}" = "" ]; then
      # Python Is Not In The Path; Add It.
      export PATH=${PYTHON_INSTALL}/bin:${PATH}
   fi
fi
