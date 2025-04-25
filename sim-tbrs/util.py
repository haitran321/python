from math import pi, sqrt
from cmath import acosh
from struct import pack, unpack
from pylab import *
# from formlayout import fedit
# from os import walk


def parseInputParamsFile(infileName):

    # Set simulation defaults
    pulseType          = 3            # CSPU pulse type.
    beamID             = 5            # NOVEM antenna beam number (1..10)
    numBasebandSamples = 250          # Number of output baseband samples to generate.
    Ps_H               = 0.0          # HP peak signal power (dBm).
    Ps_V               = -100.0       # VP peak signal power (dBm).
    Pn_H               = -55.72       # HP noise power (dBm).
    Pn_V               = -55.72       # VP noise power (dBm).
    tau_d              = 0.550205775  # Target delay (fraction of 60 MHz IF sample window).
    f_d                = 0.0          # Target Doppler frequency offset (Hz).
    muIF               = 0.0          # Simulated A/D dc offset (counts).

    params = [
              pulseType,           # 0
              beamID,              # 1
              numBasebandSamples,  # 2
              Pn_H,                # 3
              Pn_V,                # 4
              Ps_H,                # 5
              Ps_V,                # 6
              tau_d,               # 7
              f_d,                 # 8
              muIF,                # 9
              0.0,                 # 10 (sigma_H)
              0.0,                 # 11 (sigma_V)
              0.0,                 # 12 (A_H)
              0.0                  # 13 (A_V)
             ]


    # Now parse the input parameter file selected by the user.
    try:
        infile = open(infileName,'r')
    except:
        # Return empty list if the file cannot be read.
        return([])

    print "\n\nSimulation input parameters"
    for line in infile:
        splitLine = line.split()
        if splitLine[0] == 'pulseType':
            try:
                pulseType = int(splitLine[2])
                params[0] = pulseType
                print "  Pulse type = %d" % pulseType
            except:
                print "Invalid pulse type in input file"
                sys.exit()

            if (pulseType < 1) or (pulseType > 11) :
                print "Invalid pulse type in input file"
                sys.exit()

        if splitLine[0] == 'beamID':
            try:
                beamID = int(splitLine[2])
                params[1] = beamID
                print "  Beam ID = %d" % beamID
            except:
                print "Invalid beam ID in input file"
                sys.exit()

            if (beamID < 1) or (beamID > 10) :
                print "Invalid beam ID in input file"
                sys.exit()

        if splitLine[0] == 'numBasebandSamples':
            try:
                numBasebandSamples = int(splitLine[2])
                params[2] = numBasebandSamples
                print "  Number of output baseband samples = %d" % numBasebandSamples
            except:
                print "Invalid number of output baseband samples in input file"
                sys.exit()

        if splitLine[0] == 'Pn_H':
            try:
                Pn_H = float(splitLine[2])
                params[3] = Pn_H
                print "  HP noise power (dBm) = %f" % Pn_H
            except:
                print "Invalid HP noise power (dBm) in input file"
                sys.exit()

        if splitLine[0] == 'Pn_V':
            try:
                Pn_V = float(splitLine[2])
                params[4] = Pn_H
                print "  VP noise power (dBm) = %f" % Pn_V
            except:
                print "Invalid VP noise power (dBm) in input file"
                sys.exit()

        if splitLine[0] == 'Ps_H':
            try:
                Ps_H = float(splitLine[2])
                params[5] = Ps_H
                print "  HP peak signal power (dBm) = %f" % Ps_H
            except:
                print "Invalid HP peak signal power (dBm) in input file"
                sys.exit()

        if splitLine[0] == 'Ps_V':
            try:
                Ps_V = float(splitLine[2])
                params[6] = Ps_V
                print "  VP peak signal power (dBm) = %f" % Ps_V
            except:
                print "Invalid VP peak signal power (dBm) in input file"
                sys.exit()

        if splitLine[0] == 'tau_d':
            try:
                tau_d = float(splitLine[2])
                params[7] = tau_d
                print "  Target delay = %f" % tau_d
            except:
                print "Invalid Target delay in input file"
                sys.exit()

        if splitLine[0] == 'f_d':
            try:
                f_d = float(splitLine[2])
                params[8] = f_d
                print "  Target Doppler frequency offset = %f Hz" % f_d
            except:
                print "Invalid Target Doppler frequency offset in input file"
                sys.exit()

        if splitLine[0] == 'muIF':
            try:
                muIF = float(splitLine[2])
                params[9] = f_d
                print "  Simulated A/D dc offset = %f counts" % muIF
            except:
                print "Invalid Simulated A/D dc offset in input file"
                sys.exit()

        # print splitLine

    print "\n"
    return(params)

