#!/usr/bin/env python

from __future__ import division

import sys
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------- Begin Main Program --------------------------

if __name__ == '__main__' :

        MONOPULSE_ANY_CH_CHECK_INC_VALUE     =   1   
        MONOPULSE_CENTER_CH_CHECK_INC_VALUE  =   10  
        MONOPULSE_CROSS_CH_CHECK_INC_VALUE   =   100 
        MONOPULSE_CORNER_CH_CHECK_INC_VALUE  =   1000


        all = 0
        center = 0
        cross = 0
        corner = 0

        x = 1999
        temp_x = 0
        new_x = x

        if new_x >= MONOPULSE_CORNER_CH_CHECK_INC_VALUE:
            temp_x = (int)(new_x/MONOPULSE_CORNER_CH_CHECK_INC_VALUE)
            corner += temp_x

            new_x = new_x - (temp_x*MONOPULSE_CORNER_CH_CHECK_INC_VALUE)

        if new_x >= MONOPULSE_CROSS_CH_CHECK_INC_VALUE:
            temp_x = (int)(new_x/MONOPULSE_CROSS_CH_CHECK_INC_VALUE)
            cross += temp_x

            new_x = new_x - (temp_x*MONOPULSE_CROSS_CH_CHECK_INC_VALUE)

        if new_x >= MONOPULSE_CENTER_CH_CHECK_INC_VALUE:
            temp_x = (int)(new_x/MONOPULSE_CENTER_CH_CHECK_INC_VALUE)
            center += temp_x

            new_x = new_x - (temp_x*MONOPULSE_CENTER_CH_CHECK_INC_VALUE)

        if new_x >= MONOPULSE_ANY_CH_CHECK_INC_VALUE:
            temp_x = (int)(new_x/MONOPULSE_ANY_CH_CHECK_INC_VALUE)
            all += temp_x

        print "all = %d, center = %d, cross = %d, corner = %d" % (all, center, cross, corner)

        
