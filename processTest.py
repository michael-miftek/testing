# import multiprocessing
# import time

# def update_shared_variable(shared_value):
#     with shared_value.get_lock():  # Ensure atomic updates
#         shared_value.value += 1
#         print(f"Child Process updated value to: {shared_value.value}")

# if __name__ == "__main__":
#     # Create a shared integer variable initialized to 0
#     shared_value = multiprocessing.Value('i', 0)

#     shared_class = multiprocessing.Array('', )

#     # Create and start a process to update the shared variable
#     process = multiprocessing.Process(target=update_shared_variable, args=(shared_value,))
#     process.start()
#     process.join()

#     # Print the updated value in the main process
#     print(f"Main Process sees updated value: {shared_value.value}")





#################################################################

"""
manager: <__main__.MyManager object at 0x0000029948FDC2F0>
obj: <__mp_main__.MyClass object at 0x0000018A174C65D0>
lst: [1, 2, 3]
collection: <__mp_main__.Wrapper object at 0x0000018A17A464B0>
"""

# from multiprocessing.managers import SyncManager

# class MyManager(SyncManager): pass
# class MyClass: pass

# class Wrapper:
#     def set(self, ent):
#         self.ent = ent

# MyManager.register('MyClass', MyClass)
# MyManager.register('Wrapper', Wrapper)

# if __name__ == '__main__':
#     manager = MyManager()
#     manager.start()
#     print(f"manager: {manager}")

#     try:
#         obj = manager.MyClass()
#         lst = manager.list([1,2,3])

#         print(f"obj: {obj}\nlst: {lst}")

#         collection = manager.Wrapper()
#         collection.set(lst) # executed fine
#         collection.set(obj) # raises error
#         print(f"collection: {collection}")

#     except Exception as e:
#         raise


###############################################################
"""
Worker incremented count in the shared dictionary.
Worker incremented count in the shared dictionary.
Shared dictionary contents: {'count': 2}
"""
# import multiprocessing

# def worker_function(shared_dict):
#     shared_dict['count'] = shared_dict.get('count', 0) + 1
#     print("Worker incremented count in the shared dictionary.")

# if __name__ == '__main__':
#     manager = multiprocessing.Manager()
#     shared_dict = manager.dict()

#     process1 = multiprocessing.Process(target=worker_function, args=(shared_dict,))
#     process2 = multiprocessing.Process(target=worker_function, args=(shared_dict,))

#     process1.start()
#     process2.start()

#     process1.join()
#     process2.join()

#     print("Shared dictionary contents:", dict(shared_dict))



####################################################################
"""
Changing for funsies
"""

# import multiprocessing
# import multiprocessing.managers

# def worker_function(shared_dict):
#     print(shared_dict)
#     # shared_dict['count'] = shared_dict.get('count', 0) + 1
#     print("Worker incremented count in the shared dictionary.")

# class testClass():
#     def __init__(self):
#         self.data = [1,2,3,4]
#         self.flag = False

# if __name__ == '__main__':
#     manager = multiprocessing.managers.
#     # shared_dict = manager.dict()
#     shared_obj = manager.register("custom", testClass)

#     # process1 = multiprocessing.Process(target=worker_function, args=(shared_dict,))
#     # process2 = multiprocessing.Process(target=worker_function, args=(shared_dict,))

#     process1 = multiprocessing.Process(target=worker_function, args=(shared_obj,))
#     process2 = multiprocessing.Process(target=worker_function, args=(shared_obj,))

#     process1.start()
#     process2.start()

#     process1.join()
#     process2.join()

#     print("Shared dictionary contents:", shared_obj)#dict(shared_dict))



"""This is basically here for support mostly moral"""
# example of using a manager to create a custom class
# from time import sleep
# from random import random
# from multiprocessing import Process
# from multiprocessing.managers import BaseManager
 
# # custom class
# class MyCustomClass():
#     # constructor
#     def __init__(self, data):
#         # store the data in the instance
#         self.data = data
#         self.storage = list()
#         print(f"starting: {data}")
 
