# https://stackoverflow.com/questions/19233246/python-update-local-variable-in-a-parallel-process-from-parent-program
import time


# def loop(i):
#     while i.value <= 510:
#         print(i.value)
#         i.value += 1
#         time.sleep(1)

# if __name__ == "__main__":
#     # NOTE: Value and Array are options but it looks like Manager allows us to use python types and 
#     #       alter them as such so to use a dict attribute Manager might be the move
#     from multiprocessing import Process, Value

#     i = Value("i", 1)  # "i" for integer, initial value 1
#     p = Process(target=loop, args=(i,))
#     p.start()
#     for base in range(100, 600, 100):
#         time.sleep(2)
#         print(f'base: {base}')
#         i.value = base

from multiprocessing import Process, Manager

def f(d, l):
    d[1] = '1'
    d['2'] = 2
    d[0.25] = None
    for t in range(100):
        d[1] += '1'
        d['2'] += 1
        d[0.25] = None
        time.sleep(.1)
    d[3] = 5
    l.reverse()

if __name__ == '__main__':
    with Manager() as manager:
        d = manager.dict()
        l = manager.list(range(10))

        p = Process(target=f, args=(d, l))
        p.start()
        for i in range(100):
            print("hi")
            time.sleep(0.1)
            print(d)
        
        p.join()

        print(d)
        print(l)