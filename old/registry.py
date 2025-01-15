import zmq

class Registry(object):
    """!
        The registry lives inside the ssm_service_runtime. This object
        manages all of the route and service Buildup/teardown and messages

        Routes and their associated Services together are an Group.

        Registry->{Route->Socket, Service}


    """
    def __init__(self, context):
        self.context = context
        self.poller = zmq.Poller()
        self._services = {} ## Groupname: Group # good design question: Should this be an exposed variable
        self._routes = {}

    def setup(self, config):
        """!
            This consumes the registry configuration and builds the routes (but does not start)
        """
        pass

    def list_routes(self):
        pass

    def list_services(self):
        pass

    def active_services(self):
        pass

    def activate_service(self, service_name):
        """!
            This is a launch command from os. To start a given service
        """
        pass

    def deactivate_service(self, service_name):

        """!
            Kills the service
        """

        pass

    def register_service(self):
        pass

    def deregister_service(self):
        pass