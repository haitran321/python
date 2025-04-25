#!/usr/bin/env python

from __future__ import division

import sys
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------- Begin Main Program --------------------------

if __name__ == '__main__' :

    # The format() function simply formats the input following the Format Specification mini language. 
    # The # makes the format include the 0b prefix, and the 010 size formats the output to fit in 10 characters width, 
    # with 0 padding; 2 characters for the 0b prefix, the other 8 for the binary digits.

    print(format(14, '#010b'))
    print(format(14, '010b'))