#     # do something with the data
#     def task(self):
#         # generate a random number
#         value = random()
#         # block for a moment
#         sleep(value)
#         # calculate a new value
#         new_value = self.data * value
#         # Give em the ol razzle dazzle
#         self.data += 1
#         for i in range(2):
#             # store everything
#             self.storage.append((self.data, value, new_value))
#         # return the new value
#         return new_value
 
#     def get_data(self):
#         return self.data

#     # get all stored values
#     def get_storage(self):
#         return self.storage
 
# # custom manager to support custom classes
# class CustomManager(BaseManager):
#     # nothing
#     pass
 
# # custom function to be executed in a child process
# def work(shared_custom):
#     # call the function on the shared custom instance
#     value = shared_custom.task()
#     # report the value
#     print(f'>child got {value}')
 
# # protect the entry point
# if __name__ == '__main__':
#     # register the custom class on the custom manager
#     CustomManager.register('MyCustomClass', MyCustomClass)
#     # create a new manager instance
#     with CustomManager() as manager:
#         # create a shared custom class instance
#         shared_custom = manager.MyCustomClass(10)
#         # call the function on the shared custom instance
#         value = shared_custom.task()
#         # report the value
#         print(f'>main got {value}')
#         # start some child processes
#         processes = [Process(target=work, args=(shared_custom,)) for i in range(4)]
#         # processes = [Process(target=work, args=(shared_custom,)) for i in range(4)]
#         # start processes
#         count = 0
#         for process in processes:
#             process.start()
#             print(f"count: {count}\nshared_custome.data: {shared_custom.get_data()}")
#             count += 1
#         count = 0
#         # wait for processes to finish
#         for process in processes:
#             process.join()
#             print(f"count: {count}\nshared_custome.data: {shared_custom.get_data()}")
#             count += 1
#         # all done
#         print('Done')
#         # report all values stored in the central object
#         for t in shared_custom.get_storage():
#             print(t)



########################################################################

# This will not work, need to use the queue method unfortunately
from time import sleep
from random import random
from multiprocessing import Process
from multiprocessing.managers import BaseManager
import PyQt6
from PyQt6 import QtWidgets, QtGui, QtCore

class MyOtherCutomClass(QtWidgets.QWidget):
    def __init__(self, obj):
        self.count = 0


    def function_call(self):
        self.count += 1
        print("EMITTED SIGNAL CAUGHT") 
    pass

class MyCustomClass(QtWidgets.QWidget):
    # constructor
    def __init__(self, data):
        # store the data in the instance
        self.data = data
        self.storage = list()
        print(f"starting: {data}")
 
    # do something with the data
    def task(self):
        # generate a random number
        value = random()
        # block for a moment
        sleep(value)
        # calculate a new value
        new_value = self.data * value
        # Give em the ol razzle dazzle
        self.data += 1
        for i in range(2):
            # store everything
            self.storage.append((self.data, value, new_value))
        # return the new value
        return new_value
 
    def get_data(self):
        return self.data

    # get all stored values
    def get_storage(self):
        return self.storage
 
# custom manager to support custom classes
class CustomManager(BaseManager):
    # nothing
    pass
 
# custom function to be executed in a child process
def work(shared_custom):
    # call the function on the shared custom instance
    value = shared_custom.task()
    # report the value
    print(f'>child got {value}')
 
# protect the entry point
if __name__ == '__main__':
    # register the custom class on the custom manager
    CustomManager.register('MyCustomClass', MyCustomClass)
    # create a new manager instance
    with CustomManager() as manager:
        # create a shared custom class instance
        shared_custom = manager.MyCustomClass(10)
        # call the function on the shared custom instance
        value = shared_custom.task()
        # report the value
        print(f'>main got {value}')
        # start some child processes
        processes = [Process(target=work, args=(shared_custom,)) for i in range(4)]
        # processes = [Process(target=work, args=(shared_custom,)) for i in range(4)]
        # start processes
        count = 0
        for process in processes:
            process.start()
            print(f"count: {count}\nshared_custome.data: {shared_custom.get_data()}")
            count += 1
        count = 0
        # wait for processes to finish
        for process in processes:
            process.join()
            print(f"count: {count}\nshared_custome.data: {shared_custom.get_data()}")
            count += 1
        # all done
        print('Done')
        # report all values stored in the central object
        for t in shared_custom.get_storage():
            print(t)