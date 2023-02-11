# JUST USE THREAD_TOOLS

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait

import os.path as path
print("Running " , path.abspath(__file__) , '...')

################################################################################################
# TEST SET-UP
################################################################################################
NUM_CORES = 4 # Personal Laptop
THREADING_ENABLED = True

def print_2_strings(str1, str2):
    if type(str1) != str or type(str2) != str:
        raise TypeError(f"Args must be strings, got: {type(str1)=}, {type(str2)=}")
    print(f"    In print_2_strings() - {str1=}, {str2=}")

STR_PAIRS_TO_PRINT_LIST = [("Hi", "There"), ("Foo", "Bar"), ("Brown", "Fox")]

################################################################################################
# TEST
################################################################################################

# Start the thread pool
with ThreadPoolExecutor(NUM_CORES) as executor:
    futures = []
    for str1, str2 in STR_PAIRS_TO_PRINT_LIST:
        if THREADING_ENABLED:

            # Submit tasks and collect futures
            futures = [executor.submit(print_2_strings, str1, str2)]
        else:
            print_2_strings(str1, str2)

    if THREADING_ENABLED:
        # Wait for tasks to complete
        wait(futures)
        print('All tasks are done, checking for any raised exceptions...')
        for fut in futures:
            _ = fut.result()
        print("Confirmed no exceptions were raised by any thread.")
