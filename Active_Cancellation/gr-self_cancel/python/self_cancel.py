#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017 <+YOU OR YOUR COMPANY+>.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

import numpy as np
from gnuradio import gr
from scipy.fftpack import fft

class self_cancel(gr.sync_block):
    """
    docstring for block self_cancel
    """
    def __init__(self,samp_rate):
        gr.sync_block.__init__(self,
            name="self_cancel",
            in_sig=[np.complex64,np.complex64],
            out_sig=[np.complex64])
        self.insig = np.array([])
        self.size = 50   # Number of past values to be used
        self.h = np.zeros(self.size + 1)  #coefficients of FIR filter
        self.num_iter = 1000
        self.epsilon = 0.01 #Step size
        self.samp_rate=samp_rate         

    def work(self, input_items, output_items):
        rtl_sig1 = input_items[0]
        tx_sig1 =input_items[1]
        out = output_items[0]
        ###################   FREQUENCY AND PHASE OFFSET   #########################
        #
   
        # Part 1 : Estimating frequency offset and delay
        if (len(rtl_sig1) > 100):
            rtl_fft = fft(rtl_sig1,self.samp_rate*2) #for 0.5 hz accuracy
            tx_fft = fft(tx_sig1,self.samp_rate*2)
            #fft_size = len(tx_fft)
            tx_abs_list = [np.absolute(x) for x in tx_fft]
            rtl_abs_list = [np.absolute(x) for x in rtl_fft]
            max_rtl_f = np.argmax(rtl_abs_list)
            max_tx_f = np.argmax(tx_abs_list)

            freq_offset = (max_rtl_f - max_tx_f)*0.5 #as one step is 0.5 hz now
            print "Frequency Offset is: ", freq_offset

            tx_sig1 = [tx_sig1[i] * np.exp(np.complex(0,2*np.pi*i*freq_offset)) for i in range(len(rtl_sig1))]

        ##################  CHANNEL ESTIMATION ####################################
            
        rtl_sig = np.real(rtl_sig1)
        tx_sig = np.real(tx_sig1)    
        self.insig = np.append(self.insig, tx_sig)
        if(len(self.insig) > self.size):
            # Part 2 : Channel modelling FIR Filter
            #print "len of input " + str(len(tx_sig))
            if(len(self.insig) > len(tx_sig)+self.size):
                X = np.array([self.insig[len(self.insig)-self.size-i:len(self.insig)-i] for i in range(len(tx_sig))])
            else:
                X = np.array([self.insig[len(self.insig)-self.size-i:len(self.insig)-i] for i in range(len(tx_sig)-self.size)])
                Z = np.array([np.zeros(self.size) for i in range(self.size)])
                X = np.insert(X,len(X),Z,axis=0)
            #print "X shape " + str(X.shape) + " rtl shape " +str(rtl_sig.shape)
            amp_X = X.max()
            amp_y = rtl_sig.max()
            X = X/amp_X
            rtl_sig = rtl_sig/amp_y
            X = np.insert(X, 0, np.ones(len(rtl_sig)), axis=1)
            if(len(tx_sig) > 100):
                temp1 = np.dot(np.conjugate(X.transpose()), rtl_sig)
                temp2 = np.dot(np.conjugate(X.transpose()), X)
                i=0
                error = 1000
                while(i < self.num_iter):
                    if (i > 200 and error < 10**(-11)):
                        break
                    i += 1
                    #print "im in loop"
                    error_old = error
                    error = (np.sum((np.absolute(np.dot(X, self.h)-rtl_sig))**2))/(2*len(tx_sig))
                    error_new = error
                    if (error_new > 2*error_old):
                        self.epsilon = self.epsilon/2
                    #if (i % 500 == 0):
                        #print "Iteration " + str(i) + " error is : " + str(error)
                        #print "40-50 weight" + str(self.h[40:])

                #Compute the gradient
                    temp3 = np.dot(np.conjugate(temp2), self.h)
                    gradient = -temp1 + temp3
                    self.h = self.h - (self.epsilon*gradient/len(tx_sig))
                out[:] = np.real(rtl_sig1)-(np.dot(X, self.h)*(amp_y))
            else:
                out[:] = np.real(rtl_sig1)-(np.dot(X, self.h)*(amp_y))
        else:
            out[:]=np.zeros(len(out))
        #out[:] = tx_sig1    
        return len(output_items[0])
