#!/usr/bin/env python

from __future__ import division

import sys
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime
from struct import *

# ------------------------------------------- Begin Main Program --------------------------

if __name__ == '__main__' :
    # datetime object containing current date and time
    now = datetime.utcnow()

    print now

    print now.year
    print now.month
    print now.day
    print now.hour
    print now.minute
    print now.second
    print now.microsecond

    real_sec = now.second + (now.microsecond/1000000)
    print real_sec

    # Get Julian day
    tt = now.timetuple()
    print tt.tm_yday, now


