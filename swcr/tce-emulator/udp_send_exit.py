# Client program

from socket import *

# Set the socket parameters
host = "172.16.80.91"
port = 9005

addr = (host,port)

# Create socket
UDPSock_diag = socket(AF_INET,SOCK_DGRAM)

#Send messages
UDPSock_diag.sendto("exit".encode(),addr)

# Close socket
UDPSock_diag.close()
