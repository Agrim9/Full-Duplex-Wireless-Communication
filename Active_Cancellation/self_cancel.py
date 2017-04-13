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
from numpy.linalg import inv
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
        self.size = 30   # Number of past values to be used
        self.h = np.zeros([self.size + 1])  #coefficients of FIR filter
        self.h[self.size] = 0
        self.num_iter = 150
        self.epsilon = 0.1 #Step size
        self.samp_rate=samp_rate
        self.rtl_buffer=[]
        self.tx_buffer=[]         
        self.gnu_buff=4096
        self.freq_offset=0
        self.freq_offset_ctr=5

    def work(self, input_items, output_items):
        
        rtl_sig1 = input_items[0]   #Capturing Inputs
        tx_sig1 =input_items[1]     #Capturing Inputs
        out = output_items[0]
        
        ###################   FREQUENCY AND PHASE OFFSET   #########################
        #
        
        # Part 1 : Estimating frequency offset and delay
        print "Input Length " + str(len(rtl_sig1))
        
      
        rtl_fft = fft(rtl_sig1,self.samp_rate*4) #for 0.25 hz accuracy
        tx_fft = fft(tx_sig1,self.samp_rate*4)
        #fft_size = len(tx_fft)
        tx_abs_list = [np.absolute(x) for x in tx_fft]
        rtl_abs_list = [np.absolute(x) for x in rtl_fft]
        max_tx_f = np.argmax(tx_abs_list)
        max_rtl_f = np.argmax(rtl_abs_list)
        
        self.freq_offset = (max_rtl_f - max_tx_f)*0.25 #as one step is 1 hz now
        #if(abs(test_freq_offset-self.freq_offset)<500):
        
        print "Frequency Offset is: ", self.freq_offset            
                   
        ##################  CHANNEL ESTIMATION ####################################
            
        rtl_sig = np.real(rtl_sig1)
        tx_sig = np.real(tx_sig1)    
        lamda = 0.0001

        self.insig = np.append(self.insig, tx_sig)
        buff= np.zeros(self.size)
        self.insig=np.insert(self.insig,buff,0,axis=0)
        if(len(self.insig) > self.size):
            # Part 2 : Channel modelling FIR Filter      
            X = np.array([self.insig[len(self.insig)-self.size-i:len(self.insig)-i] for i in range(len(tx_sig)-1, -1, -1)])
            #print "X shape " + str(X.shape) + " rtl shape " +str(rtl_sig.shape)
            amp_X = X.max()
            amp_y = rtl_sig.max()
            X = X/amp_X
            rtl_sig = rtl_sig/amp_y
            X = np.insert(X, 0, np.ones(len(rtl_sig)), axis=1)
            #####################
            #transfer_function= np.dot(inv(np.dot(X.transpose(),X) + lamda*np.eye(X.shape[1])),np.dot(X.transpose(),rtl_sig))
            #min_error= rtl_sig - np.dot(X,transfer_function)
            #print "min error is ", np.sum(min_error**2) 
            ##################
            
            if(len(tx_sig) > 100):
                temp1 = np.dot(np.conjugate(X.transpose()), rtl_sig)
                temp2 = np.dot(np.conjugate(X.transpose()), X)
                i=0
                error = 1000
                while(i < self.num_iter):
                    if (i > 50 and abs(perc_error_change) < 2*10**(-2)):
                        break
                    i += 1
                    
                    error_old = error  
                    error = (np.sum((np.absolute(np.dot(X, self.h)-rtl_sig))**2))/(2*len(tx_sig))
                    error_new = error
                    perc_error_change = (error-error_old)*100.0/error_old
                    if (error_new > 2*error_old):
                        self.epsilon = self.epsilon/2
                        #print "40-50 weight" + str(self.h[40:])

                #Compute the gradient
                    temp3 = np.dot(np.conjugate(temp2), self.h)
                    gradient = -temp1 + temp3
                    #if (i % 20 == 0 or i==1):
                        #print X[len(tx_sig)-1,self.size], self.h[self.size], rtl_sig[len(tx_sig)-1]
                        #print "shape of H " + str(self.h) 
                        #print "Iteration " + str(i) + " error is : " + str(error)
                        #print "Gradient: " + str(gradient)
                        #print "Change in error: ", (error-error_old)*100.0/error_old
                    self.h = self.h - (self.epsilon*gradient/len(tx_sig))
                 
            #if(len(tx_sig) > 100):   
                #self.h=transfer_function
                out[:] = np.real(rtl_sig1)-(np.dot(X, self.h)*amp_y*1.0)
            else:
                out[:] = np.real(rtl_sig1)-(np.dot(X, self.h))

        else:
            out[:]=np.zeros(len(out))
        #out[:] = tx_sig1
        #print "End of Interation Error is:"+str(error)    
        return len(output_items[0])