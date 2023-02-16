from os.path import join
from os.path import abspath
from os.path import dirname

SCRIPT_PARENT_DIR_PATH    = abspath(dirname(__file__)) # src
REPO_ROOT_DIR_PATH        = dirname(SCRIPT_PARENT_DIR_PATH)
# BIG_DATA_DIR_PATH         = join(dirname(REPO_ROOT_DIR_PATH), "tik_tb_vid_big_data")
BIG_DATA_DIR_PATH         = "C:/p/tik_tb_vid_big_data"
BIG_DATA_WORKING_DIR_PATH = join(BIG_DATA_DIR_PATH, "ignore", "working")

INIT_MKVS_WORKING_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS"

FINAL_MP4_SRT_DIRS_DIR_PATH = join(INIT_MKVS_WORKING_DIR_PATH, "o_mp4_srt_dirs")
FINAL_MP4_SRT_DIRS__W_SUBS__DIR_PATH  = join(FINAL_MP4_SRT_DIRS_DIR_PATH, "w_subs")
FINAL_MP4_SRT_DIRS__NO_SUBS__DIR_PATH = join(FINAL_MP4_SRT_DIRS_DIR_PATH, "no_subs")

PROCESS_MATCHED_VID_SUB_DIRS_LOGS_DIR_PATH = join(INIT_MKVS_WORKING_DIR_PATH, "process_matched_vid_sub_dirs_logs")

BATCH_TB_VIDS_OUT_DIR_PATH              = join(INIT_MKVS_WORKING_DIR_PATH, "ignore", "batch_tb_vids_out")
BATCH_TB_VIDS_POST_PROCESS_OUT_DIR_PATH = join(INIT_MKVS_WORKING_DIR_PATH, "ignore", "post_batch_out")


TOP_VID_HEIGHT_SEP_STR = "__tvh_"
NUM_CORES = 4 # personal laptop
# NUM_CORES = 1 # personal laptop

RUN_LOG_JSON_PATH = join(INIT_MKVS_WORKING_DIR_PATH, "run_log_l.json")



if __name__ == "__main__":
    print("init")
    # import batch_make_tb_vids
    # batch_make_tb_vids.main()
    # from e
    from eval_tb_vids import make_tb_vids_report
    make_tb_vids_report._tmp_add_len_to_vid_titles("C:/p/tik_tb_vid_big_data/ignore/final_output")