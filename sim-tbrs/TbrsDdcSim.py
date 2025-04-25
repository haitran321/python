#!/usr/bin/env python

from __future__ import division

import wx

from pylab import *
from fir import FIR
from util import readIfData
from util import writeBasebandData
from util import plotSpectrumPair
from util import plotTimeDomainPair
from util import plotMfMagnitude
from util import TaylorWindow
from util import parseInputParamsFile
from math import pi, cos, sin
from os import walk
from os import mkdir

class App(wx.App):


    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)

    def OnInit(self):


        # Let user select IF data file to process. Use wxPython
        # dialog boxes to make this easy.

        ptList = ['1','2','3','4','5','6','7','8','9','10','11']

        dlg = wx.SingleChoiceDialog(None,
                'Pulse Type?', 'Select Pulse Type',
               ptList)
        if dlg.ShowModal() == wx.ID_OK:
            ptString = dlg.GetStringSelection()
            ptIndex = dlg.GetSelection()

        dlg.Destroy()

        selPT = int(ptString)
        # print "Pulse type %d selected" % selPT

        ptTwoDigit = "%02d" % selPT
        endPattern = "PT" + ptTwoDigit + ".dat"

        # print "File search pattern = %s" % endPattern


        # Get the list of file names from the IFdata folder. This is
        # where the nbvm.py program writes the data.
        tree = walk("IFdata")

        # Put the .dat filenames in a list
        for dir in tree:
            fileList = []
            for file in dir[2]:
                if file[-8:] == endPattern:
                    # print "file = %s" % file
                    fileList.append(file)


        # Check for empty list (i.e. no data files found for this
        # pulse type).
        numFilesFound = len(fileList)
        if numFilesFound < 1:
            print "Error! No data files found for pulse type %d" % selPT
            print "Try running TbrsIfSim.py to generate IF data."
            sys.exit()

        # Use dialog list box to get user filename selection
        datalist = [
                    ('IF Data File', fileList)
                    ]

        dlg = wx.SingleChoiceDialog(None,
                'IF Data File?', 'Select IF Data File',
               fileList)
        if dlg.ShowModal() == wx.ID_OK:
            fileName = dlg.GetStringSelection()
            fileNameIndex = dlg.GetSelection()

        dlg.Destroy()

        # Get flag to save png plot file
        pltFlag = 0
        dlg = wx.TextEntryDialog(None, "Save Plots?",
                'Save Plots?', '0')
        if dlg.ShowModal() == wx.ID_OK:
            response = dlg.GetValue()
        dlg.Destroy()

        try:
            pltFlag = int(response)
        except:
            pass

        proc(pltFlag,fileName)

        return True

