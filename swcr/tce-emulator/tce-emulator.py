# Server program

from socket import *
from struct import *
from time import sleep

# Set the socket parameters
localhost = "172.16.80.91"
port = 9005
buf = 1024
addr = (localhost,port)

# Create socket and bind to address
UDPSock = socket(AF_INET, SOCK_DGRAM)
UDPSock.bind(addr)

# Outgoing socker parameters
out_host = "172.16.80.110"
out_port = 8005
out_addr = (out_host,out_port)

# Create socket
out_UDPSock = socket(AF_INET, SOCK_DGRAM)

calRpt = ''
CAL_PXI_CALIBRATION_CMD_MSG = 3
CAL_PXI_CALIBRATION_RPT_MSG = 5

Tx_Alpha = 0
Tx_Beta = 1
Rx_Alpha = 2
Rx_Beta = 3

# Processing measurements from Site TWGS Log
twgs_log = "twgs.log.507"

num_dda = 153
num_bit = 8
alpha = []
beta = []
default_phases = [0.0, 2.51, 5.6, 11.25, 22.5, 45.0, 90.0, 180.0]
alpha_measured_phases_dda = [24, 100, 124]
beta_measured_phases_dda = [17, 60, 116]
alpha_measured_phases = [[-149.1, -151.6, -154.1, -160.0, -171.0, 166.4, 123.1, 30.5],\
                         [-147.2, -154.9, -157.8, -162.8, -173.9, 162.9, 118.4, 26.8],\
                         [-149.7, 0.0, -159.5, -170.7, 165.4, 120.7, 31.0, 0.0, -149.7]]
beta_measured_phases = [[-177.2, 177.2, 173.7, 168.0, 156.8, 134.6, 89.4, -0.51],\
                        [-177.1, 0.0, 173.1, 162.1, 139.6, 93.9, 3.5, -177.0],\
                        [-176.3, -179.3, 178.0, 172.1, 161.6, 138.9, 93.2, 3.3]]

def getData():
    # Create data array
    for i in range (0,num_dda):
        alpha.append([])
        beta.append([])

    # Set default data
    for dda in range (0,num_dda):
        for bit in range(0,num_bit):
            alpha[dda].append(default_phases[bit])
            beta[dda].append(default_phases[bit])

    # Set ref data from twgs log file
    ifile = open(twgs_log, 'r')

    num_pbp = 0 
    pbp_to_read = 10000
    line_to_search_for_data = 20

    reading = True

    while reading == True:
        line = ifile.readline()
        if len(line) == 0:
            reading = False

        if num_pbp >= pbp_to_read:
                reading = False

        # Get DDA number
        if line.find('DDA#: ') > -1:
            start_loc = line.find("DDA#: ") + len("DDA#: ")
            dda = int(line[start_loc:])

        # Get Calibration Type
        if line.find('Calibration Type: ') > -1:
            # Get the cal type
            start_loc = line.find("Calibration Type: ") + len("Calibration Type: ")
            cal_type_str = line[start_loc:start_loc+4]

            if cal_type_str == 'Rx_A' or cal_type_str == 'Rx_B':
                for i in range(0,line_to_search_for_data):
                    line = ifile.readline()
                    # Get Phase Error
                    if line.find('TWGS1_StatusManager - PhaseErr: ') > -1:
                        start_loc = line.find("TWGS1_StatusManager - PhaseErr: ") + len("TWGS1_StatusManager - PhaseErr: ")
                        phase = float(line[start_loc:])

                        if cal_type_str == 'Rx_A':
                            alpha[dda][0] = phase
                            # Update the phases for the other bits
                            for bit in range(1,num_bit):
                                if dda in alpha_measured_phases_dda:
                                    # DDA with actual bit measurements
                                    ind = alpha_measured_phases_dda.index(dda)
                                    alpha[dda][bit] = alpha_measured_phases[ind][bit]
                                    print("***Using actual measurement: alpha dda = %d, bit = %d, phase = %f" % (dda, bit, alpha[dda][bit]))
                                else:
                                    # DDA with only boresight measurement
                                    alpha[dda][bit] = alpha[dda][0] + default_phases[bit]
                        if cal_type_str == 'Rx_B':
                            beta[dda][0] = phase
                            # Update the phases for the other bits
                            for bit in range(1,num_bit):
                                if dda in beta_measured_phases_dda:
                                    # DDA with actual bit measurements
                                    ind = beta_measured_phases_dda.index(dda)
                                    beta[dda][bit] = beta_measured_phases[ind][bit]
                                    print("***Using actual measurement: beta dda = %d, bit = %d, phase = %f" % (dda, bit, beta[dda][bit]))
                                else:
                                    beta[dda][bit] = beta[dda][0] + default_phases[bit]

                        break

                num_pbp += 1

    ifile.close()

