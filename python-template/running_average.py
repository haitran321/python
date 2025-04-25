#!/usr/bin/env python

from __future__ import division

import sys
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------- Begin Main Program --------------------------

if __name__ == '__main__' :

    x_lst = []
    for i in range(0,10):
        x_lst.append(i)

    counter = 0
    mean = 0.0
    old_mean = 0.0

    for i in range(0,10):

        counter += 1

        if counter == 1:    # First time
            mean = x_lst[i]
        else:   # Not first time
            mean = old_mean + (x_lst[i] - old_mean)/counter

        old_mean = mean

        print "%d: mean = %f" % (i, mean)
        
