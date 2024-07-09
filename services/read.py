import psycopg
import numpy as np
import time
import zmq
import json

#NOTE:  This will need to be added to as other items are added to the database
FEATURE_NAMES = ["PEAKHEIGHT"] #, "PEAKAREA", "PEAKWIDTH", "COUNTTOTAL"]

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
    return cursor.fetchone()
#-----------------------------------------------------------------------#



if __name__ == "__main__":
    db_connection = setup_db()
    db_cur = db_connection.cursor()
    currTime = time.time()
    limit = 300

    context = zmq.Context()
    socket = context.socket(zmq.RADIO)
    # socket.connect('udp://*:9005')
    socket.connect('udp://127.0.0.1:9005')
    tag = b"example"

    while True:
        if currTime <= time.time():
            currTime += (1/60)
            x = read(db_cur, 0, 0)
            y = read(db_cur, 6, 0)
            ch1 = np.array(x[0][-10:])
            ch2 = np.array(y[0][-10:])
            # combine = np.array([ch1, ch2])
            print(ch1)
            print(ch2)
            # print(json.dumps(combine))
            # print(f"1: {ch1} 2: {ch2}")
            # socket.send_multipart([tag, x[0][-300:], y[0][-300:]])
            #NOTE:  This throws and error because of '[' need to only send a list of numbers with no brackets
            try:
                # socket.send_multipart([str(ch1).encode(), str(ch2).encode()])
                socket.send_multipart(ch1)
                # socket.send(json.dumps(combine), group='graphs')
            except Exception as e:
                print(e)
                break
            # print(f"channel{y}: {len(x[0])}")
