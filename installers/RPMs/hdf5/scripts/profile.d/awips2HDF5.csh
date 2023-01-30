#!/bin/csh

set HDF5_INSTALL="/awips2/hdf5"
setenv AWIPS_HDF5 ${HDF5_INSTALL}
setenv HDF5_PLUGIN_PATH ${HDF5_INSTALL}/lib/

if $?PATH then
   setenv PATH ${HDF5_INSTALL}/bin:$PATH
else
   setenv PATH ${HDF5_INSTALL}/bin
endif

if $?LD_LIBRARY_PATH then
   setenv LD_LIBRARY_PATH ${HDF5_INSTALL}/lib:$LD_LIBRARY_PATH
else
   setenv LD_LIBRARY_PATH ${HDF5_INSTALL}/lib
endif
