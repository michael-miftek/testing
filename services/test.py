import time
import socket
import pickle
import random
import os
import sys
import numpy as np

## This runs at about 32000 events per second, this is on a single thread at this time
if __name__ == "__main__":
    
    #We use bind on this side of life
    #SOCK_STREAM is tcp protocol we have to use this becaues our message is too big for UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 5000))
    #Required to listen for a connection
    sock.listen(1)
    #Required to accept connection and we will use the connection instead of the sock like with UDP
    con, addr = sock.accept()
    sock.settimeout(5)
    # start = time.monotonic() + 1
    # c = 0
    while True:
        #Using a try catch to easily debug at this time but if there is a timeout error could just be told to continue
        try:
            #12 channels of 1250 uint16s should be 30000 bytes so 65536 should be more than enough
            _ = con.recv(65536)
            # c+=1
        except Exception as e:
            print(e)
            if str(e) == 'timed out':
                continue
            else:
                break
        # if start < time.monotonic():
        #     start += 1
        #     print(c)
        #     c=0
        #     # break