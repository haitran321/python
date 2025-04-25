from pylab import *
from struct import *

#N = 1024        # number of sample to generate
#
## LFM or CW signal (1 for lfm, 0 for CW)
#lfm = 1
#
## Float or 16-bit hex
#hex_enable = 0
#
## Write signal to file
#write_to_file = 1

def signal_gen (N, lfm, hex_enable, write_to_file):

    if write_to_file == 1:
         # output file
         outputFile = "C:\\ITT\\WorkSpace\\ftp\\signal.dat"
         fout = open(outputFile, "w")
    
    # Signal parameters
    fs = 60E6           # sampling freq
    Ts = 1/fs           # sampling period
    tau = (N-1)*Ts      # pulse width
    fo = 22E6           # signal freq
    B = 1E6             # LFM bandwidth
    signal_amp = 1
    f_start = fo-(B/2)
    f_stop = fo+(B/2)
    
    # Create a list to hold signal 
    y = []
    
    # Generate signal
    for i in xrange (0,N) :
        if lfm == 1 :
            y.append(cos(2*pi*((f_start*(i*Ts))+((B/(2*tau))*((i*Ts)**2)))))
        else :
            y.append(cos(2*pi*fo*(i*Ts)))

    if hex_enable == 1:
        y_fix = []
        # Convert signal from signed to unsigned
        for i in xrange (0, len(y)):
            y_fix.append(y[i] * (2**15 - 1))
            y_fix[i] = round(y_fix[i])
            ostring = pack('<h', y_fix[i])
            idata = unpack('<H', ostring)
            y_fix[i] = idata[0]
    
    # Write signal to file
    if write_to_file == 1:
        for i in xrange (0,len(y)):
            if hex_enable == 1:
                fout.write("%04X\n" % y_fix[i])
            else:
                fout.write("f\n" % y[i])
        fout.close()
    
    # fft
    F = fft(y,N)
    F = 2 * abs(F)/ N
    Fdb = 20*log10(F)
    
    # Plotting
    # Plot signal
    figure()
    plot(y)

    # Plot PSD
    figure()
    xaxis = fs*arange(0, N/2)
    plot(xaxis/N, Fdb[0:N/2])

    grid(True)
    show()

    if hex_enable == 1:
        return y_fix
    else:
        return y

signal_gen(2048, 0, 0, 0)

