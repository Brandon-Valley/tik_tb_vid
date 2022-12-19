import vid_edit_utils as veu
from pathlib import Path
import os
import random
SCRIPT_PARENT_DIR_PATH = os.path.abspath(os.path.dirname(__file__)) # src
REPO_ROOT_DIR_PATH = os.path.dirname(SCRIPT_PARENT_DIR_PATH)
BIG_DATA_DIR_PATH = os.path.join(os.path.dirname(REPO_ROOT_DIR_PATH), "tik_tb_vid_big_data")
BIG_DATA_OG_CLIPS_DIR_PATH = os.path.join(BIG_DATA_DIR_PATH, "og_clips")
BIG_DATA_WORKING_DIR_PATH = os.path.join(BIG_DATA_DIR_PATH, "working")

TEST_OUT_MP4_PATH = os.path.join(BIG_DATA_DIR_PATH, "test_out_vids", "test_out.mp4")

SCALED_TOP_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "scaled_top_vid.mp4")
CUSTOM_EDITED_TOP_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "custom_edited_top_vid.mp4")
CUSTOM_EDITED_BOTTOM_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "custom_edited_bottom_vid.mp4")
SCALED_BOTTOM_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "scaled_bottom_vid_after_custom_edit.mp4")
TIME_TRIMMED_BOTTOM_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "time_trimmed_bottom_vid.mp4")

TEST_FINAL_OUT_STACKED_VID_PATH = os.path.join(BIG_DATA_WORKING_DIR_PATH, "stacked.mp4")


def get_w_matched_new_vid_dims(vid_dim_tup, vid_path):
    """Assumes vid_dim_tup always taller than vid_path"""
    og_vid_dim_tup = veu.get_vid_dims(vid_path)
    og_vid_dim_aspect_ratio = og_vid_dim_tup[1] / og_vid_dim_tup[0]
    # print(f"{og_vid_dim_aspect_ratio=}")
    new_w = vid_dim_tup[0]
    new_h = int(new_w * og_vid_dim_aspect_ratio)
    # print(f"{og_top_vid_dim_tup}")
    return (new_w, new_h)


def time_trim_bottom_vid_to_match_top(top_vid_path, bottom_vid_path, out_vid_path, time_trim_bottom_vid_method_str):
    top_vid_len = veu.get_vid_length(top_vid_path)
    bottom_vid_len = veu.get_vid_length(bottom_vid_path)

    if top_vid_len > bottom_vid_len + 1: # added + 1 for max_start_time just to make sure no fraction breaks anything
        raise Exception("ERROR: Behavior not implemented for top vid being longer than bottom vid, maybe could loop?")

    # Get time_tup of (start_time, end_time) for trimming bottom vid based on time_trim_bottom_vid_method_str
    if time_trim_bottom_vid_method_str == "from_start":
        time_tup = (0, top_vid_len)

    elif time_trim_bottom_vid_method_str == "from_rand_start":
        max_start_time = int(bottom_vid_len - top_vid_len) - 1

        rand_start_time = random.randint(0,max_start_time)
        end_time = rand_start_time + top_vid_len
        time_tup = (rand_start_time, end_time)


    elif time_trim_bottom_vid_method_str == "loop":
        raise Exception("ERROR: Behavior not implemented - loop")
    else:
        raise Exception(f"ERROR: invalid {time_trim_bottom_vid_method_str=}")

    veu.trim_vid(bottom_vid_path, out_vid_path, time_tup)


def _trim_sides_of_vid_to_match_aspect_ratio(vid_dim_tup_to_match_aspect_ratio, in_vid_path, out_vid_path):
    """ Good for trimming sides of MC Parkour vids while keeping center """
    in_vid_dim_tup = veu.get_vid_dims(in_vid_path)
    in_vid_w = in_vid_dim_tup[0]
    in_vid_h = in_vid_dim_tup[1]

    # print(f"{vid_dim_tup_to_match_aspect_ratio}")

    aspect_ratio = vid_dim_tup_to_match_aspect_ratio[0] / vid_dim_tup_to_match_aspect_ratio[1]
    # print(f"{aspect_ratio=}")

    # new_vid_h = in_vid_h
    new_vid_w = in_vid_h * aspect_ratio
    print(f"new vid diiiiiims {new_vid_w} x {in_vid_h}")
    # print(f"new vid diiiiiims {new_vid_w} x {new_vid_h}")

    # At this point, h should be the same, only w has changed (reduced)
    w_diff = in_vid_w - new_vid_w
    num_pixels_to_trim_from_both_sides = int(w_diff / 2)

    veu.crop_vid(w = w_diff,
                 h = in_vid_h,
                 x = num_pixels_to_trim_from_both_sides,
                 y = 0,
                 in_vid_path = in_vid_path, out_vid_path = out_vid_path)

