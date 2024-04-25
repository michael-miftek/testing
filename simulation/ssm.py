from collections import OrderedDict
import time

import zmq

"""
This is just the client python script added in, will ater as we go
"""

HEARTBEAT_LIVENESS = 3     # 3..5 is reasonable
HEARTBEAT_INTERVAL = 1.0   # Seconds

#  Paranoid Pirate Protocol constants
PPP_READY = b"\x01"      # Signals worker is ready
PPP_HEARTBEAT = b"\x02"  # Signals worker heartbeat


"""
Start the worker class we can pass out from here
"""
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

# So the basic idea is to turn this into an object that does everything we want the SSM to do. 
class SystemStateManager(object):

    """!
    SSM Responsibilities:
    
    1.Routes work between various services
    2. Keeps a system clock
    3. Monitors heartbeats between each connected service
    4. Produces a central log
    5. Producs other reports on request
    
    
    
    """


    def __init__(self, config) -> None:
        self.worker_queue = WorkerQueue()# I had imagined that we may or may not have more than one worker for a given service. It's a little murky to me at this moment. 
        
        ## This is a dict passed in from main/ui/controlpanel process that corresponds to a config file
        self.registered_services = {} # we need a way to track all registered services that are passing data through the ssm

        # example schema of registered services:

        """
        List of dicts from a loaded config file (JSON format?)
        self.config
            ['registered_services'] = 
                {
                'frontend_service_A': 
                    {
                    'description':'a basic service that provides some output to visualization',
                    'inbound_socket': '5556', 
                    'outbound_socket':  '5557',
                    'inbound_socket_type':'REP',
                    'outbound_socket_type':'REQ',
                    'worker_service': 'backend_service_A'
                    },
                'backend_service_A': 
                    {
                    'description': 'a service that does work for frontend service A',
                    'inbound_socket': '5558',
                    'outbound_socket': '5559',
                    }
                }

            ['optics_config'] = 
                {

                }

            ['fluidics_config'] = 
                {
                    
                }

            ['oscilloscope_config'] = 
                {
                    
                }

            ['photon_config'] = 
                {
                    
                }

            ['scatter_config'] = 
                {
                    
                }

        """


        ## This is a list of different heartbeats to keep track of
        self.heartbeats = {}

        ## This is called poller in the example but monitor is a more meaningful name for its tasks
        self.monitor = {}

        # each expression of a module has the following components: 
        ## This is the list socket that the front end is listening on
        # self.frontend = []    # are we going to have the frontend listen on sockets
        ## This is a list of sockets used by the back end, we can populate it on init or we can use 
        #  registered services and populate that on init
        self.backend = []

        #NOTE: Idea right now is that this would run like eclipse where it boots up a load screen to
        #load a config and then populated a main page/control panel that has menus and other items
        #that support each view
        #NOTE: This setup will eventually change and we might have more things inside the actual
        #control panel
        ## This is the optoelectronics tab
        self.optics_control_panel = None
        ## This is the fluidics tab
        self.fluidics_control_panel = None
        ## This is the oscilloscope tab
        self.oscilloscope_view = None
        ## This is the photon tab
        self.photon_view = None
        ## This is the scatter plot tab
        self.scatter_view = None

        #NOTE: Need to think through the player because we will not have any ZMQ protocols
        #-----------------------------------------------#
        #                   Start SSM                   #
        #-----------------------------------------------#
        self.start()
        self.setup_ui(config)
        self.run()
        #-----------------------------------------------#
        #                   End SSM                     #
        #-----------------------------------------------#
        

    def register_services(self):
        
        assert len(self.config['services'])





    def start(self):
        """!
        This method is called to start the state manager and returns nothing

        What does startup look like?
        1. Exposes the SSM to the system
        2. Undergoes discovery for all connected clients and workers
        3. Start system clock
        4. Probably waits for greetings/handshakes from user control
        5. Starts outputting to log (?)
        6. 

        """
        #Obtain a list of expected services and expected endpoints (addresses) from configuration
        self.register_services(self.config)


        count = 0
        ## Setup the backend list and bind it to the input sockets, sets up the heartbeats to track
        #  and then registers the sockets to poll through
        for key, value in self.registered_services.items():
            # self.frontend.append(context.socket(zmq.ROUTER))
            # self.frontend.bind(value)
            self.backend.append(context.socket(zmq.ROUTER))
            self.backend.bind(value)

            # Scheme for heart beat will be the key (name of worker) and initialized as 0
            # Not entirely certain that this will be used at this time
            self.heartbeats.update({f"{key}", 0})

            # This updates a dictionary with {key, {socket, event mask}} where key is the name of
            # the service and socket and event mask will be returned in a list from the Poller object
            # that has been registered with the corresponding socket, this scheme seems complex at
            # first but will make searching for updates much cleaner
            temp = zmq.Poller()
            temp.register(self.backend[count], zmq.POLLIN)
            temp.register(self.frontend[count], zmq.POLLIN)
            self.monitor.update(f"{key}", dict(temp.poll(timeout=1000)))

            count += 1

        
    def setup_ui(self, config):
        """!
        This method is called at the end of the start method and sets up all the different views
        that are currently tabs.

        In this refactor the only thing that should really be send to these views is their 
        corresponding config which will also be part of the self.config
        """
        self.optics_control_panel = OpticsControlPanel(config['optics_config'])
        self.fluidics_control_panel = FluidicsControlPanel(config['fluidics_config'])
        self.oscilloscope_view = OscilloscopeView(config['oscilloscope_config'])
        self.photon_view = PhotonView(config['photon_config'])
        self.scatter_view = ScatterView(config['scatter_config'])


    def run(self):
         """!
         This method is called to run the process that will run indefinitely in the SSM
        
         Start Conditions:
            1. User sends a START or RESTART signal         

         Interrupt conditions:
            1. User sends as STOP or RESTART SIGNAL
            2. Unknown system failure. This may mean we need a secondary watchdog process - this could be just the user interface (Control Panel/UI)
         
         
         """
         while True:
            # # Sets up which to focus on either both or workers # maybe this is wrong
            # if len(self.worker_queue) > 0:
            #     poller = poll_both
            # else:
            #     # if nothing is in the working
            #     poller = poll_workers
            # # Starts to poll with a timeout of (1000 seconds) returns event in the form {socket, event_mask}
            # socks = dict(poller.poll(HEARTBEAT_INTERVAL * 1000))

            # Seach through our dictionary and for each item check to see if it is a POLLIN if so
            # grab a message
            for key, item in self.monitor.items():
                # The more I think about this not sure if we want to do this or just assume that if
                # it is in the dict then we know that we want it, also wondering if we shouldn't 
                # just (POLLIN | POLLOUT) for each item
                if item.get(backend) == zmq.POLLIN:
                    # This is the logic to grabe the message we just iterate through the total of
                    # the dictionary
                    pass
            pass
            
            # Handle worker activity on backend, we set this when we set what to poll -> poll_workers
            # if socks.get(backend) == zmq.POLLIN:
            #     # Use worker address for LRU routing
            #     frames = backend.recv_multipart()
            #     if not frames:
            #         break
                
            #     if printFlag:
            #         print(f"frame[0]: {frames[0]}")
                    
            #     address = frames[0]
            #     workers.ready(Worker(address))

            #     # Validate control message, or return reply to client
            #     msg = frames[1:]
            #     if len(msg) == 1:
                    
            #         if msg[0] not in (PPP_READY, PPP_HEARTBEAT):
            #             print("E: Invalid message from worker: %s" % msg)
            #     else:
            #         #Send back a ready signal or a heartbeat
            #         frontend.send_multipart(msg)

            #     # Send heartbeats to idle workers if it's time
            #     if time.time() >= heartbeat_at:
            #         for worker in workers.queue:
            #             msg = [worker, PPP_HEARTBEAT]
            #             backend.send_multipart(msg)
            #         heartbeat_at = time.time() + HEARTBEAT_INTERVAL


            # if socks.get(frontend) == zmq.POLLIN:
            #     frames = frontend.recv_multipart()
            #     if not frames:
            #         break

            #     frames.insert(0, workers.next())
            #     backend.send_multipart(frames)


            # workers.purge()
            # printFlag = False # I'm tryint to understand the point of all this printFlag nonsense
            

