import vid_edit_utils as veu
from pathlib import Path
import os
import random

from sms.file_system_utils import file_system_utils as fsu

SCRIPT_PARENT_DIR_PATH = os.path.abspath(os.path.dirname(__file__)) # src
REPO_ROOT_DIR_PATH = os.path.dirname(SCRIPT_PARENT_DIR_PATH)
PERSONAL_PROJECTS_DIR_PATH = os.path.dirname(REPO_ROOT_DIR_PATH)
PLAYLIST_OG_VIDS_DIR_PATH = os.path.join(PERSONAL_PROJECTS_DIR_PATH, "DELETE_THIS__VIDS",  "fg_pl_tbs")
TEST_OUT_DIR_PATH = os.path.join(PERSONAL_PROJECTS_DIR_PATH, "DELETE_THIS__VIDS",  "fg_pl_tbs__test_output")



# BIG_DATA_DIR_PATH = os.path.join(os.path.dirname(REPO_ROOT_DIR_PATH), "tik_tb_vid_big_data")
# BIG_DATA_OG_CLIPS_DIR_PATH = os.path.join(BIG_DATA_DIR_PATH, "og_clips")
# BIG_DATA_WORKING_DIR_PATH = os.path.join(BIG_DATA_DIR_PATH, "working")

# TEST_OUT_MP4_PATH = os.path.join(BIG_DATA_DIR_PATH, "test_out_vids", "test_out.mp4")

# SCALED_TOP_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "scaled_top_vid.mp4")
# CUSTOM_EDITED_TOP_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "custom_edited_top_vid.mp4")
# CUSTOM_EDITED_BOTTOM_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "custom_edited_bottom_vid.mp4")
# SCALED_BOTTOM_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "scaled_bottom_vid_after_custom_edit.mp4")
# TIME_TRIMMED_BOTTOM_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "time_trimmed_bottom_vid.mp4")
# STACKED_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "stacked.mp4")

def batch_make_tb_vids(og_vids_dir_path, out_dir_path):
    print(og_vids_dir_path)



if __name__ == "__main__":
    batch_make_tb_vids(PLAYLIST_OG_VIDS_DIR_PATH, TEST_OUT_DIR_PATH)