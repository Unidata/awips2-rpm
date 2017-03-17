#!/bin/csh

# Determine where postgres has been installed.
set POSTGRES_INSTALL="/awips2/postgresql"

if $?LD_LIBRARY_PATH then
   setenv LD_LIBRARY_PATH ${POSTGRES_INSTALL}/lib:${POSTGRES_INSTALL}/lib32:$LD_LIBRARY_PATH
else
   setenv LD_LIBRARY_PATH ${POSTGRES_INSTALL}/lib:${POSTGRES_INSTALL}/lib32
endif

if $?PATH then
   setenv PATH ${POSTGRES_INSTALL}/bin:$PATH
else
   setenv PATH ${POSTGRES_INSTALL}/bin
endif
