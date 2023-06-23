#!/bin/bash -v

if [ -d  /awips2/edex/conf/jms/auth ]; then
  QPID_SSL_CERT_DB=/awips2/edex/conf/jms/auth
  QPID_SSL_CERT_NAME=guest

  export QPID_SSL_CERT_DB
  export QPID_SSL_CERT_NAME
fi
