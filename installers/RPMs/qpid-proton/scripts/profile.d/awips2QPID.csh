#!/bin/csh -v

set dir="/awips2/edex/conf/jms/auth"

if ( -d  ${dir} ) then
  set DB="/awips2/edex/conf/jms/auth"
  set NAME="guest"

  setenv QPID_SSL_CERT_DB ${DB}
  setenv QPID_SSL_CERT_NAME ${NAME}
endif
