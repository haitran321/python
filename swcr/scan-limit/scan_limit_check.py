#!/usr/bin/env python3

import sys

parent_dir = ".."
sys.path.append(parent_dir)
from util import *

if __name__ == '__main__':

    kSineAlpha = 511
    kSineBeta = 511

    num_arg = len(sys.argv)
    test_arg = sys.argv[1]
    if num_arg == 4:
        kSineAlpha = int(sys.argv[2])
        kSineBeta = int(sys.argv[3])
    else:
        print("Invalid command line inputs.  Using default KSine Alpha and Beta")

    if test_arg == "single":
        scan_limit_check = swcr_scan_limit_check(kSineAlpha, kSineBeta, True)
    else:   #"file"
        ofile = open("swcr_scan_limit_check_results.csv", 'w')

        angles_file = open("D:\\Work\\Dev\\Projects\\SWCR\\Baseline Data Collection\\phase-delay-reader\\scan-limit-test-angles.csv", 'r')
        test_num_lst = []
        beta_lst = []
        alpha_lst = []
        swc_sl_lst = []
        swc_sl_check_lst = []

        # Parsing scan limit ksine file
        for x in range(0,258):
            data = angles_file.readline()
            currentline = data.split(",")
            test_num_lst.append(int(currentline[0]))
            beta_lst.append(int(currentline[1]))
            alpha_lst.append(int(currentline[2]))
            swc_sl_lst.append(int(currentline[3]))
            if int(currentline[3]) == 4030:
                swc_sl_check_lst.append(1)
            else:
                swc_sl_check_lst.append(0)
        # Process ksine data
        # Write file header
        ofile.write("test_num,kSineBeta,kSineAlpha,swc_value,swc_sl_passed,")
        ofile.write("swc_all_passed,swc_diff_swcr,swcr_sl_passed,sin_el_passed,sl_check1_passed,sl_check2_passed\n")
        for x in range (0,258):
            if x == 78:
                print (test_num_lst[x], beta_lst[x], alpha_lst[x])
                scan_limit_check = swcr_scan_limit_check(alpha_lst[x], beta_lst[x], True)
            else:
                scan_limit_check = swcr_scan_limit_check(alpha_lst[x], beta_lst[x], False)

            ofile.write(str(test_num_lst[x]) + "," + \
                        str(beta_lst[x]) + "," + \
                        str(alpha_lst[x]) + "," + \
                        str(swc_sl_lst[x]) + "," + \
                        str(swc_sl_check_lst[x]) + ",")
            swc_diff_swcr = 0
            if swc_sl_check_lst[x] != scan_limit_check[0]:
                swc_diff_swcr = 1
            ofile.write(str(scan_limit_check[0]) + "," + \
                        str(swc_diff_swcr) + "," + \
                        str(scan_limit_check[1]) + "," + \
                        str(scan_limit_check[2]) + "," + \
                        str(scan_limit_check[3]) + "," + \
                        str(scan_limit_check[4]) + "," + "\n")

        angles_file.close()
        ofile.close()