def _trim_sides_of_vid_by_percent(trim_percent, in_vid_path, out_vid_path):
    """ 
        Good for trimming non-important sides of shows like Family Guy 
        - Hacky work-around, proper machine vision to identify characters/important things, signs,
          etc. is the true solution to this.
        - trim_percent =  10, 20, 30, etc.
    """
    in_vid_dim_tup = veu.get_vid_dims(in_vid_path)
    in_vid_w = in_vid_dim_tup[0]
    in_vid_h = in_vid_dim_tup[1]

    num_pixels_wide_to_remove_total = int(in_vid_w / trim_percent)
    # num_pixels_to_trim_total = int(in_vid_w / trim_percent)
    num_pixels_wide_to_keep_total = in_vid_w - num_pixels_wide_to_remove_total
    # print(f"{num_pixels_wide_to_keep_total=}")
    # print(f"{(in_vid_w - num_pixels_wide_to_remove_total)=}")

    # print(f"{num_pixels_to_trim_total=}")
    # print(f"{num_pixels_wide_to_remove_total=}")
    # print(f"{int(in_vid_w / trim_percent)=}")
    # print(f"{in_vid_w=}")
    # print(f"{trim_percent=}")
    # num_pixels_to_trim_from_both_sides = int(int(in_vid_w / trim_percent) / 2)
    num_pixels_to_trim_from_both_sides = int(num_pixels_wide_to_remove_total / 2)
    # print(f"{num_pixels_to_trim_from_both_sides=}")

    veu.crop_vid(w = num_pixels_wide_to_keep_total,
                 h = in_vid_h,
                 x = num_pixels_to_trim_from_both_sides,
                 y = 0,
                 in_vid_path = in_vid_path, out_vid_path = out_vid_path)

def custom_edit_top_vid(in_vid_path, out_vid_path, custom_edit_vid_method_str, trim_sides_percent):
    if custom_edit_vid_method_str == "None":
        raise Exception("ERROR: not implemented yet")
    if custom_edit_vid_method_str == "trim_sides_by_percent":
        _trim_sides_of_vid_by_percent(trim_sides_percent, in_vid_path, out_vid_path)
    else:
        raise Exception(f"ERROR: invalid {custom_edit_vid_method_str=}")

def custom_edit_bottom_vid(vid_dim_tup_to_match_aspect_ratio, in_vid_path, out_vid_path, custom_edit_vid_method_str):
    if custom_edit_vid_method_str == "trim_sides":
        _trim_sides_of_vid_to_match_aspect_ratio(vid_dim_tup_to_match_aspect_ratio, in_vid_path, out_vid_path)
    else:
        raise Exception(f"ERROR: invalid {custom_edit_vid_method_str=}")



