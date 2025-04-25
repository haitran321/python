#!/usr/bin/env python

from __future__ import division

import numpy as np

# Unit config
unit_number = 0
trigger_master = 1
unit_ip_addr = ("172.16.80.41", "172.16.80.42", "172.16.80.43", "172.16.80.44", "172.16.80.45", "172.16.80.46")
num_unit = len(unit_ip_addr)

# DS config
ds_type_dict = {'ALPHA' : 1,
                  'BETA' : 2}
ds_type_str = 'ALPHA'   
ds = [1,2,3]

# Angles
kSineAlpha = 0
kSineBeta = 0

# UDP config
# Set data processor host and port
data_processor_ip_addr = "172.16.80.92"
data_port = 1001
dp_addr = (data_processor_ip_addr, data_port)
# Ports
unit_in_port = 1002
unit_start_port = 1003 
buf = 1024  
# Test driver addr/port
test_driver_pi_addr = "172.16.80.40"
test_driver_port = 1004
td_addr = (test_driver_pi_addr, test_driver_port)

trigger_pin = 3
num_ds = len(ds)		
#data_pins = ((5,7,11,13,15,19,21),(23,29,31,33,35,37,12),(16,18,22,24,26,32,36))
data_pins = ((5,7,11,13,15,19,21),(12,16,18,22,24,26,32),(23,29,31,33,35,37,38))
num_gpio_per_ds = 7
num_gpio = num_ds * num_gpio_per_ds

# MSG_ID
data_msg_id = 1
trigger_msg_id = 2
start_msg_id = 3
stop_msg_id = 4
roll_file_msg_id = 5
close_dp_msg_id = 6
td_send_test_mgr_id = 7
header_size = 9*4   # msg id, msg size, unit number, ds type, kSineAlpha, kSineBeta, ds 1, ds 2, ds 3 

# Data Msg
data_msg_size = header_size + (num_gpio * 4)

# Test data
use_test_data = 0
test_data = ((1,0,1,0,1,0,1),(0,1,0,1,0,1,0),(1,0,1,0,1,0,1))

# Get ds type str from ds type num
def get_ds_type_str(ds_type_num):

    ds_type_str = 'ALPHA'

    ds_type_str = list(ds_type_dict.keys())[list(ds_type_dict.values()).index(ds_type_num)]

    return ds_type_str

# Get all test unit host
def get_all_test_unit_hosts():

    remote_addr_lst = []
    for i in range(0,num_unit):
        remote_host = unit_ip_addr[i]
        remote_addr_lst.append((remote_host,unit_start_port))

    return remote_addr_lst

# Send msg to all test units
def send_msg_to_all_test_unit(out_sock, remote_addr_lst, msg):

    for i in range(0,len(remote_addr_lst)):
        print (remote_addr_lst[i])
        out_sock.sendto(msg,remote_addr_lst[i])

