#!/bin/csh

# Red-Hat-provided psql defaults to looking for the socket in
# /var/run/postgresql. Our configuration puts it in /tmp, which is the default
# for PostgreSQL when built from source
setenv PGHOST /tmp
