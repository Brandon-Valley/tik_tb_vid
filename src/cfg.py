from os.path import join
from os.path import abspath
from os.path import dirname

SCRIPT_PARENT_DIR_PATH    = abspath(dirname(__file__)) # src
REPO_ROOT_DIR_PATH        = dirname(SCRIPT_PARENT_DIR_PATH)
# BIG_DATA_DIR_PATH         = join(dirname(REPO_ROOT_DIR_PATH), "tik_tb_vid_big_data")
BIG_DATA_DIR_PATH         = "C:/p/tik_tb_vid_big_data"
BIG_DATA_WORKING_DIR_PATH = join(BIG_DATA_DIR_PATH, "working")

if __name__ == "__main__":
    print("init")
    import batch_make_tb_vids
    batch_make_tb_vids.main()