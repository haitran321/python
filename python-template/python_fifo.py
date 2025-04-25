#!/usr/bin/env python

from __future__ import division

import sys
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------- Begin Main Program --------------------------
class FIFO:
    """A sample implementation of a First-In-First-Out
       data structure."""
    def __init__(self):
        self.stack = []
    def push(self, obj):
        self.stack.append(obj)
    def pop(self):
        self.stack.pop()


if __name__ == '__main__' :

    fifo = FIFO()
    
    # Init FIFO with 0
    for i in range(0,30):
        fifo.push(0)

    data = []
    data.append(1)
    data.append(2)
    data.append(3)
    print data, len(data)

    data.pop(0)
    print data, len(data)

    data.append(4)
    print data, len(data)



    
