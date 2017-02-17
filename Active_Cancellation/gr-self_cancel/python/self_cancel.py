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

class self_cancel(gr.sync_block):
    """
    docstring for block self_cancel
    """
    def __init__(self):
        gr.sync_block.__init__(self,
            name="self_cancel",
            in_sig=[np.complex64,np.complex64],
            out_sig=[np.complex64])
        self.insig = np.array([])
        self.size = 50   # Number of past values to be used
        self.h = np.zeros(self.size)  #coefficients of FIR filter
        self.num_iter = 5
        self.epsilon = 0.001 #Step size


    def work(self, input_items, output_items):
        rtl_sig = input_items[0]
        tx_sig =input_items[1]
        out = output_items[0]
        self.insig = np.append(self.insig, tx_sig)
        #print "len of rtl input " + str(len(rtl_sig)) + " len of tx_sig input " + str(len(tx_sig)) 
        #print "yo"
        #print "len of insig " + str(len(self.insig))
        
        if(len(self.insig) > self.size and len(tx_sig) > 0):
            # Part 1 : Estimating frequency offset and delay
            # Part 2 : Channel modelling FIR Filter
            #print "yo"
            if(len(self.insig)>len(tx_sig)+self.size):
                X = np.array([self.insig[len(self.insig)-self.size-i:len(self.insig)-i] for i in range(len(tx_sig))])
            else:
                X = np.array([self.insig[len(self.insig)-self.size-i:len(self.insig)-i] for i in range(len(tx_sig)-self.size)])
                Z = np.array([np.zeros(self.size) for i in range(self.size)])
                X = np.insert(X,len(X),Z,axis=0)
            print "X shape " + str(X.shape) + " rtl shape " +str(rtl_sig.shape)
            temp1 = 2*np.dot(np.conjugate(X.transpose()), rtl_sig)
            temp2 = 2*np.dot(np.conjugate(X.transpose()), X)
            i=0
            while(i < self.num_iter):
                i += 1
                #print "im in loop"
                error = (np.sum((np.absolute(np.dot(X, self.h)-rtl_sig))**2))/len(tx_sig)
                if (i % 5 == 0):
                    print "Iteration " + str(i) + " error is : " + str(error)

            #Compute the gradient
                temp3 = np.dot(np.conjugate(temp2), self.h)
                temp3 = np.dot(np.conjugate(self.h.transpose()), temp2)
                gradient = -temp1 + temp3
                self.h = self.h - self.epsilon*gradient/len(tx_sig)
            out[:] = rtl_sig-np.dot(X, self.h)
        else:
            out[:] = np.zeros(len(tx_sig))
        return len(output_items[0])
