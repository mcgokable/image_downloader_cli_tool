from concurrent.futures import ThreadPoolExecutor, as_completed
from random import random
from threading import Lock
from time import sleep


# simple progress indicator callback function
def progress_indicator(future):
    global lock, tasks_total, tasks_completed
    # obtain the lock
    with lock:
        # update the counter
        tasks_completed += 1
        # report progress
        print(
            f"{tasks_completed}/{tasks_total} completed, {tasks_total-tasks_completed} remain."
        )


# mock test that works for moment
def task(name):
    sleep(random())


# create a lock for the counter
lock = Lock()
# total tasks we will execute
tasks_total = 20
# total completed tasks
tasks_completed = 0
# start the thread pool
with ThreadPoolExecutor(2) as executor:
    # send in the tasks
    futures = [executor.submit(task, i) for i in range(20)]
    # register the progress indicator callback
    for future in futures:
        future.add_done_callback(progress_indicator)
    # wait for all tasks to complete
print("Done!")
