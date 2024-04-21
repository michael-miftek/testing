from collections import OrderedDict
import time

import zmq
import ntplib
c = ntplib.NTPClient()

HEARTBEAT_LIVENESS = 3     # 3..5 is reasonable
HEARTBEAT_INTERVAL = 1.0   # Seconds

#  Paranoid Pirate Protocol constants
PPP_READY = b"\x01"      # Signals worker is ready
PPP_HEARTBEAT = b"\x02"  # Signals worker heartbeat


class Worker(object):
    def __init__(self, address):
        self.address = address
        self.expiry = time.time() + HEARTBEAT_INTERVAL * HEARTBEAT_LIVENESS

class WorkerQueue(object):
    def __init__(self):
        self.queue = OrderedDict()

    def ready(self, worker):
        self.queue.pop(worker.address, None)
        self.queue[worker.address] = worker

    def purge(self):
        """Look for & kill expired workers."""
        t = time.time()
        expired = []
        for address, worker in self.queue.items():
            if t > worker.expiry:  # Worker expired
                expired.append(address)
        for address in expired:
            print("W: Idle worker expired: %s" % address)
            self.queue.pop(address, None)

    def next(self):
        address, worker = self.queue.popitem(False)
        return address

context = zmq.Context(1)

frontend = context.socket(zmq.ROUTER) # ROUTER
backend = context.socket(zmq.ROUTER)  # ROUTER
frontend.bind("tcp://192.168.1.104:5555") # For clients
backend.bind("tcp://192.168.1.104:5556")  # For workers

poll_workers = zmq.Poller()
poll_workers.register(backend, zmq.POLLIN)

poll_both = zmq.Poller()
poll_both.register(frontend, zmq.POLLIN)
poll_both.register(backend, zmq.POLLIN)

workers = WorkerQueue()

heartbeat_at = time.time() + HEARTBEAT_INTERVAL

startSync = c.request('pool.ntp.org').tx_time * 1000000000      # This sets the ntptime to be in nanoseconds to match time.time_ns()
startTime = time.time_ns()

while True:
    if len(workers.queue) > 0:
        poller = poll_both
    else:
        poller = poll_workers
    socks = dict(poller.poll(HEARTBEAT_INTERVAL * 1000))

    # Handle worker activity on backend
    if socks.get(backend) == zmq.POLLIN:
        # Use worker address for LRU routing
        frames = backend.recv_multipart()
        if not frames:
            break
        
        # currTime = c.request('pool.ntb.org')
        #Original
        # print(f"server recieved frames: {frames} at time: {time.time_ns()}")
        #Attempt 1
        # print(f"server recieved frames: {frames} at time: {(time.time_ns() - startTime) + startSync: 20.0f}")
        #Attempt 2
        print(f"server recieved frames: {frames} at time: {c.request('pool.ntp.org').tx_time}")
        address = frames[0]
        workers.ready(Worker(address))
        if frames[1] == b"stop":
            break

        # Validate control message, or return reply to client
        # msg = frames[1:]
        # if len(msg) == 1:
        #     if msg[0] not in (PPP_READY, PPP_HEARTBEAT):
        #         print("E: Invalid message from worker: %s" % msg)
        # else:
        #     frontend.send_multipart(msg)

        # Send heartbeats to idle workers if it's time
    #     if time.time() >= heartbeat_at:
    #         for worker in workers.queue:
    #             msg = [worker, PPP_HEARTBEAT]
    #             backend.send_multipart(msg)
    #         heartbeat_at = time.time() + HEARTBEAT_INTERVAL
    # if socks.get(frontend) == zmq.POLLIN:
    #     frames = frontend.recv_multipart()
    #     if not frames:
    #         break

        frames.insert(0, workers.next())
        backend.send_multipart(frames)


    workers.purge()