# Full-Duplex-Wireless-Communication
Modelling Single channel Full Duplex Wireless Communication </br>

##[Final Report](EDL_Report.pdf)    
  
## [Final GNURadio Code](Active_Cancellation/self_cancel.py)

## DSP Implementation
DSP implementation was done using DSP 5515. The Codes for the same were written in embedded C and CCSv7 IDE. Please follow the [link](Active_Cancellation/DSP_Project/main.c) for the main code. The implementation has not been *tested*. 

## Configuring GNUradio
- Copy CMakeLists.txt from FHSS project(/lib and /swig) and change names appropriately
- Add local_block_paths in `/etc/gnuradio/conf.d`
