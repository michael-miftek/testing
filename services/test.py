import time
import socket
import pickle
import random
import os
import sys
import numpy as np


if __name__ == "__main__":
    
    #We use bind on this side of life
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock = socket.socket(socket.AF_IRDA, socket.SOCK_STREAM, 0)
    sock.bind(('127.0.0.1', 5000))
    sock.settimeout(5)
    start = time.time() + 1
    c = 0
    while True:
        #Using a try catch to easily debug at this time but if there is a timeout error could just be told to continue
        try:
            #12 channels of 1250 uint16s should be 30000 bytes so 65536 should be more than enough
            _ = sock.recv(65536)
            c+=1
        except Exception as e:
            print(e)
            continue
        if start < time.time():
            start += 1
            print(c)
            c=0
            # break