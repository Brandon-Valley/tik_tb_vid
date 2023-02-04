import statistics
import time
import os
from os.path import join
from pathlib import Path
from pprint import pprint


if __name__ == "__main__":
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).parent.parent))

from YT_PL_DL_Data import YT_PL_DL_Data
from get_real_episode_sub_data_from_auto_sub import get_real_episode_sub_data_from_auto_sub
from trim_and_re_time_real_sub_file_from_auto_subs import trim_and_re_time_real_sub_file_from_auto_subs
from Series_Sub_Map import Series_Sub_map

from sms.file_system_utils import file_system_utils as fsu
from sms.logger import json_logger
import vid_edit_utils as veu
import subtitle_utils
import cfg
import sub_diff_ratio_tools

# SCRIPT_PARENT_DIR_PATH = os.path.abspath(os.path.dirname(__file__))
POST_RUN_REPORT_JSON_PATH = join(cfg.INIT_MKVS_WORKING_DIR_PATH, "post_run_report.json")

def write_sub_diff_ratio_sub_path_l_d_data():
    print(POST_RUN_REPORT_JSON_PATH)


if __name__ == "__main__":
    import os.path as path
    print("Running " , path.abspath(__file__) , '...')
    write_sub_diff_ratio_sub_path_l_d_data()
    print("End of Main") 
