#!/usr/bin/env python

from __future__ import division

import sys
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime
from struct import *

from time        import sleep

# Input: DDD HH:MM:SS.NNNNNNN
# Output: time difference in seconds
def delta_time_with_julian_day(time1_str, time2_str):
    # Expected format time to DDD HH:MM:SS.NNNNNNN)
    # Example:  123 21:04:00.7890225

    # Parse time1
    day1 = int(time1_str[0:3])
    hour1 = int(time1_str[4:6])
    min1 = int(time1_str[7:9])
    sec1 = float(time1_str[10:])

    # Compute time1 in seconds
    time1 = sec1 + (min1 * 60) + (hour1 * 3600)

    print day1, hour1, min1, sec1, time1

    # Parse time2
    day2 = int(time2_str[0:3])
    hour2 = int(time2_str[4:6])
    min2 = int(time2_str[7:9])
    sec2 = float(time2_str[10:])

    # Compute day difference
    day_diff = (day2 - day2) * 24

    # Compute time2 in seconds
    time2 = sec2 + (min2 * 60) + ((hour2 + (day_diff * 24)) * 3600)

    print day2, hour2, min2, sec2, time2
    
    return (time2-time1)

def convert_time_to_str(time):

    # Format time to DDD HH:MM:SS.NNNNNNN)
    # Example:  123 21:04:00.7890225

    # Get Julian day
    tt = time.timetuple()
    day = tt.tm_yday
        
    time_str = ''
    time_str += str(day) + ' '

    # Get hour
    hour = time.hour
    if hour > 10:
        time_str += str(hour) + ':'
    else:
        time_str += '0' + str(hour) + ':'

    # Get minute
    minute = time.minute
    if minute > 10:
        time_str += str(minute) + ':'
    else:
        time_str += '0' + str(minute) + ':'

    # Get second
    sec = time.second
    if sec > 10:
        time_str += str(sec) + '.'
    else:
        time_str += '0' + str(sec) + '.'

    # Get millisecond
    msec = time.microsecond
    if msec < 10:
        time_str += '00000' + str(msec)
    elif msec < 100:
        time_str += '0000' + str(msec)
    elif msec < 1000:
        time_str += '000' + str(msec)
    elif msec < 10000:
        time_str += '00' + str(msec)
    elif msec < 100000:
        time_str += '0' + str(msec)
    else:
        time_str += str(msec)

    time_str += '0'

    return time_str


# ------------------------------------------- Begin Main Program --------------------------

if __name__ == '__main__' :
    # datetime object containing current date and time
    time1 = datetime.utcnow()
    sleep(1)
    time2 = datetime.utcnow()

    print time1
    print time2

    time1_str = convert_time_to_str(time1)
    print time1_str
    time2_str = convert_time_to_str(time2)
    print time2_str

    delta_time = delta_time_with_julian_day(time1_str, time2_str)
    print delta_time


