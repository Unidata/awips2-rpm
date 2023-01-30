#!/bin/csh

###
#The following environmental variables are used by Apache Thrift java, c++ and python components.
###

# The MaxMessageSize member defines the maximum size of a (received) message, in bytes. 
# If not set, Thrift will use a default value of about 100 MB ( 100 * 1024 * 1024 ) .

setenv THRIFT_MAX_MESSAGE_SIZE  `expr 2000 \* 1024 \* 1024` # ~2GB 

# MaxFrameSize limits the size of one frame of data for the TFramedTransport in bytes. 
# This is unused by AWIPS, but still configurable. If not set, default is 16384000 bytes

# setenv THRIFT_MAX_FRAME_SIZE 16384000

# The Recursion Depth defines, how deep structures may be nested into each other. 
# If not set, the default allows for structures nested up to 64 levels deep.

setenv THRIFT_RECURSION_DEPTH 64
