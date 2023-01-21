# https://superfastpython.com/threadpoolexecutor-wait-all-tasks/

# SuperFastPython.com
# example of waiting for tasks to complete
from time import sleep
from random import random
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
 
# custom task that will sleep for a variable amount of time
def task(name):
    # sleep for less than a second
    sleep(random())
    print(f'Done: {name}')
 
# start the thread pool
with ThreadPoolExecutor(2) as executor:
    futures = []

    for i in range(10):
        
        # submit tasks and collect futures
        futures = [executor.submit(task, i)]

    # wait for all tasks to complete
    print('Waiting for tasks to complete...')
    wait(futures)
    print('All tasks are done!')