def GenCalRpt(txAlpha, txBeta, rxAlpha, rxBeta):

    # Create default data
    chasissNumber = 0
    boardNumber = 0
    calDataType = 0
    ddaOperabilityStatus = 1
    freqErr = 28.170944
    ampErr = 1.005241
    refPwr = 5.803215
    sigPwr = 5.848618
    fullScanFlagsRpt = 0 # TODO: Get this from the cmd

    # Create hardcoded measurements data
    measurements = pack("")
    Measurement_0_Freq = 85300000.000000
    Measurement_0_Pwr = 5.846678
    Measurement_0_Phase = -1.276179
    Measurement_0_SFDR = 75.035683
    Measurement_1_Freq = 85300000.000000
    Measurement_1_Pwr = 5.852531
    Measurement_1_Phase = -1.277120
    Measurement_1_SFDR = 74.744141
    Measurement_2_Freq = 85300000.000000
    Measurement_2_Pwr = 5.846676
    Measurement_2_Phase = -1.275332
    Measurement_2_SFDR = 74.760437
    Measurement_3_Freq = 85300000.000000
    Measurement_3_Pwr = 5.848585
    Measurement_3_Phase = -1.280388
    Measurement_3_SFDR = 74.851250

    measurements = pack(">ffffffffffffffff", Measurement_0_Freq, Measurement_0_Pwr, Measurement_0_Phase, Measurement_0_SFDR, \
                  Measurement_1_Freq, Measurement_1_Pwr, Measurement_1_Phase, Measurement_1_SFDR, \
                  Measurement_2_Freq, Measurement_2_Pwr, Measurement_2_Phase, Measurement_2_SFDR, \
                  Measurement_3_Freq, Measurement_3_Pwr, Measurement_3_Phase, Measurement_3_SFDR)
 
    numRecord = 0

    # Create record
    txAlphaRec = pack("")
    txBetaRec = pack("")
    rxAlphaRec = pack("")
    rxBetaRec = pack("")
    if txAlpha[0] != 0:
        numRecord += 1
        calibrationType = Tx_Alpha
        ddaNumber = txAlpha[0]
        bit = txAlpha[1]
        phaseErr = alpha[ddaNumber][bit]
        txAlphaRec = pack(">llllllfffffl", chasissNumber, boardNumber, calibrationType, calDataType, ddaNumber, ddaOperabilityStatus,\
                          freqErr, ampErr, phaseErr, refPwr, sigPwr, fullScanFlagsRpt)
        txAlphaRec += measurements

    if txBeta[0] != 0:
        numRecord += 1
        calibrationType = Tx_Beta
        ddaNumber = txBeta[0]
        bit = txBeta[1]
        phaseErr = beta[ddaNumber][bit]
        txBetaRec = pack(">llllllfffffl", chasissNumber, boardNumber, calibrationType, calDataType, ddaNumber, ddaOperabilityStatus,\
                         freqErr, ampErr, phaseErr, refPwr, sigPwr, fullScanFlagsRpt)
        txBetaRec += measurements

    if rxAlpha[0] != 0:
        numRecord += 1
        calibrationType = Rx_Alpha
        ddaNumber = rxAlpha[0]
        bit = rxAlpha[1]
        phaseErr = alpha[ddaNumber][bit]
        print (ddaNumber, phaseErr)
        rxAlphaRec = pack(">llllllfffffl", chasissNumber, boardNumber, calibrationType, calDataType, ddaNumber, ddaOperabilityStatus,\
                          freqErr, ampErr, phaseErr, refPwr, sigPwr, fullScanFlagsRpt)
        rxAlphaRec += measurements

    if rxBeta[0] != 0:
        numRecord += 1
        calibrationType = Rx_Beta
        ddaNumber = rxBeta[0]
        bit = rxBeta[1]
        phaseErr = beta[ddaNumber][bit]
        print (ddaNumber, phaseErr)
        rxBetaRec = pack(">llllllfffffl", chasissNumber, boardNumber, calibrationType, calDataType, ddaNumber, ddaOperabilityStatus,\
                         freqErr, ampErr, phaseErr, refPwr, sigPwr, fullScanFlagsRpt)
        rxBetaRec += measurements


    # Generate Cal Rpt
    calRpt = 1
    msgID = CAL_PXI_CALIBRATION_RPT_MSG
    pbpID = 100
    recordLen = 112 * numRecord
    msgLen = 32 + recordLen
    msgTime1 = 0
    msgTime2 = 0
    recvID = 0
    # Pack header
    calRpt = pack(">llllllll", msgID, pbpID, msgLen, msgTime1, msgTime2, numRecord, recordLen, recvID)

    calRpt += txAlphaRec + txBetaRec + rxAlphaRec + rxBetaRec

    return calRpt