def cal_delay_switch_bits(increment, ds_lst, verbose):

    phase_shifters_num_lst = []
    phase_shifters_dec_lst = []
    phase_shifters_10_bits_lst = []
    alpha_phase_shifters_7_bits_lst = []
    beta_phase_shifters_7_bits_lst = []

    for i in range(0,153):
        phase_shifters_num_lst.append(i)
        phase_shifters_dec_lst.append(i)
        phase_shifters_10_bits_lst.append(i)
        alpha_phase_shifters_7_bits_lst.append(i)
        beta_phase_shifters_7_bits_lst.append(i)

    acc1 = increment + 4
    acc2 = (increment<<4) + 4
    acc3 = (increment<<5) + 4
    acc4 = (increment<<5) + acc2
    acc5 = (increment<<6) + 4

    if verbose:
        print ("increment: ", "{0:010b}".format(increment & 0x3FF))
        print ("acc1: ", "{0:010b}".format(acc1 & 0x3FF))
        print ("acc2: ", "{0:010b}".format(acc2 & 0x3FF))
        print ("acc3: ", "{0:010b}".format(acc3 & 0x3FF))
        print ("acc4: ", "{0:010b}".format(acc4 & 0x3FF))
        print ("acc5: ", "{0:010b}".format(acc5 & 0x3FF))

    phase_shifters_dec_lst[76] = 0

    # ACC1
    for i in range(75,75-15,-1):
        phase_shifters_dec_lst[i] = acc1
        acc1 += increment

    # ACC2
    for i in range(60,60-16,-1):
        phase_shifters_dec_lst[i] = acc2
        acc2 += increment

    # ACC3
    for i in range(44,44-16,-1):
        phase_shifters_dec_lst[i] = acc3
        acc3 += increment

    # ACC4
    for i in range(28,28-16,-1):
        phase_shifters_dec_lst[i] = acc4
        acc4 += increment

    # ACC5
    for i in range(12,0,-1):
        phase_shifters_dec_lst[i] = acc5
        acc5 += increment

    # Mod to stay below 1024 (10-bit)
    for i in range(76,0,-1):
        phase_shifters_dec_lst[i] = phase_shifters_dec_lst[i] % 1024

    if verbose:
        print ("DS\t  Dec\t 10-Bits\t  Alpha\t\t  Beta")
    for i in range(1,77):
        phase_shifters_10_bits_lst[i] = ("{0:010b}".format(phase_shifters_dec_lst[i] & 0x3FF))
        alpha_phase_shifters_7_bits_lst[i] = ("{0:07b}".format(phase_shifters_dec_lst[i]>>3 & 0xFF))

    # Compute complement side
    for i in range(77,152):

        # Decimal complement
        phase_shifters_dec_lst[i] = (~phase_shifters_dec_lst[152-i]) + 1

        # 10-bit complement
        phase_shifters_10_bits_lst[i] = ''
        for j in range(0,10):
            bit = phase_shifters_10_bits_lst[152-i][j]
            if bit == '0':
                bit = '1'
            else:
                bit = '0'
            phase_shifters_10_bits_lst[i] += bit

        # 7-bit complement
        alpha_phase_shifters_7_bits_lst[i] = ''
        for j in range(0,7):
            bit = alpha_phase_shifters_7_bits_lst[152-i][j]
            if bit == '0':
                bit = '1'
            else:
                bit = '0'
            alpha_phase_shifters_7_bits_lst[i] += bit

    # Compute expected phase word for location Alpha 152
    phase_shifters_dec_lst[152] = phase_shifters_dec_lst[151] - increment - 4
    phase_shifters_dec_lst[152] = phase_shifters_dec_lst[152] % 1024
    phase_shifters_10_bits_lst[152] = ("{0:010b}".format(phase_shifters_dec_lst[152] & 0x3FF))
    alpha_phase_shifters_7_bits_lst[152] = ("{0:07b}".format(phase_shifters_dec_lst[152]>>3 & 0xFF))

    # Alpha side is inverted from Beta for the same phase increment
    for i in range(1,153):
        beta_phase_shifters_7_bits_lst[152-i] = alpha_phase_shifters_7_bits_lst[i]

    # Compute expected phase word for location Beta 152
    beta_phase_shifters_7_bits_lst[152] = ''
    for j in range(0,7):
        bit = alpha_phase_shifters_7_bits_lst[152][j]
        if bit == '0':
            bit = '1'
        else:
            bit = '0'
        beta_phase_shifters_7_bits_lst[152] += bit

    for i in range(1,153):
        if verbose:
            print(phase_shifters_num_lst[i], "\t", phase_shifters_dec_lst[i], \
                "\t", phase_shifters_10_bits_lst[i], "\t", alpha_phase_shifters_7_bits_lst[i],\
                 "\t", beta_phase_shifters_7_bits_lst[i])

    alpha_phase_word_lst = []
    beta_phase_word_lst = []
    for i in range(0, len(ds_lst)):
        alpha_phase_word_lst.append(alpha_phase_shifters_7_bits_lst[ds_lst[i]])
        beta_phase_word_lst.append(beta_phase_shifters_7_bits_lst[ds_lst[i]])

    return alpha_phase_word_lst, beta_phase_word_lst