if __name__ == "__main__":
    printFlag = True
    context = zmq.Context(1)

    # Though at the moment is maybe we want a try catch when binding
    # frontend_sockets = []
    # backend_sockets = []

    # different socket types are listed in socket method in the conext class on ZMQ
    frontend = context.socket(zmq.ROUTER) # ROUTER
    backend = context.socket(zmq.ROUTER)  # ROUTER

    #this is of class type socket
    frontend.bind("tcp://*:5555") # For clients
    backend.bind("tcp://*:5556")  # For workers

    #Class poller polls for I/O on socket or fd -> file descriptor
    #Polling frontend and backend 
    poll_workers = zmq.Poller()
    poll_workers.register(backend, zmq.POLLIN)

    poll_both = zmq.Poller()
    poll_both.register(frontend, zmq.POLLIN)
    poll_both.register(backend, zmq.POLLIN)

    workers = WorkerQueue()

    heartbeat_at = time.time() + HEARTBEAT_INTERVAL

    """
    This forms a queue and pops through them for the workers, ours will move the while true to be
    just the conditonal .get for frontend and backend, if there is an issue with the heart beat we
    would have an error condition to handle

    Items:
    
    backend: 
        DAQ
        MainBoard
        Fluidics Controller

    frontend:
        Control Panel
        Scatter Plots
        Fluidics
        Optoelectronics

    Extras: (Not going to be heard back from)
        Oscilloscope View
        Photon View

    """
    while True:
        # Sets up which to focus on either both or workers
        if len(workers.queue) > 0:
            poller = poll_both
        else:
            poller = poll_workers
        # Starts to poll with a timeout of (1000 seconds) returns event in the form {socket, event_mask}
        socks = dict(poller.poll(HEARTBEAT_INTERVAL * 1000))

        # Handle worker activity on backend, we set this when we set what to poll -> poll_workers
        if socks.get(backend) == zmq.POLLIN:
            # Use worker address for LRU routing
            frames = backend.recv_multipart()
            if not frames:
                break
            
            if printFlag:
                print(f"frame[0]: {frames[0]}")
            address = frames[0]
            workers.ready(Worker(address))

            # Validate control message, or return reply to client
            msg = frames[1:]
            if len(msg) == 1:
                if msg[0] not in (PPP_READY, PPP_HEARTBEAT):
                    print("E: Invalid message from worker: %s" % msg)
            else:
                #Send back a ready signal or a heartbeat
                frontend.send_multipart(msg)

            # Send heartbeats to idle workers if it's time
            if time.time() >= heartbeat_at:
                for worker in workers.queue:
                    msg = [worker, PPP_HEARTBEAT]
                    backend.send_multipart(msg)
                heartbeat_at = time.time() + HEARTBEAT_INTERVAL


        if socks.get(frontend) == zmq.POLLIN:
            frames = frontend.recv_multipart()
            if not frames:
                break

            frames.insert(0, workers.next())
            backend.send_multipart(frames)


        workers.purge()
        printFlag = False