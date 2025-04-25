#!/usr/bin/env python

from __future__ import division

import sys
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------- Begin Main Program --------------------------

if __name__ == '__main__' :
    matrix = []
    matrix.append([])
    matrix.append([])
    matrix.append([])

    matrix[0].append(0)
    matrix[0].append(10)
    matrix[1].append(1)
    matrix[1].append(11)
    matrix[2].append(2)
    matrix[2].append(12)

    print matrix

    print matrix[0][1]
