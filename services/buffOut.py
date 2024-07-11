import time
import socket
import pickle
import random
import os
import sys
import numpy as np


def read():
    with open('daqbuff.npy', 'rb') as file:
        a = np.load(file)
        file.close()
        return a

if __name__ == "__main__":
    
    #Use this same 3 lines and change the connect function to bind that will set up the receiving side
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 5000))
    sock.settimeout(5)
    
    arr = read()
    
    
    while True:
        #Using a try catch to easily debug at this time but if there is a timeout error could just be told to continue
        data = pickle.dumps(arr[random.randint(0,64)])
        # data = pickle.dumps(random.randint(0,64))
        try:
            # sock.sendall(pickle.dumps(arr[random.randint(0,64)]))
            sock.sendall(data)
        except Exception as e:
            print(e)
            break