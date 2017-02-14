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


    def work(self, input_items, output_items):
        rtl_sig = input_items[0]
        tx_sig =input_items[1]
        out = output_items[0]
        # Part 1 : Estimating frequency offset and delay
        

        # Part 2 : Channel modelling FIR Filter
        
        
        out[:] = tx_sig+rtl_sig
        return len(output_items[0])

