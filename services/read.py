import psycopg
import numpy as np
import time
import zmq
import socket
import json
import pickle
import random

#NOTE:  This will need to be added to as other items are added to the database
FEATURE_NAMES = ["PEAKHEIGHT"] #, "PEAKAREA", "PEAKWIDTH", "COUNTTOTAL"]
TIMESTAMP = 0

def setup_db():
    #NOTE:  These items might have to be changed depending on who is running the tests
    db_params = {
    "host": "127.0.0.1",
    "dbname": "postgres",
    "user": "postgres",
    "password": "password",
    "port": "5432"
    }

    db_conn = psycopg.connect(**db_params)
    return db_conn

#   This is what is important   #
#-----------------------------------------------------------------------#
def read(cursor, col_num, feat):
    cursor.execute(f"SELECT ARRAY_AGG(ch{col_num}) FROM {FEATURE_NAMES[feat]}")
    #NOTE:  Need to get latest time stamp from this as well probably need to change date to what it is in the db
    # cursor.execute(f"SELECT ARRAY_AGG(ch{col_num}) FROM {FEATURE_NAMES[feat]} WHERE date > {TIMESTAMP}")
    return cursor.fetchone()
#-----------------------------------------------------------------------#



if __name__ == "__main__":
    db_connection = setup_db()
    db_cur = db_connection.cursor()
    currTime = time.monotonic()
    limit = 300

    #NOTE:  ZMQ issues prevent moving forward at this time in python switching to sockets
    # context = zmq.Context()
    # socket = context.socket(zmq.RADIO)
    # # socket.connect('udp://*:9005')
    # socket.connect('udp://127.0.0.1:9005')
    # tag = b"example"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('127.0.0.1', 9005))
    sock.settimeout(5)

    while True:
        if currTime <= time.monotonic():
            currTime += (1/60)
            x = read(db_cur, 0, 0)
            y = read(db_cur, 6, 0)
            rng = random.randint(0,65000)
            ch1 = np.array(x[0][rng:rng+5000])
            ch2 = np.array(y[0][rng:rng+5000])
            # ch1 = np.array(x[0][-300:])
            # ch2 = np.array(y[0][-300:])
            # combine = [ch1,ch2]
            data = pickle.dumps([ch1,ch2])
            try:
                sock.sendall(data)
            except Exception as e:
                print(e)
                break
