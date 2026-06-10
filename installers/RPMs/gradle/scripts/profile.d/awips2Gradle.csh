#!/bin/csh

# Set Gradle installation location.
setenv GRADLE_HOME "/awips2/gradle"

if $?PATH then
   setenv PATH ${GRADLE_HOME}/bin:$PATH
else
   setenv PATH ${GRADLE_HOME}/bin
endif
