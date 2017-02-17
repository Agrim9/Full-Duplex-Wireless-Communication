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
		self.h = np.array(range(size))  #coefficients of FIR filter
		self.num_iter = 20
		self.epsilon = 0.1 #Step size


    def work(self, input_items, output_items):
        rtl_sig = input_items[0]
        tx_sig =input_items[1]
        out = output_items[0]
		np.append(self.insig, tx_sig)
		if (len(tx_sig) > 0):
		    # Part 1 : Estimating frequency offset and delay

		    # Part 2 : Channel modelling FIR Filter
			X = [self.insig[-size-i:-i] for i in range(len(tx_sig))]
		
			temp1 = 2*np.dot(np.conjugate(X.transpose()), rtl_sig)
			temp2 = 2*np.dot(np.conjugate(X.transpose()), X)

		    while(i < self.num_iter and distance):
				i += 1
				error = (np.sum((np.absolute(np.dot(X, self.h)-rtl_sig))**2))
				if (i % 10 == 0):
					print "Iteration " + str(i) + " error is : " + str(error)

			#Compute the gradient
				temp3 = np.dot(np.conjugate(temp2), self.h)
				temp3 = np.dot(np.conjugate(self.h.transpose()), temp2)
				gradient = -temp1 + temp3
				self.h = self.h - epsilon*gradient/len(tx_sig)
			 
			

		    
		    out[:] = rtl_sig-np.dot(np.conjugate(X), self.h)
		return len(output_items[0])