def writeBasebandData(bbData,filename):

    ofile = open(filename,'w')
    numSamples = len(bbData[0])
    for index in range(numSamples):
        # HP I
        ostring = pack('<h',bbData[0][index])
        iData = unpack('<H',ostring)
        ofile.write("%04X " % iData[0])
        # HP Q
        ostring = pack('<h',bbData[0][index])
        iData = unpack('<H',ostring)
        ofile.write("%04X " % iData[0])
        # VP I
        ostring = pack('<h',bbData[0][index])
        iData = unpack('<H',ostring)
        ofile.write("%04X " % iData[0])
        # VP Q
        ostring = pack('<h',bbData[0][index])
        iData = unpack('<H',ostring)
        ofile.write("%04X" % iData[0])
        ofile.write("\n")
    ofile.close()

def readIfData(filename):

    ifFile = open(filename,'r')
    ifData = []
    for line in ifFile:
        dlist = line.split()
        hexDigits = dlist[0][0:4]
        signDigit = int(hexDigits[0],base=16)
        if signDigit > 7:
            # Negative, sign extend with F's
            for j in range(4):
                hexDigits = 'F' + hexDigits
        else :
            # Positive, sign extend with 0's
            for j in range(4):
                hexDigits = '0' + hexDigits
        hexDigits = int(hexDigits,base=16)
        ostring = pack('<I',hexDigits)
        hexDigits = unpack('<i',ostring)[0]
        ifData.append(hexDigits)
        # print "%s, %d" % (dlist[0],hexDigits)
    ifFile.close()
    return(ifData)

# Support lambda product function for TaylorWindow()
prod = lambda x,y:x*y

# Support factorial function for TaylorWindow()
def fact(l):
    if (l > 1):
        return(reduce(prod,range(1,l+1,1)))
    else:
        return(1)

# Two-parameter Taylor weight function.
def TaylorWindow(nbar,sll,npoints,wf):

    """This function computes two parameter Taylor weights. This
    weighting function was designed by T. T. Taylor of Hughes Aircraft in
    the 1950s. The function was designed to approximate Chebyshev weights
    without discontinuities at the endpoints. The two parameters are the
    sidelobe level SLL, and nbar. The SLL is entered as a positive dB
    value for a peak sidelobe level of SLL dB below the peak of the main
    lobe. The parameter nbar is the number of sidelobes to each side of
    the mainlobe at a flat SLL down."""
    ratio = 10**(-sll/20)
    deltaX = 1/npoints
    capm = nbar-1
    B = acosh(ratio)/pi
    A = B.real
    sigma = nbar/sqrt(A*A + (nbar - 0.5)**2)
    W = ones(npoints+1)
    F = ones(capm+1)
    for m in range(1,(capm+1),1):
        numer = 1
        for n in range(1,(capm+1),1):
            f1 = m**2;
            f2 = (sigma**2)*(A**2+(n-0.5)**2)
            f3 = 1 - f1/f2
            numer = numer*f3
        f4 = fact(capm)
        f4 = f4**2
        f4 = f4/(fact(capm+m) * fact(capm-m))
        F[m] = f4*numer

    for i in range(1,(npoints+1),1):
        x = -0.5 + deltaX/2 + (i-1)*deltaX
        for m in range(1,(capm+1),1):
            if (wf == 1):
              W[i] = W[i] + 2*F[m]*cos(2*pi*m*x)
    return(W[1:])