class TbrsDDC(object):

    # Define any class variables (shared by all instances) here.

    def __init__(self,coefficientFileNames):

        # Initialize per instance variables here.

        # Vectors to hold plot data.
        self.pltDataDemod60  = 4*[0]
        self.pltDataDemod60f = 4*[0]
        self.pltDataDemod    = 4*[0]
        self.pltDataDemod5f  = 4*[0]
        self.pltData1_25     = 4*[0]
        self.pltData_125     = 4*[0]

        # Create FIR for quadrature demodulator LPFs (LPF1).
        self.iqFir = FIR(coefficientFileNames[0])

        # Create FIR for decimate by 4 LPF (LPF2).
        self.decBy4Fir = FIR(coefficientFileNames[1])

        # Create FIR for decimate by 10 LPF (LPF3).
        self.decBy10Fir = FIR(coefficientFileNames[2])

        # Create FIR for 25 microsecond GCW multi-pulse MF (MF25).
        self.mf25usec = FIR(coefficientFileNames[3])

        # Create FIR for 125 microsecond GCW multi-pulse MF (MF125).
        self.mf125usec = FIR(coefficientFileNames[4])

        # Set frequeny and period constants for down conversion.
        self.fs  = 60.0e6      # A/D sample rate.
        self.Ts  = 1/self.fs   # A/D sample period.
        self.f_H = 20.5*10**6  # HP center frequency.
        self.f_V = 23.5*10**6  # HP center frequency.

        self.f_lfm = 12*[0]
        self.f_lfm[0]  = 0        #   0: Not defined
        self.f_lfm[1]  = 0        #   1: 1   usec GCW
        self.f_lfm[2]  = 0        #   2: 10  usec GCW
        self.f_lfm[3]  = 1.0e6    #   3: 16  usec 1 MHz LFM
        self.f_lfm[4]  = 0        #   4: 25  usec GCW multi-pulse
        self.f_lfm[5]  = 1.0e6    #   5: 32  usec 1 MHz LFM
        self.f_lfm[6]  = 1.0e6    #   6: 64  usec 1 MHz LFM
        self.f_lfm[7]  = 0        #   7: 125 usec GCW multi-pulse
        self.f_lfm[8]  = 100.0e3  #   8: 128 usec 100 kHz LFM
        self.f_lfm[9]  = 1.0e6    #   9: 128 usec 1 MHz LFM
        self.f_lfm[10] = 100.0e3  #  10: 250 usec 100 kHz LFM
        self.f_lfm[11] = 1.0e6    #  11: 250 usec 1 MHz LFM

        self.tau_p = 12*[0]
        self.tau_p[0]  = 0         #   0: Not defined
        self.tau_p[1]  = 1.0e-6    #   1: 1   usec GCW
        self.tau_p[2]  = 10.0e-6   #   2: 10  usec GCW
        self.tau_p[3]  = 16.0e-6   #   3: 16  usec 1 MHz LFM
        self.tau_p[4]  = 25.0e-6   #   4: 25  usec GCW multi-pulse
        self.tau_p[5]  = 32.0e-6   #   5: 32  usec 1 MHz LFM
        self.tau_p[6]  = 64.0e-6   #   6: 64  usec 1 MHz LFM
        self.tau_p[7]  = 125.0e-6  #   7: 125 usec GCW multi-pulse
        self.tau_p[8]  = 128.0e-6  #   8: 128 usec 100 kHz LFM
        self.tau_p[9]  = 128.0e-6  #   9: 128 usec 1 MHz LFM
        self.tau_p[10] = 250.0e-6  #  10: 250 usec 100 kHz LFM
        self.tau_p[11] = 250.0e-6  #  11: 250 usec 1 MHz LFM

        self.alpha_r = [
                    1.0000, # PT  0, N/A
                    1.4400, # PT  1, 1   usec GCW
                    1.4750, # PT  2, 10  usec GCW
                    0.6900, # PT  3, 16  usec LFM 1 MHz
                    1.0000, # PT  4, 25  usec GCW
                    0.8050, # PT  5, 32  usec LFM 1 MHz
                    0.7300, # PT  6, 64  usec LFM 1 MHz
                    1.0000, # PT  7, 125 usec GCW
                    1.2600, # PT  8, 128 usec LFM 100 kHz
                    0.7550, # PT  9, 128 usec LFM 1 MHz
                    1.2400, # PT 10, 250 usec LFM 100 kHz
                    0.6950  # PT 11, 250 usec LFM 1 MHz
                  ]

        self.alpha_m = [
                    1.0000, # PT  0, N/A
                    1.1400, # PT  1, 1   usec GCW
                    1.1800, # PT  2, 10  usec GCW
                    0.6900, # PT  3, 16  usec LFM 1 MHz
                    1.0000, # PT  4, 25  usec GCW
                    0.7600, # PT  5, 32  usec LFM 1 MHz
                    0.6900, # PT  6, 64  usec LFM 1 MHz
                    1.0000, # PT  7, 125 usec GCW
                    1.1550, # PT  8, 128 usec LFM 100 kHz
                    0.6930, # PT  9, 128 usec LFM 1 MHz
                    1.1008, # PT 10, 250 usec LFM 100 kHz
                    0.6600  # PT 11, 250 usec LFM 1 MHz
                  ]

        # Number of pulse samples for each LFM pulse type.
        self.N_p = [
          1,   # PT  0, N/A
          1,   # PT  1, 1   usec GCW
          1,   # PT  2, 10  usec GCW
         20,   # PT  3, 16  usec LFM 1 MHz
          2,   # PT  4, 25  usec GCW
         40,   # PT  5, 32  usec LFM 1 MHz
         80,   # PT  6, 64  usec LFM 1 MHz
          2,   # PT  7, 125  usec GCW
         16,   # PT  8, 128 usec LFM 100 kHz
         160,  # PT  9, 128  usec LFM 1 MHz
         31 ,  # PT 10, 250 usec LFM 100 kHz
         312   # PT 11, 250 usec LFM 1 MHz
        ]

        # Taylor SLL parameter to achieve required SLL for each LFM pulse type.
        self.sll = [
          0,    # PT  0, N/A
          0,    # PT  1, 1   usec GCW
          0,    # PT  2, 10  usec GCW
         -31,   # PT  3, 16  usec LFM 1 MHz
          0,    # PT  4, 25  usec GCW
         -26,   # PT  5, 32  usec LFM 1 MHz
         -30,   # PT  6, 64  usec LFM 1 MHz
          0,    # PT  7, 125  usec GCW
         -13,   # PT  8, 128 usec LFM 100 kHz
         -29,   # PT  9, 128 usec LFM 1 MHz
         -13,   # PT 10, 250 usec LFM 100 kHz
         -31.5  # PT 11, 250 usec LFM 1 MHz
        ]
        self.nbar = 4 # Taylor weight nbar parameter.

        # Set variable member attributes to reasonable values.
        self.pulseType = 1
        self.numBasebandSamples = 100
        self.sigmaH = 3.0
        self.sigmaV = 3.0
        self.A_H = 100
        self.A_V = 100
        self.tau_d = 1000
        self.f_d = 0.0
        self.beamID = 5
        self.tau_d = self.tau_d * self.Ts
        self.mu = 0.0

    def ComputeMfImpulseResponse(self):

        # Get the parameters for this pulse type.
        lclPulseType = self.pulseType
        f_s = 1.25*self.f_lfm[lclPulseType]
        T_s = 1.0/f_s
        mu = self.f_lfm[lclPulseType]/self.tau_p[lclPulseType]
        pulseSamples = self.N_p[lclPulseType]*[0]
        A = 1 # Pulse samples amplitude.

        # Get the Taylor weights or uniform weights for 100 kHz LFM pulse types.
        if self.f_lfm[lclPulseType] < 500.0e3:
            w_dsl = ones(self.N_p[lclPulseType])
        else:
            w_dsl = asarray(TaylorWindow(self.nbar,self.sll[lclPulseType],self.N_p[lclPulseType],1))

        # Calculate the noise gain, the square root of the sum of the square of
        # the weights.
        G_n = 0.0
        G_s = 0.0
        for i in range(self.N_p[lclPulseType]):
            G_n += (w_dsl[i]*w_dsl[i])
            G_s += w_dsl[i]
        G_n = sqrt(G_n)

        print "  MF noise gain = %f, MF signal gain = %f" % (G_n,G_s)
        # Normalize the weights for unity gain through MF.
        w_dsl /= G_n

        # Generate the complex time domain pulse samples for this LFM pulse type
        for n in range(self.N_p[lclPulseType]):
            nTs = n*T_s
            phi = 2.0*pi*( (-self.f_lfm[lclPulseType]/2)*nTs + 0.5*mu*nTs*nTs )
            pulseSamples[n] = complex(
                                      A*w_dsl[n]*cos(phi),
                                      -A*w_dsl[n]*sin(phi)
                                     )
        return(pulseSamples)

    def QuadratureDemodulate(self,s_if):

        numIfSamples = len(s_if)

        # Generate quadrature LOs
        LOIH = zeros(numIfSamples)
        LOQH = zeros(numIfSamples)
        LOIV = zeros(numIfSamples)
        LOQV = zeros(numIfSamples)
        for i in arange(0,numIfSamples,1):
            LOIH[i] = 2**15 * cos(2 * pi * self.f_H * i * self.Ts)
            LOQH[i] = 2**15 * sin(2 * pi * self.f_H * i * self.Ts)
            LOIV[i] = 2**15 * cos(2 * pi * self.f_V * i * self.Ts)
            LOQV[i] = 2**15 * sin(2 * pi * self.f_V * i * self.Ts)

        LOIH = map(round,LOIH)
        LOQH = map(round,LOQH)
        LOIV = map(round,LOIV)
        LOQV = map(round,LOQV)

        # Mix IF input samples with LOs
        x_H = s_if*LOIH
        x_H = x_H/2**14
        y_H = s_if*LOQH
        y_H = -1*y_H
        y_H = y_H/2**14
        x_V = s_if*LOIV
        x_V = x_V/2**14
        y_V = s_if*LOQV
        y_V = -1*y_V
        y_V = y_V/2**14

        self.pltDataDemod60[0] = x_H
        self.pltDataDemod60[1] = y_H
        self.pltDataDemod60[2] = x_V
        self.pltDataDemod60[3] = y_V

        # Lowpass filter with decimate by 12 LPF
        I_H = self.iqFir.filter(x_H,0)
        Q_H = self.iqFir.filter(y_H,0)
        I_V = self.iqFir.filter(x_V,0)
        Q_V = self.iqFir.filter(y_V,0)

        self.pltDataDemod60f[0] = I_H
        self.pltDataDemod60f[1] = Q_H
        self.pltDataDemod60f[2] = I_V
        self.pltDataDemod60f[3] = Q_V

        # Decimate by 12
        I_H = I_H[0::12]
        Q_H = Q_H[0::12]
        I_V = I_V[0::12]
        Q_V = Q_V[0::12]

        self.pltDataDemod[0] = I_H
        self.pltDataDemod[1] = Q_H
        self.pltDataDemod[2] = I_V
        self.pltDataDemod[3] = Q_V

        return [I_H,Q_H,I_V,Q_V]

    def GenerateBasebandSamples(self,parameters,ioDataFilenames):

        # Pulse types are:
        #
        #   1: 1   usec GCW
        #   2: 10  usec GCW
        #   3: 16  usec 1 MHz LFM
        #   4: 25  usec GCW multi-pulse
        #   5: 32  usec 1 MHz LFM
        #   6: 64  usec 1 MHz LFM
        #   7: 125 usec GCW multi-pulse
        #   8: 128 usec 100 kHz LFM
        #   9: 128 usec 1 MHz LFM
        #  10: 250 usec 100 kHz LFM
        #  11: 250 usec 1 MHz LFM
        #

        # Extract pulse type and noise parameters
        self.pulseType          = parameters[0]
        self.beamID             = parameters[1]
        self.numBasebandSamples = parameters[2]
        self.sigmaH             = parameters[10]
        self.sigmaV             = parameters[11]
        self.A_H                = parameters[12]
        self.A_V                = parameters[13]
        self.tau_d              = parameters[7]
        self.f_d                = parameters[8]
        self.mu                 = parameters[9]

        lclPulseType = self.pulseType


        # Read in IF data samples from selected file
        s_if = asarray(readIfData(ioDataFilenames[0]))
        numIfSamples = len(s_if)
        printStr  = '  Read in %d' % numIfSamples
        printStr += ' 60 MHz IF samples'
        print '%s' % printStr

        # Quadrature demodulate to generate 5 MHz baseband samples. All pulse
        # types.
        iqData5MHz = self.QuadratureDemodulate(s_if)
        numIqSamples = len(iqData5MHz[0])
        # Write 5MHz samples to output file
        writeBasebandData(iqData5MHz,ioDataFilenames[1])
        printStr  = '  Generated %d' % numIqSamples
        printStr += ' 5 MHz I,Q samples'
        print '%s' % printStr

        # Decimate by 4 for all pulse types except multi-pulse (4 and 7)
        if (lclPulseType != 4) and (lclPulseType != 7):

            # Low pass filter to decimate by 4.
            iqData1Dot25MHz = 4*[0]
            for i in range(4):
                iqData1Dot25MHz[i] = self.decBy4Fir.filter(iqData5MHz[i],0)
                # Save the data before decimation for plotting.
                self.pltDataDemod5f[i] = iqData1Dot25MHz[i]
                iqData1Dot25MHz[i] = iqData1Dot25MHz[i][0::4]
                self.pltData1_25[i] = iqData1Dot25MHz[i]

            numIqSamples = len(iqData1Dot25MHz[0])
            printStr  = '  Generated %d' % numIqSamples
            printStr += ' 1.25 MHz I,Q samples'
            # Write 1.25MHz samples to output file
            writeBasebandData(iqData1Dot25MHz,ioDataFilenames[2])
            print '%s' % printStr

        # Process 1 MHz bandwidth waveforms
        if (lclPulseType == 1) or (self.f_lfm[lclPulseType] > 500.0e3):

            mfResponse = 2*[0]

            # --- Perform Matched Filter for LFM pulse types ----
            if self.f_lfm[lclPulseType] > 500.0e3 :

                # Get time domain, weighted impulse response
                impResp = self.ComputeMfImpulseResponse()

                # Use Numpy convolve function for now
                numIqSamples = len(iqData1Dot25MHz[0])
                for j in range(2):
                    r_t = numIqSamples*[0]
                    for n in range(numIqSamples):
                        r_t[n] = complex(iqData1Dot25MHz[2*j + 0][n],iqData1Dot25MHz[2*j + 1][n])

                    r_t = asarray(r_t)
                    mfResponse[j] = convolve(r_t,impResp)

            return (iqData1Dot25MHz,mfResponse)


        # Process 100 kHz bandwidth waveforms
        if (lclPulseType == 2) or (lclPulseType == 8) or (lclPulseType == 10):

            # Low pass filter to decimate by 10 for these pulse types.
            iqData125kHz = 4*[0]
            for i in range(4):
                iqData125kHz[i] = self.decBy10Fir.filter(iqData1Dot25MHz[i],2)
                iqData125kHz[i] = iqData125kHz[i][0::10]
                self.pltData_125[i] = iqData125kHz[i]

            numIqSamples = len(iqData125kHz[0])
            printStr  = '  Generated %d' % numIqSamples
            printStr += ' 125 kHz I,Q samples'
            # Write 1.25MHz samples to output file
            writeBasebandData(iqData125kHz,ioDataFilenames[3])
            print '%s' % printStr

            mfResponse = 2*[0]

            # --- Perform Matched Filter for LFM pulse types ----
            if self.f_lfm[lclPulseType] > 50.0e3 :

                # Get time domain, weighted impulse response
                impResp = self.ComputeMfImpulseResponse()

                # Use Numpy convolve function for now
                for j in range(2):
                    r_t = numIqSamples*[0]
                    for n in range(numIqSamples):
                        r_t[n] = complex(iqData125kHz[2*j + 0][n],iqData125kHz[2*j + 1][n])

                    r_t = asarray(r_t)
                    mfResponse[j] = convolve(r_t,impResp)


            return (iqData125kHz,mfResponse)

        # Process 25 usec GCW multi-pulse waveform
        if (lclPulseType == 4):

            # Matched Filter 5 MHz samples for multi-pulse pulse types.
            iqDataMf25 = 8*[0]
            for i in range(4):
                iqDataMf25[i] = self.mf25usec.filter(iqData5MHz[i],1)
                # Extract early gate samples if this is beam/channel 5. Must do
                # this prior to decimation of "normal" gate channels
                if self.beamID == 5:
                    iqDataMf25[i+4] = iqDataMf25[i][0::250]
                iqDataMf25[i] = iqDataMf25[i][62::250]
            numIqSamples = len(iqDataMf25[0])
            print"\n  Generated %d 25 usec multi-pulse I,Q samples" % numIqSamples
            if self.beamID == 5:
                numIqSamples = len(iqDataMf25[4])
                printStr  = 'Generated %d' % numIqSamples
                printStr += ' 25 usec early gate multi-pulse I,Q samples'
                print '%s' % printStr

            return iqDataMf25


        # Process 125 usec GCW multi-pulse waveform
        if (lclPulseType == 7):

            # Matched Filter 5 MHz samples for multi-pulse pulse types.
            iqDataMf125 = 8*[0]
            for i in range(4):
                iqDataMf125[i] = self.mf125usec.filter(iqData5MHz[i],1)
                # Extract early gate samples if this is beam/channel 5. Must do
                # this prior to decimation of "normal" gate channels
                if self.beamID == 5:
                    iqDataMf125[i+4] = iqDataMf125[i][0::750]
                iqDataMf125[i] = iqDataMf125[i][312::750]
            numIqSamples = len(iqDataMf125[0])
            print"\n Generated %d 125 usec multi-pulse I,Q samples" % numIqSamples
            if self.beamID == 5:
                numIqSamples = len(iqDataMf125[4])
                printStr  = 'Generated %d' % numIqSamples
                printStr += ' 125 usec early gate multi-pulse I,Q samples'
                print '%s' % printStr

            return iqDataMf125

