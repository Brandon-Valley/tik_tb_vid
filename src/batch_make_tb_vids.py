import vid_edit_utils as veu
from pathlib import Path
import os
import random

from make_tb_vid import make_tb_vid

from sms.file_system_utils import file_system_utils as fsu

TIK_BEST_VID_DIM_TUP = (1080,1920) # W x H

SCRIPT_PARENT_DIR_PATH = os.path.abspath(os.path.dirname(__file__)) # src
REPO_ROOT_DIR_PATH = os.path.dirname(SCRIPT_PARENT_DIR_PATH)
PERSONAL_PROJECTS_DIR_PATH = os.path.dirname(REPO_ROOT_DIR_PATH)
PLAYLIST_OG_VIDS_DIR_PATH = os.path.join(PERSONAL_PROJECTS_DIR_PATH, "DELETE_THIS__VIDS",  "fg_pl_tbs")
TEST_OUT_DIR_PATH = os.path.join(PERSONAL_PROJECTS_DIR_PATH, "DELETE_THIS__VIDS",  "fg_pl_tbs__test_output")

BIG_DATA_DIR_PATH = os.path.join(os.path.dirname(REPO_ROOT_DIR_PATH), "tik_tb_vid_big_data")
BIG_DATA_OG_CLIPS_DIR_PATH = os.path.join(BIG_DATA_DIR_PATH, "og_clips")
MC_PARK_VID_PATH = os.path.join(BIG_DATA_OG_CLIPS_DIR_PATH, "mc_test.mp4")

# BIG_DATA_OG_CLIPS_DIR_PATH = os.path.join(BIG_DATA_DIR_PATH, "og_clips")
BIG_DATA_WORKING_DIR_PATH = os.path.join(BIG_DATA_DIR_PATH, "working")

TEST_OUT_MP4_PATH = os.path.join(BIG_DATA_DIR_PATH, "test_out_vids", "test_out.mp4")

SCALED_TOP_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "scaled_top_vid.mp4")
CUSTOM_EDITED_TOP_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "custom_edited_top_vid.mp4")
CUSTOM_EDITED_BOTTOM_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "custom_edited_bottom_vid.mp4")
SCALED_BOTTOM_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "scaled_bottom_vid_after_custom_edit.mp4")
TIME_TRIMMED_BOTTOM_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "time_trimmed_bottom_vid.mp4")
STACKED_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "stacked.mp4")


def make_fg_mcpark_trim_sides_by_percent_tb_vid(trim_sides_by_percent, og_vid_path, vid_edits_dir_path):

    og_vid_file_name = fsu.get_basename_from_path(og_vid_path, include_ext = False)

    make_tb_vid(vid_dim_tup = TIK_BEST_VID_DIM_TUP,
                out_vid_path = os.path.join(vid_edits_dir_path, og_vid_file_name + f"_tsbp_{trim_sides_by_percent}.mp4"),
                top_vid_path = og_vid_path,
                bottom_vid_path = MC_PARK_VID_PATH,
                use_audio_from_str = "top",
                time_trim_bottom_vid_method_str = "from_rand_start", 
                custom_edit_bottom_vid_method_str = "trim_sides",
                custom_edit_top_vid_method_str = "trim_sides_by_percent",
                trim_top_vid_sides_percent = trim_sides_by_percent)

def batch_make_tb_vids(og_vids_dir_path, out_dir_path):

    og_vid_path_l = fsu.get_dir_content_l(og_vids_dir_path, object_type = 'file', content_type = 'abs_path')
    print(og_vid_path_l)

    for og_vid_path in og_vid_path_l:
        og_vid_file_name = fsu.get_basename_from_path(og_vid_path, include_ext = False)
        vid_len = int(veu.get_vid_length(og_vid_path))
        vid_edits_dir_path = os.path.join(out_dir_path, f"vl_{vid_len}__" + og_vid_file_name)

        fsu.delete_if_exists(vid_edits_dir_path)
        fsu.make_dir_if_not_exist(vid_edits_dir_path)

        # make_fg_mcpark_trim_sides_by_percent_tb_vid(5, og_vid_path, vid_edits_dir_path)
        # make_fg_mcpark_trim_sides_by_percent_tb_vid(10, og_vid_path, vid_edits_dir_path)
        # make_fg_mcpark_trim_sides_by_percent_tb_vid(15, og_vid_path, vid_edits_dir_path)
        # make_fg_mcpark_trim_sides_by_percent_tb_vid(20, og_vid_path, vid_edits_dir_path)
        # make_fg_mcpark_trim_sides_by_percent_tb_vid(25, og_vid_path, vid_edits_dir_path)
        make_fg_mcpark_trim_sides_by_percent_tb_vid(30, og_vid_path, vid_edits_dir_path)

def main():
    batch_make_tb_vids(PLAYLIST_OG_VIDS_DIR_PATH, TEST_OUT_DIR_PATH)

if __name__ == "__main__":
    main()