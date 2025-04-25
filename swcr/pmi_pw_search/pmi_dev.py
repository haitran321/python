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

    step1p_min = 0
    step1p_max = 356
    step1n_min = -304
    step1n_max = -1
    alpha_min = -371
    alpha_max = 464
    beta_min = -464
    beta_max = 464

#   phaseShiftPerBit = [180.0, 90.0, 45.0, 22.5, 11.25, 5.6, 2.8]

    ds_min = 1
    ds_max = 152

    # RESULTS:
    # [-304, 356] # 9999 is 55
    pattern = ['0000001','0000010','0000100','0001000','0010000','0100000','1000000']

    ofile = open("results.csv", 'w')
    
    # Write csv header
    ofile.write("Alpha DS Number,Beta DS Number")
    for i in range(0,7):
        ofile.write("," + pattern[i])
    ofile.write("\n")

    # STEP 1 a/b
#   print ("DS \t PW  \t DS")
    ofile.write("=====STEP 1 a/b - Alpha and Beta (" + str(step1n_min) + "," + str(step1p_max) + ")==================\n")
    print("\n=====STEP 1 a/b - Alpha and Beta (" + str(step1n_min) + "," + str(step1p_max) + ")==================")
    step1a_remain_ds_lst = []
    step1a_remain_found_lst = []
    step1a_remain_results_lst = []
    step1b_remain_ds_lst = []
    step1b_remain_found_lst = []
    step1b_remain_results_lst = []
    for ds in range(ds_min,ds_max):
        found = [False,False,False,False,False,False,False]
        results = [9999,9999,9999,9999,9999,9999,9999]
        # Search positive phase words first
        for pw in range(step1p_min,step1p_max):
            swcr_phase_words = swcr_cal_delay_switch_bits(pw,ds,False)

            # Check the zero-delay side returns
            alpha = swcr_phase_words[0]

            for i in range(0,7):
                if alpha == pattern[i] and found[i] == False:
                    found[i] = True  
                    results[i] = pw

            # Break if found all
            if not (9999 in results):
                break;
          
        # Search negative phase words  
        for pw in range(step1n_max,step1n_min,-1):
            swcr_phase_words = swcr_cal_delay_switch_bits(pw,ds,False)

            # Check the zero-delay side returns
            alpha = swcr_phase_words[0]

            for i in range(0,7):
                if alpha == pattern[i] and found[i] == False:
                    found[i] = True  
                    results[i] = pw    
                    
            # Break if found all
            if not (9999 in results):
                break;   

        ofile.write(str(ds) + "," + str(152-ds))
        for i in range(0,7):
            ofile.write("," + str(results[i]))
#           print (ds, "\t", results[i], "\t", pattern[i])
        ofile.write("\n")

        # Check to see if there is any remaining 9999
        if (9999 in results):
            step1a_remain_ds_lst.append(ds)  
            step1b_remain_ds_lst.append(152-ds)
            step1a_remain_found_lst.append(found)
            step1a_remain_results_lst.append(results)
        step1b_remain_found_lst = step1a_remain_found_lst
        step1b_remain_results_lst = step1a_remain_results_lst

    print ("Number of Remain Alpha DS after STEP 1 = ", len(step1a_remain_ds_lst))
    print ("Number of Remain Beta DS after STEP 1 = ", len(step1b_remain_ds_lst))
    
    # STEP 2a
    ofile.write("=====STEP 2a - Alpha Only (" + str(alpha_min) + "," + str(alpha_max) + ")==================\n")
    print("\n=====STEP 2a - Alpha Only (" + str(alpha_min) + "," + str(alpha_max) + ")==================")
    step2a_remain_ds_lst = []
    step2a_remain_found_lst = []
    step2a_remain_results_lst = []
    for i in range(0,len(step1a_remain_ds_lst)):
        ds = step1a_remain_ds_lst[i]
        found = step1a_remain_found_lst[i]
        results = step1a_remain_results_lst[i]
        for pw in range(alpha_min,alpha_max):
            swcr_phase_words = swcr_cal_delay_switch_bits(pw,ds,False)

            # Check the zero-delay side returns
            alpha = swcr_phase_words[0]

            for i in range(0,7):
                if alpha == pattern[i] and found[i] == False:
                    found[i] = True
                    results[i] = pw

            # Break if found all
            if not (9999 in results):
                break;

        ofile.write(str(ds))
        for i in range(0,7):
            ofile.write("," + str(results[i]))
