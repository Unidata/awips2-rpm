#!/bin/bash

if [ ! $TCLLIBPATH ]; then
	export TCLLIBPATH=/awips2/pgtcl/lib
elif  [[ $TCLLIBPATH != *"/awips2/pgtcl/lib"* ]]; then
	export TCLLIBPATH="/awips2/pgtcl/lib $TCLLIBPATH"
fi
