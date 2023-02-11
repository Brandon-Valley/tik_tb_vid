from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait

class Thread_Manager:
    def __enter__(self):
        return self

    def __init__(self, enable_threading, num_cores, verbose = True):
        self.verbose = verbose
        self.enable_threading = enable_threading

        if not self.enable_threading:
            return

        # Start the thread pool
        self.executor = ThreadPoolExecutor(num_cores)
        self.futures = []

    def thread_func_if_enabled(self, func, *args):
        if self.enable_threading:
            # Submit tasks and collect futures
            self.futures.append(self.executor.submit(func, *args))
        else:
            # Run function with *args normally if threading is disabled
            func(*args)

    # https://docs.python.org/release/2.5.2/lib/typecontextmanager.html
    def __exit__(self, type, value, traceback):
        ''' Upon exiting with-block, if threading is enabled, wait for all threads to finish, then raise any exception thrown by a thread if needed. '''
        if not self.enable_threading:
            return

        # Wait for all threads to complete
        wait(self.futures)

        if self.verbose:
            print("All threads done, checking if any thread raised an exception...")
        print(f"{len(self.futures)=}")

        for fut in self.futures:
            _ = fut.result()

        if self.verbose:
            print("Confirmed no exceptions were raised by any thread!")


# Test
if __name__ == "__main__":
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
    # TEST #1 - Thread Jobs
    ################################################################################################
    print("TEST #1 - Thread Jobs\n")
    with Thread_Manager(THREADING_ENABLED, NUM_CORES) as tm:
        for str1, str2 in STR_PAIRS_TO_PRINT_LIST:
            tm.thread_func_if_enabled(print_2_strings, str1, str2)

    ################################################################################################
    # TEST #2 - Threading Disabled
    ################################################################################################
    print("\n\nTEST #2 - Threading Disabled\n")
    with Thread_Manager(False, NUM_CORES) as tm:
        for str1, str2 in STR_PAIRS_TO_PRINT_LIST:
            tm.thread_func_if_enabled(print_2_strings, str1, str2)

    ################################################################################################
    # TEST #3 - Raise Exception
    ################################################################################################
    print("\n\nTEST #3 - Raise Exception\n")
    str_list_w_bad_arg = [("good_str_arg", 1.23)] + STR_PAIRS_TO_PRINT_LIST
    with Thread_Manager(THREADING_ENABLED, NUM_CORES) as tm:
        for str1, str2 in str_list_w_bad_arg:
            tm.thread_func_if_enabled(print_2_strings, str1, str2)

    print("\nEnd of Main")
