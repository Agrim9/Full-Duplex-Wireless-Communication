#!/bin/sh
export GR_DONT_LOAD_PREFS=1
export srcdir=/home/agrim/Desktop/git/Full-Duplex-Wireless-Communication/Active_Cancellation/gr-self_cancel/lib
export PATH=/home/agrim/Desktop/git/Full-Duplex-Wireless-Communication/Active_Cancellation/gr-self_cancel/build/lib:$PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$DYLD_LIBRARY_PATH
export DYLD_LIBRARY_PATH=$LD_LIBRARY_PATH:$DYLD_LIBRARY_PATH
export PYTHONPATH=$PYTHONPATH
test-self_cancel 
