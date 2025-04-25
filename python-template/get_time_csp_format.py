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

    # Get Julian day
    tt = now.timetuple()
    print tt.tm_yday, now

    day = tt.tm_yday

    bcd_time = ''

#   Stored in 8-bytes (DD DH HM MS SN NN NN NN)
    word_1 = 0x0
    word_2 = 0x0

    # Get day
    dayO = int(day % 10)
    day = day / 10
    dayT = int(day % 10)
    day = day /10
    dayH = int(day % 10)
    word_1 = (dayH << 28) | (dayT << 24) | (dayO << 20)

    # Get hour
    hour = now.hour
    hourO = int(hour % 10)
    hour = hour /10
    hourT = int(hour % 10)
    word_1 = word_1 | (hourT << 16) | (hourO << 12)

    # Get minute
    minute = now.minute
    minO = int(minute % 10)
    minute = minute /10
    minT = int(minute % 10)
    word_1 = word_1 | (minT << 8) | (minO << 4)

    # Get second
    sec = now.second
    secO = int(sec % 10)
    sec = sec /10
    secT = int(sec % 10)
    word_1 = word_1 | secT 
    word_2 = word_2 | (secO << 28)

    # Get millisecond
    msec = now.microsecond / 1000
    msecO = int(msec % 10)
    msec = msec / 10
    msecT = int(msec % 10)
    msec = msec /10
    msecH = int(msec % 10)
    word_2 = word_2 | (msecH << 24) | (msecT << 20) | (msecO << 16)

    print "word_1 = 0x%x, word_2 = 0x%x" % (word_1, word_2)
    bcd_time = pack(">ll", word_1, word_2)
