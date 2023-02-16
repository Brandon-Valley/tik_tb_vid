
from pprint import pprint
import random
import vid_edit_utils as veu
from pathlib import Path
import os
from os.path import join
import random

from make_tb_vid import make_tb_vid
from vid_edit_utils import Impossible_Dims_Exception

import cfg

from Matched_Vid_Sub_Dir import Matched_Vid_Sub_Dir
from Matched_Vid_Sub_Dir import get_matched_vid_sub_dir_l


from sms.file_system_utils import file_system_utils as fsu
from sms.thread_tools.Simple_Thread_Manager import Simple_Thread_Manager


THREADING_ENABLED = False


def _copy_all_no_subs_vids_to_dir(in_no_subs_dir_path, out_dir_path):
    # no_subs_vid_path_l = fsu.get_dir_content_l(in_no_subs_dir_path)
    print(f"Post-Batch - Copying all no-subs vids from {in_no_subs_dir_path=} to {out_dir_path=}...")
    fsu.copy_dir_contents_to_dest(in_no_subs_dir_path, out_dir_path)
    # fsu.copy_objects_to_dest(in_no_subs_dir_path, out_dir_path)


def _burn_subs_into_all_w_subs_vids__and__write_to_out_dir(in_w_subs_dir_path, out_burned_subs_dir_path):
    def _get_out_burned_subs_vid_path(in_vid_path):
        burned_subs_vid_name = f"bs_{Path(in_vid_path).name}"
        return join(out_burned_subs_dir_path, burned_subs_vid_name)

    def _get_top_vid_height__from__vid_path(in_vid_path):
        return int(str(Path(in_vid_path).stem).split(cfg.TOP_VID_HEIGHT_SEP_STR)[1].split("_")[0])

    def _burn_subs_into_vid_w_height(in_vid_path, in_sub_path, out_vid_path, top_vid_height):
        print(f"??? - {in_vid_path=}")
        print(f"??? - {in_sub_path=}")
        print(f"??? - {out_vid_path=}")
        print(f"??? - {top_vid_height=}")
        print("???")
    
    matched_vid_sub_dir_l = get_matched_vid_sub_dir_l(in_w_subs_dir_path)

    with Simple_Thread_Manager(THREADING_ENABLED, cfg.NUM_CORES) as stm:
        for mvsd in matched_vid_sub_dir_l:
            out_burned_subs_vid_path = _get_out_burned_subs_vid_path(mvsd.vid_path)
            top_vid_height = _get_top_vid_height__from__vid_path(mvsd.vid_path)

            stm.thread_func_if_enabled(_burn_subs_into_vid_w_height, 
                                       mvsd.vid_path,
                                       mvsd.sub_path,
                                       out_burned_subs_vid_path,
                                       top_vid_height)


def process_batch_tb_vids_output(in_dir_path, out_dir_path, aggressive_housekeeping = False):
    in_w_subs_dir_path       = join(in_dir_path , "w_subs")
    in_no_subs_dir_path      = join(in_dir_path , "no_subs")
    out_burned_subs_dir_path = join(out_dir_path, "burned_subs")
    out_no_subs_dir_path     = join(out_dir_path, "no_subs")

    _copy_all_no_subs_vids_to_dir(in_no_subs_dir_path, out_no_subs_dir_path)

    _burn_subs_into_all_w_subs_vids__and__write_to_out_dir(in_w_subs_dir_path, out_burned_subs_dir_path)



    # LATER copy to archive on external HD?


    if aggressive_housekeeping:
        fsu.delete_if_exists(in_dir_path)


    





if __name__ == "__main__":
    import os.path as path
    print("Running " , path.abspath(__file__) , '...')
    # process_batch_tb_vids_output(cfg.BATCH_TB_VIDS_OUT_DIR_PATH, cfg.BATCH_TB_VIDS_POST_PROCESS_OUT_DIR_PATH)
    process_batch_tb_vids_output("C:/p/tik_tb_vid_big_data/ignore/final_output", cfg.BATCH_TB_VIDS_POST_PROCESS_OUT_DIR_PATH)
    print("End of Main") 