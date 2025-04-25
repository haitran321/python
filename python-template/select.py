#!/usr/bin/env python

from __future__ import division

import socket
import select
import struct

# Set the socket parameters
in_host_1 = "172.16.80.91"
in_port_1 = 1001
buf = 1024

in_host_2 = "172.16.80.92"
in_port_2 = 1002

# ------------------------------------------- Begin Main Program --------------------------
if __name__ == '__main__' :

    # Define incoming socket
    in_addr_1 = (in_host_1,in_port_1)
    in_sock_1 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    in_sock_1.bind(in_addr_1)

    # Define incoming socket
    in_addr_2 = (in_host_2,in_port_2)
    in_sock_2 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    in_sock_2.bind(in_addr_2)

    # Define select loop input list
    input = [in_sock_1, in_sock_2]

    running = 1
    while running:
        inputready,outputready,exceptready = select.select(input, [], [])

        for s in inputready:
            if s == in_sock_1:
                data,addr = in_sock_1.recvfrom(buf)
                if data == 'exit':
                    running = 0
                else:
                    msgId = msgSize = unpack(">l", data[0:4])[0]

            elif s == in_sock_2:
                data,addr = in_sock_2.recvfrom(buf)
                if data == 'exit':
                    running = 0
                else:
                    msgId = msgSize = unpack(">l", data[0:4])[0]


    in_sock_1.close()
    in_sock_2.close()



