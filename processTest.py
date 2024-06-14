import multiprocessing
import time

def update_shared_variable(shared_value):
    with shared_value.get_lock():  # Ensure atomic updates
        shared_value.value += 1
        print(f"Child Process updated value to: {shared_value.value}")

if __name__ == "__main__":
    # Create a shared integer variable initialized to 0
    shared_value = multiprocessing.Value('i', 0)

    # Create and start a process to update the shared variable
    process = multiprocessing.Process(target=update_shared_variable, args=(shared_value,))
    process.start()
    process.join()

    # Print the updated value in the main process
    print(f"Main Process sees updated value: {shared_value.value}")