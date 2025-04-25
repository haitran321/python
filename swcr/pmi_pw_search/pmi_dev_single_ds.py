#!/usr/bin/env python3

import sys

parent_dir = ".."
sys.path.append(parent_dir)
from util import *

if __name__ == '__main__':

    # Alpha max [-371, 464] while Beta is 0 
    # Beta max [464, -464] while Alpha is 0
    # Most negative when both Alpha and Beta have the same value is -304
    # Most positive when both Alpha and Beta have the same value is 356

    # SEARCH SEQUENCE:
    # Goal: For each Delay Switch (DS) location, search 10-bit phase word that produces a 7-bit phase shift setting with one bit set at a time.  
    # If not possible, set multiple bits and interpret differential results
    #
    # Step 1a/b: Use the same phase words [-304, 356] for both Alpha and Beta for all DS
    # Step 2a: Use the full range of possible Alpha phase words for the remaining Alpha DS that didn't have answer from Step 1a
    # Step 3a: Manual search Alpha phase words for the remaining Alpha DS that didn't have answer from Step 2a - using differential 
    # Step 2b: Use the full range of possible Beta phase words for the remaining Beta DS that didn't have answer from Step 1b
    # Step 3b: Manual search Beta phase words for the remaining Beta DS that didn't have answer from Step 2b - using differential 
    # 
    # Steps a's are Alpha
    # Steps b's are Beta


#   phaseShiftPerBit = [180.0, 90.0, 45.0, 22.5, 11.25, 5.6, 2.8]

    ksine_min = 0
    ksine_max = 356
    ds = 140 

    # RESULTS:
    # [-304, 356] # 9999 is 55
    pattern = ['0000001','0000010','0000100','0001000','0010000','0100000','1000000']

    alpha_found = [False,False,False,False,False,False,False]
    alpha_results = [9999,9999,9999,9999,9999,9999,9999]

    beta_found = [False,False,False,False,False,False,False]
    beta_results = [9999,9999,9999,9999,9999,9999,9999]

    # Search positive phase words first
    for pw in range(ksine_min,ksine_max):
        swcr_phase_words = swcr_cal_delay_switch_bits(pw,ds,False)

        # Check the zero-delay side returns
        alpha = swcr_phase_words[0]
        beta = swcr_phase_words[2]

        for i in range(0,7):
            if alpha == pattern[i] and alpha_found[i] == False:
                alpha_found[i] = True  
                alpha_results[i] = pw

            if beta == pattern[i] and beta_found[i] == False:
                beta_found[i] = True  
                beta_results[i] = pw


    print (alpha_results)
    print (beta_results)
        


    