def make_tb_vid(vid_dim_tup, out_vid_path, top_vid_path, bottom_vid_path, use_audio_from_str = "top", 
                time_trim_bottom_vid_method_str = "from_rand_start", 
                custom_edit_bottom_vid_method_str = "trim_sides",
                custom_edit_top_vid_method_str = "trim_sides_by_percent",
                trim_top_vid_sides_percent = 10):
    """ - Zoom top vid in or out to fit vid_dim_tup,
        - Do same for bottom vid with remaining dims?
        - Assume top_vid is already the length you want
          - Use time_trim_bottom_vid_method_str to choose how bottom vid time is trimmed to match top
            - from_start - Just cut off extra from end
            - from_rand_start - Start from random point in bottom vid and cut off extra
              - Good for 10-hour vids
            - LOOP???
            - MORE???
    """
    # veu.remove_watermark(top_vid_path, "C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\working\\removed_watermark_test.mp4")

    veu.remove_black_border_from_vid_if_needed(top_vid_path, "C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\working\\black_bars_test.mp4")
    # veu.trim_black_borders(top_vid_path, "C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\working\\black_bars_test.mp4")


    # # Perform custom edit to top vid
    # # - This can be different depending on custom_edit_top_vid_method_str to best match the type of vid on top
    # # - This is done before final scaling (making top vid bigger or smaller) because this edit might not be
    # #   pixel-perfect and the final top scale will stretch the vid a tiny bit if needed to fit pixels
    # # custom_edit_top_vid(top_vid_path, CUSTOM_EDITED_TOP_VID_PATH, custom_edit_top_vid_method_str, trim_top_vid_sides_percent) # PUT BACK !!!!!!!!!
    # # print(f"{veu.get_vid_dims(CUSTOM_EDITED_TOP_VID_PATH)=}")


    # # new_top_vid_dim_tup = get_w_matched_new_vid_dims(vid_dim_tup, top_vid_path)
    # new_top_vid_dim_tup = get_w_matched_new_vid_dims(vid_dim_tup, CUSTOM_EDITED_TOP_VID_PATH)
    # print(f"..........{new_top_vid_dim_tup=}")

    # veu.scale_vid(new_top_vid_dim_tup, top_vid_path, SCALED_TOP_VID_PATH) # PUT BACK!!!!!!!!!!!

    # # scale_vid() can change h by 1 pixel, get fresh dims to be safe
    # scaled_top_vid_dims_tup = veu.get_vid_dims(SCALED_TOP_VID_PATH)
    # print(f"{scaled_top_vid_dims_tup=}")

    # # Just in case
    # if scaled_top_vid_dims_tup[0] != vid_dim_tup[0]:
    #     raise Exception(f"ERROR: width should not have changed, {scaled_top_vid_dims_tup=}, {vid_dim_tup=}")

    # # Trim bottom vid time to match top
    # time_trim_bottom_vid_to_match_top(SCALED_TOP_VID_PATH, bottom_vid_path, TIME_TRIMMED_BOTTOM_VID_PATH, time_trim_bottom_vid_method_str) # PUT BACK !!!!!!!!!

    # # get remaining dims to be filled by bottom_vid
    # new_bottom_vid_dim_tup = (scaled_top_vid_dims_tup[0], vid_dim_tup[1] - scaled_top_vid_dims_tup[1])
    # print(f"{new_bottom_vid_dim_tup=}")

    # # Perform custom edit to bottom vid
    # # - This can be different depending on custom_edit_bottom_vid_method_str to best match the type of vid on bottom
    # # - This is done before final scaling (making bottom vid bigger or smaller) because this edit might not be
    # #   pixel-perfect and the final bottom scale will stretch the vid a tiny bit if needed to fit pixels
    # custom_edit_bottom_vid(new_bottom_vid_dim_tup, TIME_TRIMMED_BOTTOM_VID_PATH, CUSTOM_EDITED_BOTTOM_VID_PATH, custom_edit_bottom_vid_method_str) # PUT BACK !!!!!!!

    # # print(f"{SCALED_BOTTOM_VID_PATH=}")

    # veu.scale_vid(new_bottom_vid_dim_tup, CUSTOM_EDITED_BOTTOM_VID_PATH, SCALED_BOTTOM_VID_PATH) # PUT BACK!!!!!!!!!!!

    # # Make stacked vid
    # veu.stack_vids(SCALED_TOP_VID_PATH, SCALED_BOTTOM_VID_PATH, out_vid_path) # PUT BACK!!!!!!!!!


if __name__ == "__main__":
    print("init")
    import batch_make_tb_vids
    batch_make_tb_vids.main()




    # vid_dim_tup = (1080,1920) # W x H
    # out_vid_path = TEST_FINAL_OUT_STACKED_VID_PATH
    # top_vid_path = "C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\og_clips\\fg_test_short.mp4"
    # bottom_vid_path = "C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\og_clips\\mc_test.mp4"

    # make_tb_vid(vid_dim_tup, out_vid_path, top_vid_path, bottom_vid_path, use_audio_from_str = "top")