# NOTE: EACH DELAY SWITCH HAS 7 SETTINGS.  
# EACH DELAY SWITCH HAS THE ZERO DELAY AND PHASE SHIFT SIDES.  
# THERE ARE 7 BITS TO CONTROL THE ZERO DELAY SIDE AND THE OPPOSITE 7 BITS TO CONTROL THE PHASE SHIFT SIDE
def swcr_cal_delay_switch_bits(increment, ds, verbose):

    phase_shifters_dec_lst = []
    phase_shifters_10_bits_lst = []
    phase_shifters_multiples_7_bits_lst = []
    phase_shifters_complements_7_bits_lst = []

    for i in range(0,77):
        phase_shifters_dec_lst.append(i)
        phase_shifters_10_bits_lst.append(i)
        phase_shifters_multiples_7_bits_lst.append(i)
        phase_shifters_complements_7_bits_lst.append(i)

    # Compute integer multiples
    for i in range(1,77):
        phase_shifters_dec_lst[i] = increment*i+4

    # Mod to stay below 1024 (10-bit)
    for i in range(1,77):
        phase_shifters_dec_lst[i] = phase_shifters_dec_lst[i] % 1024

    for i in range(1,77):
        phase_shifters_10_bits_lst[i] = ("{0:010b}".format(phase_shifters_dec_lst[i] & 0x3FF))
        phase_shifters_multiples_7_bits_lst[i] = ("{0:07b}".format(phase_shifters_dec_lst[i]>>3 & 0xFF))

    # Compute complements
    for i in range(1,77):
        phase_shifters_complements_7_bits_lst[i] = ''
        for j in range(0,7):
            bit = phase_shifters_multiples_7_bits_lst[i][j]
            if bit == '0':
                bit = '1'
            else:
                bit = '0'
            phase_shifters_complements_7_bits_lst[i] += bit

    # Populate alpha and beta 7-bit outputs
    phase_shifters_num_lst = []
    alpha_zero_delay_phase_shifters_7_bits_lst = []
    alpha_phase_shift_phase_shifters_7_bits_lst = []
    beta_zero_delay_phase_shifters_7_bits_lst = []
    beta_phase_shift_phase_shifters_7_bits_lst = []

    for i in range(0,153):
        phase_shifters_num_lst.append(i)
        alpha_zero_delay_phase_shifters_7_bits_lst.append(i)
        alpha_phase_shift_phase_shifters_7_bits_lst.append(i)
        beta_zero_delay_phase_shifters_7_bits_lst.append(i)
        beta_phase_shift_phase_shifters_7_bits_lst.append(i)

    # ALPHA
    # Alpha zero delay side of Delay Units 75 to 1 get integer multiples 1 to 75
    for i in range (75,0,-1):
        alpha_zero_delay_phase_shifters_7_bits_lst[i] = phase_shifters_multiples_7_bits_lst[75-i+1]

    # Alpha phase shift side of Delay Units 75 to 1 get complements 1 to 75
    for i in range (75,0,-1):
        alpha_phase_shift_phase_shifters_7_bits_lst[i] = phase_shifters_complements_7_bits_lst[75-i+1]

    # Alpha phase shift side of Delay Units 77 to 152 get integer multiple 1 to 76
    for i in range (77,153):
        alpha_phase_shift_phase_shifters_7_bits_lst[i] = phase_shifters_multiples_7_bits_lst[i-77+1]

    # Alpha zero delay side of Delay Units 77 to 152 get complemens 1 to 76
    for i in range (77,153):
        alpha_zero_delay_phase_shifters_7_bits_lst[i] = phase_shifters_complements_7_bits_lst[i-77+1]

    # For Delay Units 76
        alpha_zero_delay_phase_shifters_7_bits_lst[76] = ("{0:07b}".format(0x7F))
        alpha_phase_shift_phase_shifters_7_bits_lst[76] = ("{0:07b}".format(0x0))

    # BETA
    # Beta zero delay side of Delay Units 77 to 152 get integer multiples 1 to 76
    for i in range (77,153):
        beta_zero_delay_phase_shifters_7_bits_lst[i] = phase_shifters_multiples_7_bits_lst[i-77+1]

    # Beta phase shift side of Delay Units 77 to 152 get complements 1 to 76
    for i in range (77,153):
        beta_phase_shift_phase_shifters_7_bits_lst[i] = phase_shifters_complements_7_bits_lst[i-77+1]

    # Beta phase shift side of Delay Units 75 to 1 get integer multiple 1 to 75
    for i in range (75,0,-1):
        beta_phase_shift_phase_shifters_7_bits_lst[i] = phase_shifters_multiples_7_bits_lst[75-i+1]

    # Beta zero delay side of Delay Units 75 to 1 get complemens 1 to 75
    for i in range (75,0,-1):
        beta_zero_delay_phase_shifters_7_bits_lst[i] = phase_shifters_complements_7_bits_lst[75-i+1]

    # For Delay Units 76
    beta_zero_delay_phase_shifters_7_bits_lst[76] = ("{0:07b}".format(0x7F))
    beta_phase_shift_phase_shifters_7_bits_lst[76] = ("{0:07b}".format(0x0))

    if verbose:
        print ("DS \t\t  Alpha \t\t Beta")
        print ("\t zero-delay \t phase-shift \t zero-delay \t phase-shift")
    for i in range(1,153):
        if verbose:
            print(phase_shifters_num_lst[i], "\t", alpha_zero_delay_phase_shifters_7_bits_lst[i], \
                "\t", alpha_phase_shift_phase_shifters_7_bits_lst[i], "\t", beta_zero_delay_phase_shifters_7_bits_lst[i],\
                 "\t", beta_phase_shift_phase_shifters_7_bits_lst[i])

    alpha_zero_delay_phase_word_lst = alpha_zero_delay_phase_shifters_7_bits_lst[ds]
    alpha_phase_shift_phase_word_lst = alpha_phase_shift_phase_shifters_7_bits_lst[ds]
    beta_zero_delay_phase_word_lst = beta_zero_delay_phase_shifters_7_bits_lst[ds]
    beta_phase_shift_phase_word_lst = beta_phase_shift_phase_shifters_7_bits_lst[ds]

    return alpha_zero_delay_phase_word_lst, alpha_phase_shift_phase_word_lst, beta_zero_delay_phase_word_lst, beta_phase_shift_phase_word_lst

