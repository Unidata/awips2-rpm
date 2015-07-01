#!/bin/csh

# Determine where maven has been installed.
setenv M2_HOME "/awips2/maven"
setenv M2 $M2_HOME/bin

if $?PATH then
   setenv PATH ${M2}:$PATH
else
   setenv PATH ${M2}
endif
