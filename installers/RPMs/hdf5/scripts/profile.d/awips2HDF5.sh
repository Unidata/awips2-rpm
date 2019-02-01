#!/bin/bash

if [ $(id -u) -eq 0 -a ! -v A2LIBS ]; then
   return;
fi

if [ -d /awips2/hdf5 ]; then
   HDF5_INSTALL="/awips2/hdf5"
   # Update The Environment.
   AWIPS_HDF5=${HDF5_INSTALL}
   # Determine If HDF5 Is Already Part Of The Path
   CHECK_PATH=`echo ${PATH} | grep ${HDF5_INSTALL}`
   if [ "${CHECK_PATH}" = "" ]; then
      # HDF5 Is Not In The Path; Add It.
      export PATH=${HDF5_INSTALL}/bin:${PATH}
   fi
   export HDF5_PLUGIN_PATH=${HDF5_INSTALL}/lib
fi
