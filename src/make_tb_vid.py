import vid_edit_utils as veu
from pathlib import Path
import os
SCRIPT_PARENT_DIR_PATH = os.path.abspath(os.path.dirname(__file__)) # src
REPO_ROOT_DIR_PATH = os.path.dirname(SCRIPT_PARENT_DIR_PATH)
# print(REPO_ROOT_DIR_PATH)
BIG_DATA_DIR_PATH = os.path.join(os.path.dirname(REPO_ROOT_DIR_PATH), "tik_tb_vid_big_data")
# print(BIG_DATA_DIR_PATH)

BIG_DATA_OG_CLIPS_DIR_PATH = os.path.join(BIG_DATA_DIR_PATH, "og_clips")
BIG_DATA_WORKING_DIR_PATH = os.path.join(BIG_DATA_DIR_PATH, "working")
TEST_OUT_MP4_PATH = os.path.join(BIG_DATA_DIR_PATH, "test_out_vids", "test_out.mp4")
# print(Path(TEST_OUT_MP4_PATH).w)

def get_w_matched_new_vid_dims(vid_dim_tup, vid_path):
    """Assumes vid_dim_tup always taller than vid_path"""
    og_vid_dim_tup = veu.get_vid_dims(vid_path)
    og_vid_dim_aspect_ratio = og_vid_dim_tup[1] / og_vid_dim_tup[0]
    # print(f"{og_vid_dim_aspect_ratio=}")
    new_w = vid_dim_tup[0]
    new_h = new_w * og_vid_dim_aspect_ratio
    # print(f"{og_top_vid_dim_tup}")
    return (new_w, new_h)

def make_tb_vid(vid_dim_tup, top_vid_path, bottom_vid_path, use_audio_from_str = "top", trim_bottom_vid_method_str = "from_start"):
    """ - Zoom top vid in or out to fit vid_dim_tup,
        - Do same for bottom vid with remaining dims?
        - Assume top_vid is already the length you want
          - Use trim_bottom_vid_method_str to choose how bottom vid time is trimmed to match top
            - from_start - Just cut off extra from end
            - from_rand_start - Start from random point in bottom vid and cut off extra
              - Good for 10-hour vids
            - MORE???
    """

    new_top_vid_dim_tup = get_w_matched_new_vid_dims(vid_dim_tup, top_vid_path)
    print(f"{new_top_vid_dim_tup=}")

    scaled_top_vid_path = os.path.join(BIG_DATA_WORKING_DIR_PATH, "scaled_top_vid.mp4")
    print(f"{scaled_top_vid_path=}")
    # veu.scale_vid(new_top_vid_dim_tup, top_vid_path, scaled_top_vid_path) # PUT BACK!!!!!!!!!!!

    # scale_vid() can change h by 1 pixel, get fresh dims to be safe
    scaled_top_vid_dims_tup = veu.get_vid_dims(scaled_top_vid_path)
    print(f"{scaled_top_vid_dims_tup=}")

    # Just in case
    if scaled_top_vid_dims_tup[0] != vid_dim_tup[0]:
        raise Exception(f"ERROR: width should not have changed, {scaled_top_vid_dims_tup=}, {vid_dim_tup=}")

    # get remaining dims to be filled by bottom_vid
    new_bottom_vid_dim_tup = (scaled_top_vid_dims_tup[0], vid_dim_tup[1] - scaled_top_vid_dims_tup[1])
    print(f"{new_bottom_vid_dim_tup=}")

    scaled_bottom_vid_path = os.path.join(BIG_DATA_WORKING_DIR_PATH, "scaled_bottom_vid.mp4")
    print(f"{scaled_bottom_vid_path=}")

    veu.scale_vid(new_bottom_vid_dim_tup, bottom_vid_path, scaled_bottom_vid_path) # PUT BACK!!!!!!!!!!!


print("init")
vid_dim_tup = (1080,1920) # W x H
top_vid_path = "C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\og_clips\\fg_test.mp4"
bottom_vid_path = "C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\og_clips\\mc_test.mp4"

make_tb_vid(vid_dim_tup, top_vid_path, bottom_vid_path, use_audio_from_str = "top")