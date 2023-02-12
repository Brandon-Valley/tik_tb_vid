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
from main_run_logging import    get_clip_process_time, \
                                downloaded_yt_clip_has_no_subs__make_no_sub_mkv__and_get_log_d, \
                                no_episode_sub_fuzzy_match_found__make_no_sub_mkv__and_get_log_d, \
                                fuzz_ratio_0__get_log_d, \
                                normal_successful_clip_w_subs_created__get_log_d, \
                                write_final_stats
from Series_Sub_Map import Series_Sub_map

from sms.file_system_utils import file_system_utils as fsu
from sms.logger import json_logger
import vid_edit_utils as veu
import subtitle_utils
import cfg
import sub_diff_ratio_tools
import real_sub_dialog_match_tools