# Get data
print("Pharsing data from TWGS Log")
getData()
print("Finished pharsing data from TWGS Log")

# Receive messages
last_tx_alpha_dda = 0
last_tx_beta_dda = 0
last_rx_alpha_dda = 0
last_rx_beta_dda = 0
cmd_counter = 0
bit_counter = 0
reset_bit_counter = False
last_cmd_all_zeros = True
while 1:
    data,addr = UDPSock.recvfrom(buf)
    if not data:
        print ("Client has exited!")
        break
    elif data == "exit":
        print ("Commanded to exit from the sender")
        break
    else:
#       print ("\nReceived message '", data,"'")
        send_rpt = False
        msgId = unpack(">l", data[0:4])[0]
        print ("msgId = %d" % msgId)

        if msgId == CAL_PXI_CALIBRATION_CMD_MSG:

            cmdTxAlpha = unpack(">l", data[32:36])[0]
            cmdTxBeta = unpack(">l", data[36:40])[0]
            cmdRxAlpha = unpack(">l", data[40:44])[0]
            cmdRxBeta = unpack(">l", data[44:48])[0]
            fullScan = unpack(">l", data[48:52])[0]
            print ("txAlpha = %d, txBeta = %d, rxAlpha = %d, rxBeta = %d, fullScan = %d" % \
                    (cmdTxAlpha, cmdTxBeta, cmdRxAlpha, cmdRxBeta, fullScan))

            # Check for all zeros
            # if all zeros, send the report
            if cmdTxAlpha == 0 and cmdTxBeta == 0 and cmdRxAlpha == 0 and cmdRxBeta == 0:
                if last_cmd_all_zeros == False:
                    send_rpt = True
                    cmd_counter = 0
                    last_cmd_all_zeros = True

            else:
                bit_counter += 1
                cmd_counter += 1
                if cmd_counter == 4:
                    send_rpt = True
                    cmd_counter = 0

                if cmdTxAlpha != last_tx_alpha_dda or cmdTxBeta != last_tx_beta_dda or \
                    cmdRxAlpha != last_rx_alpha_dda or cmdRxBeta != last_rx_beta_dda:

                    if last_cmd_all_zeros == False:
                        send_rpt = True
                        cmd_counter = 0

                    last_tx_alpha_dda = cmdTxAlpha
                    last_tx_beta_dda = cmdTxBeta
                    last_rx_alpha_dda = cmdRxAlpha
                    last_rx_beta_dda = cmdRxBeta

                last_cmd_all_zeros = False

        if send_rpt:

            # Detemine what bit
            bit = 0
            if bit_counter >= 4 and bit_counter < 8:
                bit = 0
            elif bit_counter >= 8 and bit_counter < 12:
                bit = 1
            elif bit_counter >= 12 and bit_counter < 16:
                bit = 2
            elif bit_counter >= 16 and bit_counter < 20:
                bit = 3
            elif bit_counter >= 20 and bit_counter < 24:
                bit = 4
            elif bit_counter >= 24 and bit_counter < 28:
                bit = 5
            elif bit_counter >= 28 and bit_counter < 32:
                bit = 6
            elif bit_counter >= 32:
                bit = 7
                if reset_bit_counter == True:
                    bit_counter = 0
                    reset_bit_counter = False
                else:
                    reset_bit_counter = True

            print ("Sending rpt: txA = %d, txB = %d, rxA = %d, rxB = %d, bit = %d" % \
                    (last_tx_alpha_dda, last_tx_beta_dda, last_rx_alpha_dda, last_rx_beta_dda, bit))

            txAlpha = [last_tx_alpha_dda, bit]   # replace bit 0 with the commanded bit
            txBeta = [last_tx_beta_dda, bit]
            rxAlpha = [last_rx_alpha_dda, bit]
            rxBeta = [last_rx_beta_dda, bit]
            calRpt = GenCalRpt(txAlpha, txBeta, rxAlpha, rxBeta)
            out_UDPSock.sendto(calRpt, out_addr)

# Close socket
UDPSock.close()