#           print (ds, "\t", results[i], "\t", pattern[i])
        ofile.write("\n")

        # Check to see if there is any remaining 9999
        if (9999 in results):
            step2a_remain_ds_lst.append(ds)
            step2a_remain_found_lst.append(found)
            step2a_remain_results_lst.append(results)

    print ("Number of Remain Alpha DS after STEP 2a = ", len(step2a_remain_ds_lst))

    # STEP 3a
    print("\n=====STEP 3a - Alpha Only (" + str(alpha_min) + "," + str(alpha_max) + ")==================")
    for i in range(0,len(step2a_remain_ds_lst)):
        ds = step2a_remain_ds_lst[i]

        # Open ds file
        ds_ofile = open("alpha_" + str(ds) + ".txt", 'w')

        for pw in range(alpha_min,alpha_max):
            swcr_phase_words = swcr_cal_delay_switch_bits(pw,ds,False)

            # Check the zero-delay side returns
            alpha = swcr_phase_words[0]

            sum = num_of_ones(alpha)
            if sum > 1:
                ds_ofile.write(str(ds))
                ds_ofile.write("," + str(pw) + "," + alpha + "\n")

        ds_ofile.close()

    # STEP 2b
    ofile.write("=====STEP 2b - Beta Only (" + str(beta_min) + "," + str(beta_max) + ")==================\n")
    print("\n=====STEP 2b - Beta Only (" + str(beta_min) + "," + str(beta_max) + ")==================")
    step2b_remain_ds_lst = []
    step2b_remain_found_lst = []
    step2b_remain_results_lst = []
    for i in range(0,len(step1b_remain_ds_lst)):
        ds = step1b_remain_ds_lst[i]
        found = step1b_remain_found_lst[i]
        results = step1b_remain_results_lst[i]
        for pw in range(beta_min,beta_max):
            swcr_phase_words = swcr_cal_delay_switch_bits(pw,ds,False)

            # Check the zero-delay side returns
            beta = swcr_phase_words[2]

            for i in range(0,7):
                if beta == pattern[i] and found[i] == False:
                    found[i] = True
                    results[i] = pw

            # Break if found all
            if not (9999 in results):
                break;

        ofile.write(str(ds))
        for i in range(0,7):
            ofile.write("," + str(results[i]))
#           print (ds, "\t", results[i], "\t", pattern[i])
        ofile.write("\n")

        # Check to see if there is any remaining 9999
        if (9999 in results):
            step2b_remain_ds_lst.append(ds)
            step2b_remain_found_lst.append(found)
            step2b_remain_results_lst.append(results)

    print ("Number of Remain Beta DS after STEP 2b = ", len(step2b_remain_ds_lst))

    ofile.close()

    # STEP 3b
    print("\n=====STEP 3b - Beta Only (" + str(beta_min) + "," + str(beta_max) + ")==================")
    for i in range(0,len(step2b_remain_ds_lst)):
        ds = step2b_remain_ds_lst[i]

        # Open ds file
        ds_ofile = open("beta_" + str(ds) + ".txt", 'w')

        for pw in range(beta_min,beta_max):
            swcr_phase_words = swcr_cal_delay_switch_bits(pw,ds,False)

            # Check the zero-delay side returns
            beta = swcr_phase_words[2]

            sum = num_of_ones(beta)
            if sum > 1:
                ds_ofile.write(str(ds))
                ds_ofile.write("," + str(pw) + "," + beta + "\n")

        ds_ofile.close()

        


    
