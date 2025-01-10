import zmq
import zlib
import pickle
import numpy as np
from typing import Dict, Any, cast

socket_types = {
    'dealer': zmq.DEALER,
    'router': zmq.ROUTER,
    'pub': zmq.PUB,
    'sub': zmq.SUB,
    'push': zmq.PUSH,
    'pull': zmq.PULL,
    'req': zmq.REQ,
    'rep': zmq.REP
}


class Socket(object):
    """!
    This is essentially a wrapper class for the ZMQ Socket, that stores a set of name attributes
    and reference attributes. 

    Each Socket in a route is paired with at least one other socket. This provides a Left-Right 
    handedness to the relationship. We use this because the sockets have to be polled at each end

    Attributes:


    """
    def __init__(self, context, name, config):
        """!
            Instantiates the socket instance
        """
        self.context = context
        self.name = name
        self.address = config['address']
        self.handle = config['handle']
        self.socket_type = config['socket_type']
        self.bport = None
        self.connected = []
        self.mates = {}


        self._socket = self.context.socket(socket_types[self.socket_type.lower()])
        self._socket.set_string(zmq.IDENTITY, f"{self.handle}")

        #self.bind(self.address)

    def bind(self, address=None):
        """!
            Binds the socket (A or client side) to an address.
        """
        try:
            if not address:

                self._socket.bind(self.address)
                self._socket.set_string(zmq.IDENTITY, f"{self.name} bport: {self._socket.last_endpoint.decode('ascii')}")
                self.bport = self._socket.last_endpoint.decode('ascii')

            else:
                self._socket.bind(address)
                self._socket.set_string(zmq.IDENTITY, f"{self.name} bport: {address}")
                self.bport = address

        except Exception as e:
            # NOTE: promote logging
            print(f"failed to bind a socket: {self.name} error: {e}")

    def unbind(self, address=None):
        """!
            Binds the socket (A or client side) to an address.
        """
        try:
            if not address:
                self._socket.unbind(self._socket.last_endpoint)
                self._socket.set_string(zmq.IDENTITY, f"{self.name} bport: {None}")
                self.bport = None

            else:
                self._socket.unbind(address)
                self._socket.set_string(zmq.IDENTITY, f"{self.name} bport: {None}")
                self.bport = None

        except Exception as e:
            # NOTE: promote logging
            print(f"failed to unbind a socket: {self.name} error: {e}")


    def connect(self, address):
        """!
            Connects the socket (A or client side) to an address.
        """
        try:
            self._socket.connect(address)
            self.connected.append(address)

        except Exception as e:
            # NOTE: promote logging
            print(f"failed to connect a socket: {self.name} error: {e}") 

    def disconnect(self, address):
        """!
            Disconnects the socket (A or client side) to an address.
        """
        try:
            if address in self.connected:
                self._socket.disconnect(address)
                self.connected.remove(address)

            else:
                print(f"attempted to disconnect {address}; this is not in {self.name} connected sockets.")

        except Exception as e:
            # NOTE: promote logging
            print("failed to disconnect a socket: {self.name} error: {e}") 

    def close(self):
        """!
            Normally shouldn't be required unless a context doesn't exit
        """
        try:
            return self._socket.close()

        except Exception as e:
            print(f"failed to close socket: {self.name}: {e}")

    @property
    def closed(self):
        return self._socket.closed


    def get(self, attribute):
        """!
            An implementation of the .get method. Only returns binary results
        """
        try:
            return self._socket.get(attribute)

        except Exception as e:
            print(f"failed to get attribute: {e}")

    def getsockopt(self, attribute):
        """!
        An implementation of the .get method. Only returns string results
        """
        try:
            return self._socket.getsockopt(attribute)

        except Exception as e:
            print(f"failed to get attribute: {e}")

    def send_string(self, msg, flags=0, copy=True, encoding='utf-8', **kwargs):
        try:
            return self._socket.send_string(msg, flags, copy, encoding, **kwargs)

        except Exception as e:
            print(f"failure to send string message on socket: {self.name} at {self.address}: {e}")

    def recv_string(self, flags=0, encoding='utf-8'):
        try:
            return self._socket.recv_string(flags, encoding)

        except Exception as e:
            print(f"failure to send string message on socket: {self.name} at {self.address}: {e}")


    def send_multipart(self, seq, flags=0, copy=True, track=False, **kwargs):
        try:
            self._socket.send_multipart(seq, flags, copy, track, **kwargs)
        
        except Exception as e:
            print(f"failure to send multipart message on socket: {self.name} at {self.address}: {e}")

    def recv_multipart(self, flags=0, copy=True, track=False):
        try:
            return self._socket.recv_multipart(flags, copy, track)
        
        except Exception as e:
            print(f"failure to recv multipart message on socket: {self.name} at {self.address}: {e}")


    def send_json(self, json, flags=0, **kwargs):
        try:
            return self._socket.send_json(json, flags, **kwargs)

        except Exception as e:
            print(f"failure to send json message on socket: {self.name} at {self.address}: {e}")

    def recv_json(self, flags=0, **kwargs):
        try:
            return self._socket.recv_json(flags, **kwargs)
        
        except Exception as e:
            print(f"failure to send json message on socket: {self.name} at {self.address}: {e}")

    def send_zipped_pickle(
        self, obj: Any, flags: int = 0, protocol: int = pickle.HIGHEST_PROTOCOL
    ) -> None:
        """pack and compress an object with pickle and zlib."""
        pobj = pickle.dumps(obj, protocol)
        zobj = zlib.compress(pobj)
        print('zipped pickle is %i bytes' % len(zobj))
        return self._socket.send(zobj, flags=flags)

    def recv_zipped_pickle(self, flags: int = 0) -> Any:
        """reconstruct a Python object sent with zipped_pickle"""
        zobj = self._socket.recv(flags)
        pobj = zlib.decompress(zobj)
        return pickle.loads(pobj)

    def send_array(
        self, A: np.ndarray, flags: int = 0, copy: bool = True, track: bool = False
    ) -> Any:
        """send a numpy array with metadata"""
        md = dict(
            dtype=str(A.dtype),
            shape=A.shape,
        )
        self._socket.send_json(md, flags | zmq.SNDMORE)
        return self._socket.send(A, flags, copy=copy, track=track)

    def recv_array(
        self, flags: int = 0, copy: bool = True, track: bool = False
    ) -> np.ndarray:
        """recv a numpy array"""
        md = cast(Dict[str, Any], self._socket.recv_json(flags=flags))
        msg = self._socket.recv(flags=flags, copy=copy, track=track)
        A = np.frombuffer(msg, dtype=md['dtype'])  # type: ignore
        return A.reshape(md['shape'])

    def add_mate(self, mate_socket):
        try:
            self.mates[mate_socket.name] = mate_socket

        except Exception as e:
            print(f"socket {self.name} unable to add mate: {mate_name}")

    def is_mate(self, potential_mate):
        try:

            matedAB = potential_mate.name in self.mates
            matedBA = self.name in potential_mate.mates

            return matedAB or matedBA
        
        except Exception as e:
        
            print(f"socket {self.name} unhandled error for is_mate: {e}")   


    def remove_mate(self, mate_name):
        try:
            self.mates.pop(mate_name)

        except Exception as e:
            print(f"socket {self.name} unable to remove mate: {mate_name}")