def plotSpectrumPair(
                     hpvpdata,
                     titleStr,
                     fName,
                     f_s,
                     xlims,
                     fsFlag,
                     numPulseSamples,
                     volts2counts,
                     fSize=10,
                     xLbl='Frequency (MHz)'
                    ):

    """This is a utility function to plot a side-by-side pair of baseband
    spectral plots, one for HP and one for VP. The main program creates these
    plots often enought to warrant this function."""
    numBB = len(hpvpdata[0])
    numBB2 = log(numBB)/log(2)
    numBB2 = ceil(numBB2)
    numBB2 += 1
    numBB2 = 2**numBB2
    df = f_s / numBB2
    figure()
    s_f = zeros(int(numBB2),dtype=complex)
    s_f.real[:numBB] = hpvpdata[0]
    s_f.imag[:numBB] = hpvpdata[1]
    # Convert from counts to volts
    s_f *= (1.0 / volts2counts)
    s_f = fft(s_f)
    # Scale for FFT gain
    s_f = s_f * (1.0/numPulseSamples)
    s_f = fftshift(s_f)
    sh_f = 20*log10(hypot(s_f.real,s_f.imag)+1.0e-20) + 10
    maxMagHp = max(sh_f)
    s_f = zeros(int(numBB2),dtype=complex)
    s_f.real[:numBB] = hpvpdata[2]
    s_f.imag[:numBB] = hpvpdata[3]
    # Convert from counts to volts
    s_f *= (1.0 / volts2counts)
    s_f = fft(s_f)
    s_f = s_f * (1.0/numPulseSamples)
    s_f = fftshift(s_f)
    sv_f = 20*log10(hypot(s_f.real,s_f.imag)+1.0e-20) + 10
    maxMagHp = max(sh_f)
    maxMagVp = max(sv_f)
    maxMag = maxMagHp
    if maxMagVp > maxMagHp:
        maxMag = maxMagVp
    plotMax = ceil(maxMag * 10.0) + 100
    plotMax /= 10.0
    index = arange(numBB2)
    index -= (numBB2//2)
    index *= df
    subplot(1,2,1)
    plot(index,sh_f)
    xlim(xlims)
    ylim([plotMax-100,plotMax])
    title(titleStr[0], fontsize=fSize, fontname='Times')
    xlabel(xLbl, fontsize=fSize, fontname='Times')
    ylabel("Power (dBm)", fontsize=fSize, fontname='Times')
    locs,  labels = yticks()
    setp(labels, fontsize=fSize, fontname='Times')
    locs,  labels = xticks()
    setp(labels, fontsize=fSize, fontname='Times')
    grid(True)
    subplot(1,2,2)
    plot(index,sv_f)
    xlim(xlims)
    ylim([plotMax-100,plotMax])
    title(titleStr[1], fontsize=fSize, fontname='Times')
    xlabel(xLbl, fontsize=fSize, fontname='Times')
    locs,  labels = yticks()
    setp(labels, fontsize=fSize, fontname='Times')
    locs,  labels = xticks()
    setp(labels, fontsize=fSize, fontname='Times')
    grid(True)
    if fsFlag != 0:
        savefig(fName,dpi=200,format='png')

def plotTimeDomainPair(hpvpdata,titleStr,fName,fsFlag,fSize=10):

    """This is a utility function to plot a side-by-side pair of baseband time
    domain sample plots, one for HP and one for VP. The main program creates
    these plots often enought to warrant this function."""
    figure()
    numBB = len(hpvpdata[0])
    index = arange(numBB)
    subplot(1,2,1)
    plot(index,hpvpdata[0],index,hpvpdata[1])
    xlim([0,numBB])
    title(titleStr[0], fontsize=fSize, fontname='Times')
    xlabel("Sample Number", fontsize=fSize, fontname='Times')
    ylabel("Amplitude (counts)", fontsize=fSize, fontname='Times')
    locs,  labels = yticks()
    setp(labels, fontsize=fSize, fontname='Times')
    locs,  labels = xticks()
    setp(labels, fontsize=fSize, fontname='Times')
    grid(True)
    subplot(1,2,2)
    plot(index,hpvpdata[2],index,hpvpdata[3])
    xlim([0,numBB])
    title(titleStr[1], fontsize=fSize, fontname='Times')
    xlabel("Range Bin", fontsize=fSize, fontname='Times')
    locs,  labels = yticks()
    setp(labels, fontsize=fSize, fontname='Times')
    locs,  labels = xticks()
    setp(labels, fontsize=fSize, fontname='Times')
    grid(True)
    if fsFlag != 0:
        savefig(fName,dpi=200,format='png')

def plotMfMagnitude(mfData,titleStr,fName,fsFlag,fSize=10):

    """This is a utility function to plot a side-by-side pair of
    baseband Matched Filter log-magnitude plots, one for HP and one for VP. The main
    program creates these plots often enought to warrant this function."""
    figure()
    numBB = len(mfData[0])
    index = arange(numBB)
    subplot(1,2,1)
    magnitude = sqrt(mfData[0].real**2 + mfData[0].imag**2 + 1.0e-2)
    magnitude = 20.0*log10(magnitude)
    plot(index,magnitude)
    xlim([0,numBB])
    title(titleStr[0], fontsize=fSize, fontname='Times')
    xlabel("Range Bin", fontsize=fSize, fontname='Times')
    ylabel("Log-Mag (dB)", fontsize=fSize, fontname='Times')
    locs,  labels = yticks()
    setp(labels, fontsize=fSize, fontname='Times')
    locs,  labels = xticks()
    setp(labels, fontsize=fSize, fontname='Times')
    grid(True)
    subplot(1,2,2)
    magnitude = sqrt(mfData[1].real**2 + mfData[1].imag**2 + 1.0e-2)
    magnitude = 20.0*log10(magnitude)
    plot(index,magnitude)
    xlim([0,numBB])
    title(titleStr[1], fontsize=fSize, fontname='Times')
    xlabel("Range Bin", fontsize=fSize, fontname='Times')
    locs,  labels = yticks()
    setp(labels, fontsize=fSize, fontname='Times')
    locs,  labels = xticks()
    setp(labels, fontsize=fSize, fontname='Times')
    grid(True)
    if fsFlag != 0:
        savefig(fName,dpi=200,format='png')

if __name__ == '__main__' :

    ifFilename = 'IFdata/IF_Y2009M07D23H21M04S46PT03.dat'
    readIfData(ifFilename)