import vid_edit_utils as veu
from pathlib import Path
import os
SCRIPT_PARENT_DIR_PATH = os.path.abspath(os.path.dirname(__file__)) # src
REPO_ROOT_DIR_PATH = os.path.dirname(SCRIPT_PARENT_DIR_PATH)
# print(REPO_ROOT_DIR_PATH)
BIG_DATA_DIR_PATH = os.path.join(os.path.dirname(REPO_ROOT_DIR_PATH), "tik_tb_vid_big_data")
# print(BIG_DATA_DIR_PATH)

BIG_DATA_OG_CLIPS_DIR_PATH = os.path.join(BIG_DATA_DIR_PATH, "og_clips")
TEST_OUT_MP4_PATH = os.path.join(BIG_DATA_DIR_PATH, "test_out_vids", "test_out.mp4")
# print(Path(TEST_OUT_MP4_PATH).w)

def get_w_matched_new_vid_dims(vid_dim_tup, vid_path):
    """Assumes vid_dim_tup always taller than vid_path"""
    og_vid_dim_tup = veu.get_vid_dims(vid_path)
    og_vid_dim_aspect_ratio = og_vid_dim_tup[1] / og_vid_dim_tup[0]
    print(f"{og_vid_dim_aspect_ratio=}")
    new_w = vid_dim_tup[0]
    new_h = new_w * og_vid_dim_aspect_ratio
    # print(f"{og_top_vid_dim_tup}")
    return (new_w, new_h)

def make_tb_vid(vid_dim_tup, top_vid_path, bottom_vid_path, use_audio_from_str = "top"):
    """ - Zoom top vid in or out to fit vid_dim_tup,
        - Do same for bottom vid with remaining dims?
    """
    og_top_vid_dim_tup = veu.get_vid_dims(top_vid_path)
    print(f"{og_top_vid_dim_tup}")

    new_top_vid_dim_tup = get_w_matched_new_vid_dims(vid_dim_tup, top_vid_path)
    print(f"{new_top_vid_dim_tup=}")

print("init")
vid_dim_tup = (1080,1920) # W x H
top_vid_path = "C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\og_clips\\fg_test.mp4"
bottom_vid_path = "C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\og_clips\\mc_test.mp4"

make_tb_vid(vid_dim_tup, top_vid_path, bottom_vid_path, use_audio_from_str = "top")