# Reference CSP Algorithm Manual - Beam Steer Test
def swcr_scan_limit_check(kSineAlpha, kSineBeta, verbose):
    
    gamma = 1.207234
    pulse_center_freq = 442.0   # Default to 442 MHz

    # Thresholds
    uv_threshold = np.sin(1.055924)  # 60.5 degrees
    w_threshold = np.cos(1.230457)  # 70.5 degrees
    sin_el_threshold = np.sin(0.01658063)   # 0.95 degress

    if verbose:
        print ("****************************************************************")

    if verbose:
        print ("Threshold: uv = %f, w = %f, sin_el = %f" % \
               (uv_threshold, w_threshold, sin_el_threshold))

    K = gamma * pulse_center_freq
    u = -kSineBeta/K
    v = kSineAlpha/K
    w = np.sqrt(1 - u*u - v*v)
    sin_el = v*np.cos(0.785398) + w*np.sin(0.785398)    # el_b is boresight elevation at 45 degree in radians

    if verbose:
        print ("kSineAlpha = %d, kSineBeta = %d, K = %f, u = %f, v = %f, w = %f, sin_el = %f" % \
               (kSineAlpha, kSineBeta, K, u, v, w, sin_el))

    # Check against thresholds
    all_passed = 0
    sl_passed = 0
    sl_check1_passed = 0
    sl_check2_passed = 0
    sin_el_passed = 0

    # Elevation test
    if sin_el > sin_el_threshold:
        sin_el_passed = 1
        if verbose:
            print ("Passed sin_el check")

    # u, v, w tests
    if ((abs(u) < uv_threshold) and (abs(v) < uv_threshold) and (w > w_threshold)):
        sl_passed = 1
        sl_check1_passed = 1
        sl_check2_passed = 1
        if verbose:
            print ("Passed 1st check")
    else:
        if verbose:
            print ("Failed 1st check")
        # One of u, v, or w has failed, but elevation passed.  Recompute
        # rounded values of u, v, and w, then check them again.
        if sin_el_passed:
            u = -(kSineBeta - np.sign(kSineBeta)/2)/K
            v = -(kSineAlpha - np.sign(kSineAlpha)/2)/K
            w = np.sqrt(1 - u*u - v*v)

            if verbose:
                print ("2nd results: u = %f, v = %f, w = %f" % \
                       (u, v, w))

            # Re-test u, v and w
            if ((abs(u) < uv_threshold) and (abs(v) < uv_threshold) and (w > w_threshold)):
                sl_passed = 1
                sl_check2_passed = 1
                if verbose:
                    print ("Passed 2nd check")
            else:
                if verbose:
                    print ("Failed 2nd check")

    # Set overall test result
    all_passed = 0
    if (sl_passed == 1 and sin_el_passed == 1):
        all_passed = 1

    if verbose:
        print ("all_passed = %d, sl_passed = %d, sin_el_passed = %d" % \
               (all_passed, sl_passed, sin_el_passed))

    return (all_passed, sl_passed, sin_el_passed, sl_check1_passed, sl_check2_passed)


# Search in_str for the exact num_of_ones
# Assume in_str is string of binary, example '0100101"
def num_of_ones(in_str):
    sum = 0
    for i in range(0,len(in_str)):
        sum += int(in_str[i])
    return sum


