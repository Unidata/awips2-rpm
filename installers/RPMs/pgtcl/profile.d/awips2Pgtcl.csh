#!/bin/csh

if ( ! $?TCLLIBPATH ) then 
  setenv TCLLIBPATH /awips2/pgtcl/lib
else if ( "$TCLLIBPATH" !~ *"/awips2/pgtcl/lib"* ) then
  setenv TCLLIBPATH "/awips2/pgtcl/lib $TCLLIBPATH"
endif

