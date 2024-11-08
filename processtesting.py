# https://stackoverflow.com/questions/19233246/python-update-local-variable-in-a-parallel-process-from-parent-program
import time


def loop(i):
    while i.value <= 510:
        print(i.value)
        i.value += 1
        time.sleep(1)

if __name__ == "__main__":
    # NOTE: Value and Array are options but it looks like Manager allows us to use python types and 
    #       alter them as such so to use a dict attribute Manager might be the move
    from multiprocessing import Process, Value

    i = Value("i", 1)  # "i" for integer, initial value 1
    p = Process(target=loop, args=(i,))
    p.start()
    for base in range(100, 600, 100):
        time.sleep(2)
        print(f'base: {base}')
        i.value = base