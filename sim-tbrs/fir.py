import csv
from pylab import *

class FIR(object):
    """Class to implement finite impulse response (FIR) filter.
    Objects must be initialized with the name of a CSV file that
    contains the FIR coefficients."""

    # Define any class variables (shared by all instances) here.

    def __init__(self,filename):
        """FIR constructor. Requires name of a CSV file that contains
        the filter coefficients. Initializes the object coefficients
        from the file. Also computes the filter signal and noise
        gain."""


        # Read in the impulse response
        self.h = []
        reader = csv.reader(open(filename,"rb"))
        for row in reader:
            h_n = float(row[1])
            self.h.append(h_n)

        self.numCoeff = len(self.h)
        self.h = asarray(self.h)
        # Signal gain is sum of weights
        self.G_s = reduce(add,self.h)
        h_sq = self.h*self.h
        # Noise gain is the square root of the sum of the square of the weights
        self.G_n = sqrt(reduce(add,h_sq))
        # Compute integer power of 2 signal gain
        self.G_si = round(log(self.G_s)/log(2))
        self.G_si = 2**self.G_si
        # print "Filter %s, G_s = %f, G_n = %f" % (filename,self.G_s,self.G_n)

    def filter(self,x,scaleFlag):
        """Method that convolve an input vector and the FIR impulse
        response vector."""

        # Note: This could easily be done with SciPy convolve function, but
        # this code is to be ported to C/C++/C#.

        # Calculate input vector length and minimum FFT size
        Nx = len(x)
        Nfft = Nx + self.numCoeff - 1
        Nfft = log(Nfft)/log(2)
        Nfft = ceil(Nfft)
        Nfft = 2**Nfft

        # Compute complex conjugate of FFT of zero-padded impulse response.
        h_f = zeros(Nfft)
        h_f[0:self.numCoeff] = self.h
        h_f = fft(h_f)

        # Compute the FFT of the zero-padded input.
        x_f = zeros(Nfft)
        x_f[0:Nx] = x
        x_f = fft(x_f)
        # Compute point-by-point complex vector multiply.
        y_f = h_f * x_f
        # Inverse FFT
        y_f = ifft(y_f)
        # Extract fully overlapped convolution samples
        y = y_f.real[0:(Nx - self.numCoeff + 1)]
        if scaleFlag == 0:
            y = (1/self.G_si) * y
        elif scaleFlag == 1:
            y = (1/self.G_s) * y
        else:
            y = (1/self.G_n) * y


        return y

