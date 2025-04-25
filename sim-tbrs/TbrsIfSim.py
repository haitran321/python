#!/usr/bin/env python

from __future__ import division

import wx

from pylab import *
from fir import FIR
import datetime as dt
from struct import pack, unpack
from os import mkdir
from os import walk
from util import parseInputParamsFile

class App(wx.App):


    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)

    def OnInit(self):


        # Get the list of pulse type parameter files.
        # print "Directory Tree"
        tree = walk("") # Walk the current directory

        # Put the .py filenames in a list
        for dir in tree:
            # print dir
            if dir[0] == '': # Just the top directory
                fileList = []
                for file in dir[2]:
                    # print file
                    if (file[-4:] == '.inp') and (file[:2] == 'pt'):
                        # print "file = %s" % file
                        fileList.append(file)

        # print fileList


        # Use dialog list box to get user filename selection
        datalist = [
                    ('Pulse Type Parameters File', fileList)
                    ]

        dlg = wx.SingleChoiceDialog(None,
                'Pulse Type Parameters File?', 'Select Pulse Type Parameters File',
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


class VectorModulator(object):

    # Define any class variables (shared by all instances) here.

    def __init__(self,coefficientFileName):

        # Initialize per instance variables here.

        # Create FIR for vector modulator LPFs.
        self.vmFir = FIR(coefficientFileName)
        self.decBy10FirnumCoeff = 167
        self.decBy4FirnumCoeff  = 87
        self.iqFirnumCoeff      = 83
        # Set constants for vector modulator
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

    def Modulate(self,parameters,roundFlag):

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

        # Calculate the number of IF samples based on the desired number of
        # baseband samples. This depends on filter chain through TBRS which is
        # different for the different pulse types.
        if (lclPulseType == 1) or (self.f_lfm[lclPulseType] > 500.0e3):

            # These are the 1 MHz bandwidth pulse types. They go through I,Q
            # demodulation with decimation by 12, and decimation by 4 LPF.
            N0 = self.numBasebandSamples
            N1 = 4 * N0 + self.decBy4FirnumCoeff - 1
            N2 = 12 * N1 + self.iqFirnumCoeff - 1
            numIfSamples = N2

        if (lclPulseType == 2) or (lclPulseType == 8) or (lclPulseType == 10):

            # These are the 100 kHz bandwidth pulse types. They go through I,Q
            # demodulation with decimation by 12, decimation by 4 LPF, and
            # decimation by 10 LPF.
            N0 = self.numBasebandSamples
            N1 = 10 * N0 + self.decBy10FirnumCoeff - 1
            N2 = 4 * N1 + self.decBy4FirnumCoeff - 1
            N3 = 12 * N2 + self.iqFirnumCoeff - 1
            numIfSamples = N3

        if (lclPulseType == 4):

            # This is the 25 usec GCW multi-pulse pulse type. It goes through
            # I,Q demodulation with decimation by 12, decimation by 4 LPF, and
            # matched filter with decimation by 250.
            N0 = self.numBasebandSamples
            N1 = 250 * N0 + self.mf25usecnumCoeff - 1
            N2 = 12 * N1 + self.iqFirnumCoeff - 1
            numIfSamples = N2

        if (lclPulseType == 7):

            # This is the 125 usec GCW multi-pulse pulse type. It goes through
            # I,Q demodulation with decimation by 12, decimation by 4 LPF, and
            # matched filter with decimation by 750.
            N0 = self.numBasebandSamples
            N1 = 750 * N0 + self.mf125usecnumCoeff - 1
            N2 = 12 * N1 + self.iqFirnumCoeff - 1
            numIfSamples = N2

        # Calculate target leading edge
        self.tau_d = self.tau_d * numIfSamples * self.Ts
        # self.tau_d = ((numIfSamples // 2) * self.Ts) + ( 155 * self.Ts)

        # Vector modulate to generate IF samples. All pulse types.
        roundFlag = True

        # Compute number of input samples
        numInput = numIfSamples + self.vmFir.numCoeff - 1

        # Generate input noise samples
        N_IH = self.sigmaH*randn(numInput)
        N_QH = self.sigmaH*randn(numInput)
        N_IV = self.sigmaV*randn(numInput)
        N_QV = self.sigmaV*randn(numInput)

        # Generate the signal samples
        mu = self.f_lfm[lclPulseType]/self.tau_p[lclPulseType]
        S_IH = zeros(numInput)
        S_QH = zeros(numInput)
        S_IV = zeros(numInput)
        S_QV = zeros(numInput)
        numPulseSamples = 0

        # Signal pre-scale for unity signal gain
        sigScale = (self.vmFir.G_n/self.vmFir.G_s)
        # sigScale = 1
        for i in arange(0, numInput, 1):
            t = i * self.Ts
            tMinus = t - self.tau_d
            if (
                (t >= self.tau_d)
                and
                (t <= (self.tau_d + self.tau_p[lclPulseType]) )
               ):
                numPulseSamples += 1
                phi_tMinus  = (self.f_d - self.f_lfm[lclPulseType]/2) * tMinus
                phi_tMinus += (0.5 * mu * tMinus**2)
                phi_tMinus *= (2.0 * pi)
                S_IH[i] = self.A_H * sigScale  * cos(phi_tMinus)
                S_QH[i] = self.A_H * sigScale  * sin(phi_tMinus)
                S_IV[i] = self.A_V * sigScale  * cos(phi_tMinus)
                S_QV[i] = self.A_V * sigScale  * sin(phi_tMinus)
            else:
                S_IH[i] = 0
                S_QH[i] = 0
                S_IV[i] = 0
                S_QV[i] = 0

        # Combine vector modulator input signal plus noise samples
        SigPlusNoiseIH = N_IH + S_IH
        SigPlusNoiseQH = N_QH + S_QH
        SigPlusNoiseIV = N_IV + S_IV
        SigPlusNoiseQV = N_QV + S_QV


        # LPF vector modulator input signal plus noise samples
        SigPlusNoiseIHfiltered = self.vmFir.filter(SigPlusNoiseIH,2)
        SigPlusNoiseQHfiltered = self.vmFir.filter(SigPlusNoiseQH,2)
        SigPlusNoiseIVfiltered = self.vmFir.filter(SigPlusNoiseIV,2)
        SigPlusNoiseQVfiltered = self.vmFir.filter(SigPlusNoiseQV,2)

        # Modulate baseband I/Q components to IF
        numFiltered = len(SigPlusNoiseIVfiltered)

        LOIH = zeros(numFiltered)
        LOQH = zeros(numFiltered)
        LOIV = zeros(numFiltered)
        LOQV = zeros(numFiltered)
        for i in arange(0,len(SigPlusNoiseIVfiltered),1):
            LOIH[i] = cos(2 * pi * self.f_H * i * self.Ts)
            LOQH[i] = sin(2 * pi * self.f_H * i * self.Ts)
            LOIV[i] = cos(2 * pi * self.f_V * i * self.Ts)
            LOQV[i] = sin(2 * pi * self.f_V * i * self.Ts)

        LOIVProduct = LOIV*SigPlusNoiseIVfiltered
        LOQVProduct = LOQV*SigPlusNoiseQVfiltered
        LOIHProduct = LOIH*SigPlusNoiseIHfiltered
        LOQHProduct = LOQH*SigPlusNoiseQHfiltered

        VM_H = LOIHProduct - LOQHProduct
        VM_V = LOIVProduct - LOQVProduct

        # Add the two vector modulator outputs, and add simulated A/D dc offset.
        S_IF = VM_H + VM_V + self.mu

        # Round to simulate A/D amplitude quantization.
        if roundFlag == True:
            S_IF = map(round,S_IF)

        # Copy to  plot vector and return.
        return S_IF


def proc(fsFlag,infileName):


    # Call utility function to parse the input parameters.
    params = parseInputParamsFile(infileName)

    # Make the directory for the output IF data samples.
    try:
        mkdir("IFdata")
    except:
        pass # Directory exists, OK

    # Initialize the vector modulator with the CSV file that holds the coefficients.
    coeffFileName = "h767_dec48_100.csv"
    vm = VectorModulator(coeffFileName)

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

    # Signal-to-noise ratio (SNR) equations
    #
    # Noise power into an impedance of R ohms (typically 50 ohms)
    #
    # P_n = sigma**2 / R (noise power)
    # P_ndB = 10 log10(sigma**2 / R)
    #
    # Signal power into an impedance of R ohms
    #
    # P_s = A**2 / (2 R) (signal power)
    # P_sdB = 10 log10(A**2 / (2 R) )
    #
    # SNR
    #
    # SNR = A**2 / 2 sigma**2
    # SNR_dB = 10 * log10(A**2 / 2 sigma**2)
    #
    # Full scale signal power and voltage
    #
    # P_fs = +10 dBm (full scale power, given for TBRS)
    #      = 10 log10(A_fs**2 / (2 R) ) + 30
    # A_fs = full scale voltage
    # 10 log10(A_fs**2 / (2 R) ) + 30 = 10
    # 10 log10(A_fs**2 / (2 R) ) = -20
    # log10(A_fs**2 / (2 R) ) = -2
    # A_fs**2 / (2 R) = 10**-2 = 0.01
    # A_fs**2 = 0.01 * 2R = 1
    # A_fs = 1 volt
    #
    # A/D voltage quantization
    #
    # v_q = A/D LSB, or voltage quantization
    #     = 1 volt / 8192 (2's complement, 14-bit A/D)
    #     = 122.07 microvolts

    # Convert input noise power in dBm to noise counts
    #
    # P_n (dBm) = 10 log10(sigma**2 / R) + 30, sigma (volts)
    #           = 10 log10(sigma**2 / 50) + 30
    # 10 log10(sigma**2 / 50) = P_n (dBm) - 30
    # 20 log10(sigma / sqrt(50)) = P_n (dBm) - 30
    # log10(sigma / sqrt(50)) = (P_n (dBm) - 30) / 20
    # sigma (volts) = sqrt(50) * 10**( (P_n (dBm) - 30) / 20 )
    # sigma (counts) = 8192 * sqrt(50) * 10**( (P_n (dBm) - 30) / 20 )

    sr50 = sqrt(50.0)
    v2counts = 8192.0

    # params[3] = P_n (dBm) (HP)
    # params[4] = P_n (dBm) (VP)
    params[10] = v2counts * sr50 * 10**( (params[3] - 30.0) / 20.0 ) # sigma_H (counts)
    params[11] = v2counts * sr50 * 10**( (params[4] - 30.0) / 20.0 ) # sigma_V (counts)

    # Convert input signal power in dBm to signal amplitude counts
    #
    # P_s (dBm) = 10 log10(A**2 / 2R) + 30, A (volts)
    #           = 10 log10(A**2 / 100) + 30
    # 10 log10(A**2 / 100) = P_s (dBm) - 30
    # 20 log10(A / 10) = P_s (dBm) - 30
    # log10(A / 10) = (P_s (dBm) - 30) / 20
    # A/10 = 10**((P_s (dBm) - 30) / 20)
    # A = 10 * 10**((P_s (dBm) - 30) / 20)
    # A (volts)  = 10**(1 + (P_s (dBm) - 30) / 20)
    # A (counts)  = 8192 * 10**(1 + (P_s (dBm) - 30) / 20)

    # params[5] = P_s (dBm) (HP)
    # params[6] = P_s (dBm) (VP)
    params[12] = v2counts * 10**(1.0 + ((params[5] - 30.0) / 20.0) ) # A_H (counts)
    params[13] = v2counts * 10**(1.0 + ((params[6] - 30.0) / 20.0) ) # A_V (counts)

    print "\n\nCalculated from input parameters"
    print "  sigma_H = %f counts" % params[10]
    print "  sigma_V = %f counts" % params[11]
    print "  A_H     = %f counts" % params[12]
    print "  A_V     = %f counts" % params[13]

    # Call main function to generate baseband samples and all the intermediate
    # samples.
    roundFlag = True
    ifData = vm.Modulate(params,roundFlag)
    numberIfSamples = len(ifData)

    pt = params[0]
    ptStr = dspsPTypeStrings[pt]
    lfmBW = vm.f_lfm[pt]
    numIfPulseSamples = int(60.0e6 * vm.tau_p[pt])

    # Plot the IF spectrum
    fs = 14
    numIF = len(ifData)
    numIF2 = log(numIF)/log(2)
    numIF2 = ceil(numIF2)
    numIF2 += 1
    numIF2 = 2**numIF2
    df = 60.0 / numIF2
    s_f = zeros(int(numIF2))
    s_f[:numIF] = ifData
    # Convert counts to volts
    s_f = s_f  * (1.0 / v2counts)
    s_f = fft(s_f)
    # Scale FFT output to set peak output to peak input voltage.
    fftScale = (1.0 / numIfPulseSamples)
    s_f = s_f * fftScale
    s_f = fftshift(s_f)
    # Convert to log magnitude squared
    s_f = 10*log10( s_f.real**2 + s_f.imag**2 + 1.0e-20)
    # Subtract 20 (10 log 2R) to convert to dBW, add 30 to convert to
    # dBm.
    s_f += 10
    maxMag = max(s_f)
    plotMax = ceil(maxMag * 10.0) + 100
    plotMax /= 10.0
    index = arange(numIF2)
    index -= (numIF2//2)
    index *= df
    plot(index,s_f)
    ylim([plotMax-100,plotMax])
    Ps_H = params[5]
    Ps_V = params[6]
    A_H = params[12]
    A_V = params[13]
    titleString = "IF Spectrum, PsH = %.1f dBm, PsV = %.1f dBm, %s" % (
                  Ps_H,Ps_V,ptStr
                  )
    title(titleString, fontsize=fs, fontname='Times')
    xlabel("Frequency (MHz)", fontsize=fs, fontname='Times')
    ylabel("Power (dBm)", fontsize=fs, fontname='Times')
    locs,  labels = yticks()
    setp(labels, fontsize=fs, fontname='Times')
    locs,  labels = xticks()
    setp(labels, fontsize=fs, fontname='Times')
    grid(True)
    filename = "IFdata/IFSpectrumFull_PT%d_AH%d_AV%dM2.png" % (pt,int(A_H),int(A_V))
    if fsFlag != 0:
        savefig(filename,dpi=200,format='png')

    # Zoom in on the positive frequency sidebands
    figure()
    plot(index,s_f)
    titleString = "Positive IF Spectrum, PsH = %.1f dBm, PsV = %.1f dBm, %s" % (
                   Ps_H,
                   Ps_V,
                   ptStr
                  )
    title(titleString, fontsize=fs, fontname='Times')
    xlim([19,25])
    ylim([plotMax-100,plotMax])
    xlabel("Frequency (MHz)", fontsize=fs, fontname='Times')
    ylabel("Power (dBm)", fontsize=fs, fontname='Times')
    locs,  labels = yticks()
    setp(labels, fontsize=fs, fontname='Times')
    locs,  labels = xticks()
    setp(labels, fontsize=fs, fontname='Times')
    grid(True)
    filename = "IFdata/IFSpectrumPos_PT%d_AH%d_AV%dM2.png" %  (pt,int(A_H),int(A_V))
    if fsFlag != 0:
        savefig(filename,dpi=200,format='png')


    # Call the MatPlotLib show() function to display plots to screen.
    show()

    # Write IF samples to file

    # Generate the ouput IF filename using the current date and time
    cdt = dt.datetime.now()
    cdtu = cdt.utctimetuple()
    pt = params[0]

    dtString = 'Y%04dM%02dD%02dH%02dM%02dS%02dPT%02d' % (cdtu[0],cdtu[1],cdtu[2],cdtu[3],cdtu[4],cdtu[5],pt)
    ifFilename = 'IFdata/IF_'+ dtString + '.dat'
    ifFile = open(ifFilename,'w')
    ifLogFilename = 'IFdata/IF_'+ dtString + '.txt'
    logFile = open(ifLogFilename,'w')


    logFile.write("pulseType          = %12d  # CSPU pulse type.\n" % params[0])
    logFile.write("beamID             = %12d  # NOVEM antenna beam number (1..10)\n" % params[1])
    logFile.write("numBasebandSamples = %12d  # Number of output baseband samples to generate.\n" % params[2])
    logFile.write("Pn_H               = %12.6f  # HP noise power (dBm).\n" % params[3])
    logFile.write("Pn_V               = %12.6f  # VP noise power (dBm).\n" % params[4])
    logFile.write("Ps_H               = %12.6f  # HP peak signal power (dBm).\n" % params[5])
    logFile.write("Ps_V               = %12.6f  # VP peak signal power (dBm).\n" % params[6])
    logFile.write("tau_d              = %12.6f  # Target delay (fraction of 60 MHz IF sample window).\n" % params[7])
    logFile.write("f_d                = %12.6f  # Target Doppler frequency offset (Hz).\n" % params[8])
    logFile.write("muIF               = %12.6f  # Simulated A/D dc offset (counts).\n" % params[9])
    logFile.write("A_H                = %12.6f  # HP Amplitude (counts).\n" % A_H)
    logFile.write("A_V                = %12.6f  # VP Amplitude (counts).\n" % A_V)
    logFile.write("sigma_H            = %12.6f  # HP Sigma (counts).\n" % params[10])
    logFile.write("sigma_V            = %12.6f  # VP Sigma (counts).\n" % params[11])
    for index in range(numberIfSamples):
        ostring = pack('<h',ifData[index])
        iData = unpack('<H',ostring)
        ifFile.write("%04X\n" % iData[0])
    ifFile.close()
    logFile.close()

# ---------------------------- Begin Main Program ----------------------------

if __name__ == '__main__' :

    # Run wxPython app to get user input.
    app = App(False, "output")
    fred = app.MainLoop()

