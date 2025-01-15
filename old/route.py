
from typing import Any, Dict, AnyStr

class Route(object):
    """!
        The Route stores two or more sockets, storing a set of A->B or A->[B0, B1,...BN] relationships.
        If the route is a bidirectional path, we consider A->B as well as B->A

        It manages orchestrated sends and recoveries from members of the route.

    """
    def __init__(self) -> None:
        pass

    
    def setup(self) -> bool:
        """!
            Consumes a configuration and enables launch of other services
        """
        pass

    def teardown(self) -> bool:
        pass


    def send_AB(self) -> bool:
        """!
            Sends an outbound message
        """
        pass


    def send_BA(self) -> bool:

        """!
            Note this is not normally what takes place when a service is on the other end.
            Typically routes are not connected to from both sides in the same process.

            Typically the route exposes a single outbound socket and records the presence of
            another socket on the other end.
            
            A much more typical pattern is as follows:

            A (outbound/inbound socket->bind) <- (service owns service_A->connect) .send/recv

            or

            A (outbound socket->bind) <- (service owns service_A->connect) service_A.recv
            B (inbound socket ->connect) <-(service owns service_B->bind) service_B.send


        """
        pass

    def recv_BA(self) -> bool:
        pass

    def recv_AB(self) -> bool:
        pass

