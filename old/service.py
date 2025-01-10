import os
import sys
import shlex
import errno
import inspect
import delegator
from subprocess import Popen
from queue import Full, Empty
from multiprocessing import Process, Queue


class Service(object):
    """!
        A handle/mixin class that exports a number of methods required to bind to another program. 
        This basic concept enables all programs with conforming command structure to bind to the kernel.

        Please see the all-important process creation flags help menu:
        https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags?redirectedfrom=MSDN

        

    """
    def __init__(self, name, type="managed"):

        # let's see the configuration is going to need a reference to the process 
        # this could be either module or command-line interface

        self.name = name
        self.in_queue = None # this implies that we might refactor this into subclasses
        self.out_queue = None


        

    def start(self, method=""):
        """!
            This method provides the tooling to launch processes with different management methods.
            The basic idea here is that the kernel provides the following support:

            Open Ports: The kernel opens up a port that simply exists and traffic is not monitored
            Detached Processes: The kernel has access through the configuration to 
                                launch detached processes
            Managed subprocesses: The kernel opens up a subprocess which is managed 
                                  by the lifetime of the kernel
        """
        # The default assumption is that we are using a managed subprocess. 

        pass

    def launch_cmd(self, launch_cmd, block=False):
        """!
            Launches a detached (typically nonblocking) process using OS, returning a status 
            from delegator if successful. 
            Typical commands: 

            'python my_awesome_launch_script.py -c cmd1 -d cmd2 -e cmd3'

            this command is split using shlex and converted to a list:
            ['python', 'my_awesome_launch_script.py', '-c', 'cmd1', '-d', 'cmd2', '-e', 'cmd3']

            This command would be stored in the service configuration and updated as necessary
        """

        try:

            c = delegator.run(shlex.split(launch_cmd), block=block)
            
            if not c.ok:
                raise RuntimeError(f"Service failed to launch unmanaged process! return code: {c.return_code}")

            else:
                print(f"process launch ok: {c.pid}")
            
            self.pid = c.pid

            return c
        
        except Exception as e:

            print(f"Unhandled error while Service failed to launch command: {launch_cmd}: {e}")

            return None

    def launch_qprocess(self, classpath, classname, **kwargs):
        """!
            Launches an unmanaged process from an imported file. 
            This uses the Process(.run()) method iterface that is commonly deployed throughout
            legacy Granite. Shutdown requres a "stop" or "quit" command into the api.

            The expectation is that this process still connects over 

            {}

        """
        try:
            # try to import a class 
            process = self.import_from_file(classpath, classname)
            # communication queues*
            self.in_queue = Queue()
            self.out_queue = Queue()

            # implied signature of the service service: (self.in_queue, self.out_queue, **kwargs)
            self.process = Process(target=process, args=(self.in_queue, self.out_queue), kwargs=kwargs)

            self.process.start()

            self.pid = self.process._identity

        except Exception as e:

            print(f"Service failed to launch unmanaged process: {classpath} {classname}: {e}")


    def import_from_file(self, filepath, filename, classname):
        """!
            Imports a python class defined in a module which is configured, not part of the package.
        """
        try:
            sys.path.append(filepath)
            loaded_module = __import__(filename)
            classes = {cls_name:cls_obj for cls_name, cls_obj in inspect.getmembers(sys.modules[filename]) if inspect.isclass(cls_obj)}

            if classname in classes:
                return classes[classname]
            
            else:

                raise RuntimeError(f"Service unable to spawn configured class: classname {classname} not found in module: {filename}")

        except Exception as e:
            
            print(f"Service failed to import object from file: {filepath} {filename} {classname}: {e}")


    @property
    def is_alive(self):

        if self.pid is not None:
            return self.pid_exists(self.pid)
        else:
            return False


    def pid_exists(self, pid):
        """Check whether pid exists in the current process table."""
        if pid in (0, 4):
            return True
        try:
            os.kill(pid, 0)
        except OSError as err:
            if err.errno == errno.ESRCH:
                # ESRCH == No such process
                return False
            elif err.errno == errno.EPERM:
                # EPERM clearly means there's a process to deny access to
                return True
            else:
                # According to "man 2 kill" possible error values are
                # (EINVAL, EPERM, ESRCH) therefore we should never get
                # here. Return error.
                raise err
        else:
            return True

    def stop(self):
        pass

    def state(self):
        pass 