def proc(fsFlag,selFilename):


    ifFilename = 'IFdata/' + selFilename
    paramFileName = 'IFdata/' + selFilename[:-4] + '.txt'

    # Call utility function to parse the input parameters.
    params = parseInputParamsFile(paramFileName)
    if len(params) < 1 :
        print "Error parsing input parameters file %s" % paramFileName
        sys.exit()

    # Build absolute filename to write 5MHz baseband data samples.
    try:
        mkdir('5Mdata/')
    except:
        pass # Directory exists, OK
    filename5MHz = '5Mdata/' + 'BB5M_' + selFilename[3:]

    # Build absolute filename to write 1.25MHz baseband data samples.
    try:
        mkdir('1_25Mdata/')
    except:
        pass # Directory exists, OK
    filename1_25MHz = '1_25Mdata/' + 'BB1_25M_' + selFilename[3:]

    # Build absolute filename to write 125kHz baseband data samples.
    try:
        mkdir('125kdata/')
    except:
        pass # Directory exists, OK
    filename125kHz = '125kdata/' + 'BB125k_' + selFilename[3:]

    # Make directory to write output plot files.
    try:
        mkdir('plots')
    except:
        pass # Directory exists, OK


    ioFilenames = [
                   ifFilename,
                   filename5MHz,
                   filename1_25MHz,
                   filename125kHz
                  ]

    coeffFileNames = [
                      "lpf1.csv",
                      "lpf2.csv",
                      "lpf3.csv",
                      "hmf_25usec.csv",
                      "hmf_125usec.csv"
                     ]
    tbrs = TbrsDDC(coeffFileNames)

    dspsPTypeStrings = [
                        "N/A",                  # 0
                        "1 usec GCW",           # 1
                        "10 usec GCW",          # 2
                        "16 usec 1 MHz LFM",    # 3
                        "25 usec GCW",          # 4
                        "32 usec 1 MHz LFM",    # 5
                        "64 usec 1 MHz LFM",    # 6
                        "125 usec GCW",         # 7
                        "128 usec 100 kHz LFM", # 8
                        "128 usec 1 MHz LFM",   # 9
                        "250 usec 100 kHz LFM", # 10
                        "250 usec 1 MHz LFM",   # 11
                       ]

    # Call main function to generate baseband samples and all the intermediate
    # samples.
    roundFlag = True
    (iqData,mfData) = tbrs.GenerateBasebandSamples(params,ioFilenames)
    numBasebandSamples = len(iqData[0])

    pt = params[0]
    ptStr = dspsPTypeStrings[pt]
    lfmBW = tbrs.f_lfm[pt]
    numIfPulseSamples = int(60.0e6 * tbrs.tau_p[pt])

    # Plot the 5 MHz outputs of LPF1.
    numIfPulseSamples = int(5.0e6 * tbrs.tau_p[pt])
    titles = 2*[0]
    titles[0] = "HP 5 MHz Baseband Spectrum"
    titles[1] = "VP 5 MHz Baseband Spectrum"
    A_H = params[12]
    A_V = params[13]
    v2counts = 8192.0
    filename = "plots/IQSpectrumPT%d_AH%d_AV%dM2.png" %  (pt,int(A_H),int(A_V))
    f_s = 5.0
    xlimits = [-2.5,2.5]
    plotSpectrumPair(
                     tbrs.pltDataDemod,
                     titles,
                     filename,
                     f_s,
                     xlimits,
                     fsFlag,
                     numIfPulseSamples,
                     v2counts
                    )
    # Plot the time domain samples if this is the final sampling rate.
    titles = 2*[0]
    titles[0] = "HP 5 MHz Samples"
    titles[1] = "VP 5 MHz Samples"
    filename = "plots/5MHzTimeDomainPT%d_AH%d_AV%dM2.png" % (
                                                       pt,
                                                       int(A_H),
                                                       int(A_V)
                                                      )

    # muH = mean(tbrs.pltDataDemod[0])
    # muV = mean(tbrs.pltDataDemod[2])
    # sigmaH = sqrt(var(tbrs.pltDataDemod[0]))
    # sigmaV = sqrt(var(tbrs.pltDataDemod[2]))
    # print "mu_h = %f, mu_v = %f" % (muH,muV)
    # print "sigma_h = %f, sigma_v = %f" % (sigmaH,sigmaV)
    plotTimeDomainPair(
                       tbrs.pltDataDemod,
                       titles,
                       filename,
                       fsFlag,
                       fSize=10
                      )

    # Now plot the spectrum and time domain samples of the output of the
    # decimate by 4 filter if the pulse type is not multi-pulse (4, 7). Input
    # sample rate = 5 MHz, output sample rate = 1.25 MHz.
    if (pt != 4) and (pt != 7):

        # Plot the 1.25 MHz spectrum at the output of LPF3.
        numIfPulseSamples = int(1.25e6 * tbrs.tau_p[pt])
        titles = 2*[0]
        titles[0] = "HP 1.25 MHz Baseband Spectrum"
        titles[1] = "VP 1.25 MHz Baseband Spectrum"
        filename = "plots/1_25MHzSpectrumPT%d_AH%d_AV%dM2.png" % (
                                                            pt,
                                                            int(A_H),
                                                            int(A_V)
                                                           )
        f_s = 1.25
        xlimits = [-0.625,0.625]
        plotSpectrumPair(
                         tbrs.pltData1_25,
                         titles,
                         filename,
                         f_s,
                         xlimits,
                         fsFlag,
                         numIfPulseSamples,
                         v2counts
                        )

        # Plot the time domain LPF2 samples
        titles = 2*[0]
        titles[0] = "HP 1.25 MHz Samples"
        titles[1] = "VP 1.25 MHz Samples"
        filename = "plots/1_25MHzTimeDomainPT%d_AH%d_AV%dM2.png" % (
                                                              pt,
                                                              int(A_H),
                                                              int(A_V)
                                                             )
        plotTimeDomainPair(
                           tbrs.pltData1_25,
                           titles,
                           filename,
                           fsFlag,
                           fSize=10
                          )

        # Plot the Matched Filter data for 1 MHz LFM
        if lfmBW > 500.0e3 :
            titles = 2*[0]
            titles[0] = "HP 1.25 MHz MF Samples"
            titles[1] = "VP 1.25 MHz MF Samples"
            filename = "plots/1_25MHzMatchedFilterPT%d_AH%d_AV%dM2.png" % (
                                                                  pt,
                                                                  int(A_H),
                                                                  int(A_V)
                                                                 )
            plotTimeDomainPair(
                               [mfData[0].real,mfData[0].imag,mfData[1].real,mfData[1].imag],
                               titles,
                               filename,
                               fsFlag,
                               fSize=10
                              )

            # Plot the MF log-magnitude samples
            titles = 2*[0]
            titles[0] = "HP 1.25 MHz MF Log-Magnitude"
            titles[1] = "VP 1.25 MHz MF Log-Magnitude"
            filename = "plots/1_25MHzMfLogMagPT%d_AH%d_AV%dM2.png" % (
                                                                  pt,
                                                                  int(A_H),
                                                                  int(A_V)
                                                                 )
            plotMfMagnitude(
                          mfData,
                          titles,
                          filename,
                          fsFlag,
                          fSize=10
                        )

        # Plot 125 kHz spectrum and time domain samples for pulse types 2, 8,
        # and 10.
        if (pt == 2) or (pt == 8) or (pt == 10):
            numIfPulseSamples = int(125e3 * tbrs.tau_p[pt])
            titles = 2*[0]
            titles[0] = "HP 125 kHz Baseband Spectrum"
            titles[1] = "VP 125 kHz Baseband Spectrum"
            filename = "plots/125kHzSpectrumPT%d_AH%d_AV%dM2.png" % (
                                                               pt,
                                                               int(A_H),
                                                               int(A_V)
                                                              )
            f_s = 125.0
            xlimits = [-62.5,62.5]
            plotSpectrumPair(
                             tbrs.pltData_125,
                             titles,
                             filename,
                             f_s,
                             xlimits,
                             fsFlag,
                             numIfPulseSamples,
                             v2counts,
                             fSize=10,
                             xLbl = 'Frequency (kHz)'
                            )

            # Plot the time domain samples since this is the final sampling rate.
            titles = 2*[0]
            titles[0] = "HP 125 kHz Samples"
            titles[1] = "VP 125 kHz Samples"
            filename = "plots/125kHzTimeDomainPT%d_AH%d_AV%dM2.png" % (
                       pt,int(A_H),int(A_V)
                       )
            plotTimeDomainPair(tbrs.pltData_125,titles,filename,fsFlag,fSize=10)

            # Plot the Matched Filter data for 100 kHz LFM
            if lfmBW > 50.0e3 :
                titles = 2*[0]
                titles[0] = "HP 125 kHz MF Samples"
                titles[1] = "VP 125 kHz MF Samples"
                filename = "plots/125kHzMatchedFilterPT%d_AH%d_AV%dM2.png" % (
                                                                      pt,
                                                                      int(A_H),
                                                                      int(A_V)
                                                                     )
                plotTimeDomainPair(
                                   [mfData[0].real,mfData[0].imag,mfData[1].real,mfData[1].imag],
                                   titles,
                                   filename,
                                   fsFlag,
                                   fSize=10
                                  )

                # Plot the MF log-magnitude samples
                titles = 2*[0]
                titles[0] = "HP 125 kHz MF Log-Magnitude"
                titles[1] = "VP 125 kHz MF Log-Magnitude"
                filename = "plots/125kHzMfLogMagPT%d_AH%d_AV%dM2.png" % (
                                                                      pt,
                                                                      int(A_H),
                                                                      int(A_V)
                                                                     )
                plotMfMagnitude(
                              mfData,
                              titles,
                              filename,
                              fsFlag,
                              fSize=10
                            )

    # Call the MatPlotLib show() function to display plots to screen.
    show()

# ---------------------------- Begin Main Program ----------------------------

if __name__ == '__main__' :


    # try:
        # infile = sys.argv[1]
    # except:
        # print "Usage %s paramFile.py \n" % sys.argv[0]
        # print "    paramFile.py contains run parameters"
        # sys.exit()

    # try:
        # execfile(infile)
    # except:
        # print "Can't execute parameter file %s" % infile
        # sys.exit()

    # print params

    # Display dialog box to select FIR filter to simulate sampling
    app = App(False, "output")
    fred = app.MainLoop()

