#!/bin/bash

if [ $(id -u) -eq 0 -a ! -v A2LIBS ]; then
   return;
fi

if [ -d /awips2/ant ]; then
   # Determine Where Ant Has Been Installed.
   ANT_INSTALL=/awips2/ant

   # Update The Environment.
   export ANT_HOME="${ANT_INSTALL}"
   # Determine If Ant Is Already Part Of The Path.
   if ! echo ${PATH} | grep -q ${ANT_INSTALL}; then
      # Ant Is Not In The Path; Add It To The Path.
      export PATH="${ANT_INSTALL}/bin:${PATH}"
   fi
fi
