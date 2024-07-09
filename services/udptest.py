import time

import zmq

ctx = zmq.Context.instance()
radio = ctx.socket(zmq.RADIO)
dish = ctx.socket(zmq.DISH)
dish.rcvtimeo = 1000

dish.bind('udp://*:5556')
# dish.join(b'numbers')
radio.connect('udp://127.0.0.1:5556')

string = b'this is a test'
for i in range(10):
    time.sleep(0.1)
    # radio.send(f'{i:03}'.encode('ascii'), group='numbers')
    radio.send_multipart(string)
    try:
        msg = dish.recv_multipart(copy=False)
    except zmq.Again:
        print('missed a message')
        continue
    print(f"Received {msg}")

dish.close()
radio.close()
ctx.term()