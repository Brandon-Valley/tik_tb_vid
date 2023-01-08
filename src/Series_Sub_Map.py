from sms.file_system_utils import file_system_utils as fsu

class Series_Sub_map():
    def __init__(self):
        print("in init")
        pass



if __name__ == "__main__":
    import os.path as path
    print("Running ",  path.abspath(__file__),  '...')
    ssm = Series_Sub_map()
    print("End of Main")