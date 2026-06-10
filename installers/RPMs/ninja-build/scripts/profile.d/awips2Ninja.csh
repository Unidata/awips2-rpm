#!/bin/csh

# Set Ninja installation location.
setenv NINJA_HOME "/awips2/ninja-build"

if $?PATH then
   setenv PATH ${NINJA_HOME}/bin:$PATH
else
   setenv PATH ${NINJA_HOME}/bin
endif
