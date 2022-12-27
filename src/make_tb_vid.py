import vid_edit_utils as veu
from pathlib import Path
import os
import random
import cfg

# Working top vid paths
TOP_VID_PATH__BLACK_BARS_REMOVED = os.path.join(cfg.BIG_DATA_WORKING_DIR_PATH, "top__black_bars_removed.mp4")
TOP__VID_PATH__SCALED            = os.path.join(cfg.BIG_DATA_WORKING_DIR_PATH, "top__scaled.mp4")
TOP_VID_PATH__CUSTOM_EDIT        = os.path.join(cfg.BIG_DATA_WORKING_DIR_PATH, "top__custom_edited.mp4")

# Working bottom vid paths
BOTTOM_VID_PATH__CUSTOM_EDIT  = os.path.join(cfg.BIG_DATA_WORKING_DIR_PATH, "bottom__custom_edited.mp4")
BOTTOM_VID_PATH__SCALED       = os.path.join(cfg.BIG_DATA_WORKING_DIR_PATH, "bottom__scaled.mp4")
BOTTOM_VID_PATH__TIME_TRIMMED = os.path.join(cfg.BIG_DATA_WORKING_DIR_PATH, "bottom__time_trimmed.mp4")

####################################################################################################
# Top Vid Exclusive
####################################################################################################

def _scale_vid_to_new_w_matched_vid_dims(final_vid_dim_tup, in_vid_path, out_vid_path):
    """Assumes final_vid_dim_tup always taller than vid_path"""
    print(f"{in_vid_path=}")
    print(f"{out_vid_path=}")

    og_vid_dim_tup = veu.get_vid_dims(in_vid_path)
    og_vid_dim_aspect_ratio = og_vid_dim_tup[1] / og_vid_dim_tup[0]
    # print(f"{og_vid_dim_aspect_ratio=}")
    new_w = final_vid_dim_tup[0]
    new_h = int(new_w * og_vid_dim_aspect_ratio)
    # print(f"{og_top_vid_dim_tup}")
    new_top_vid_dim_tup = (new_w, new_h)

    scaled_vid_path = veu.scale_vid(new_top_vid_dim_tup, in_vid_path, out_vid_path)

    return scaled_vid_path



def _crop_sides_of_vid_to_match_aspect_ratio_from_percent_of_final_dims(custom_edit_percent, final_vid_dim_tup, in_vid_path, out_vid_path):
    print(f"{custom_edit_percent=}")
    print(f"{final_vid_dim_tup=}")
    print(f"{in_vid_path=}")
    print(f"{out_vid_path=}")

    final_vid_w = final_vid_dim_tup[0]
    final_vid_h = final_vid_dim_tup[1]

    # LATER do you really need to trim sides to match aspect ratio THEN scale separately in 2 diff steps?
    # LATER have vinal top vid dims here vv, could you save time by doing both in 1 step?
    final_top_vid_h = int(final_vid_h * (custom_edit_percent / 100))
    final_top_vid_dim_tup = (final_vid_w, final_top_vid_h)

    # top_vid_aspect_ratio = final_vid_w / final_top_vid_h

    cropped_or_uncropped_vid_path = veu.crop_sides_of_vid_to_match_aspect_ratio(final_top_vid_dim_tup, in_vid_path, out_vid_path)

    return cropped_or_uncropped_vid_path


def _custom_edit_top_vid(in_vid_path, out_vid_path, custom_edit_vid_method_str, custom_edit_percent, final_vid_dim_tup):

    if custom_edit_vid_method_str == None:
        raise Exception("ERROR: not implemented yet")

    # Good for cropping non-important sides of shows like Family Guy
    #   - Hacky work-around, proper machine vision to identify characters/important things, signs,
    #     etc. is the true solution to this.
    #   - trim_percent =  10, 20, 30, etc.
    elif custom_edit_vid_method_str == "crop_sides_by_percent":
        cropped_or_uncropped_vid_path = veu.crop_sides_of_vid_by_percent(custom_edit_percent, in_vid_path, out_vid_path)
        print(f"{cropped_or_uncropped_vid_path=}")
        return cropped_or_uncropped_vid_path

    # Allows you to say "no matter what dims the given top vid is, trim ONLY the sides in order to match the aspect 
    # ratio (will be scaled later) needed such that the top vid will always occupy the top 40% of the final vertical vid."
    # - Good for setting an "optimal top vid percent"
    # - Why not use crop_sides_by_percent?
    #   - crop_sides_by_percent worked too well, turns out the top vid can be made so large (while still understanding
    #     whats going on) that you can hardly see the bottom vid.
    #   - Also, crop_sides_by_percent will result in a batch of final vids that have different ratios of 
    #     top-to-bottom-vids, might be nice for all final vids to have same ratio?
    elif custom_edit_vid_method_str == "crop_sides_of_vid_to_match_aspect_ratio_from_percent_of_final_dims":
        cropped_or_uncropped_vid_path = _crop_sides_of_vid_to_match_aspect_ratio_from_percent_of_final_dims(custom_edit_percent, final_vid_dim_tup, in_vid_path, out_vid_path)
        print(f"{cropped_or_uncropped_vid_path=}")
        return cropped_or_uncropped_vid_path
    else:
        raise Exception(f"ERROR: invalid {custom_edit_vid_method_str=}")


def _get_and_check__final_top_vid__dims_tup__and__len(final_vid_dim_tup, final_top_vid_path):
    """
        The returns of this func. should be the only data from top vid needed to create final bottom vid
          - scale_vid() can change h by 1 pixel, get fresh dims to be safe
    """
    # Get/check top vid dims
    final_top_vid_dims_tup = veu.get_vid_dims(final_top_vid_path)
    print(f"{final_top_vid_dims_tup=}")

    # Just in case
    if final_top_vid_dims_tup[0] != final_vid_dim_tup[0]:
        raise Exception(f"ERROR: width should not have changed, {final_top_vid_dims_tup=}, {final_vid_dim_tup=}")

    # Get top vid length
    final_top_vid_len = veu.get_vid_length(final_top_vid_path)

    return final_top_vid_dims_tup, final_top_vid_len


####################################################################################################
# Bottom Vid Exclusive
####################################################################################################

def _time_trim_bottom_vid_to_match_top(final_top_vid_len, bottom_vid_path, out_vid_path, time_trim_bottom_vid_method_str):
    bottom_vid_len = veu.get_vid_length(bottom_vid_path)

    if final_top_vid_len > bottom_vid_len + 1: # added + 1 for max_start_time just to make sure no fraction breaks anything
        raise Exception("ERROR: Behavior not implemented for top vid being longer than bottom vid, maybe could loop?")

    # Get time_tup of (start_time, end_time) for trimming bottom vid based on time_trim_bottom_vid_method_str
    if time_trim_bottom_vid_method_str == "from_start":
        time_tup = (0, final_top_vid_len)

    elif time_trim_bottom_vid_method_str == "from_rand_start":
        max_start_time = int(bottom_vid_len - final_top_vid_len) - 1

        rand_start_time = random.randint(0,max_start_time)
        end_time = rand_start_time + final_top_vid_len
        time_tup = (rand_start_time, end_time)

    elif time_trim_bottom_vid_method_str == "loop":
        raise Exception("ERROR: Behavior not implemented - loop")
    else:
        raise Exception(f"ERROR: invalid {time_trim_bottom_vid_method_str=}")

    trimmed_vid_path = veu.trim_vid(bottom_vid_path, out_vid_path, time_tup)
    return trimmed_vid_path


def _custom_edit_bottom_vid(vid_dim_tup_to_match_aspect_ratio, in_vid_path, out_vid_path, custom_edit_vid_method_str):
    if custom_edit_vid_method_str == "crop_sides":
        side_cropped_vid_path = veu.crop_sides_of_vid_to_match_aspect_ratio(vid_dim_tup_to_match_aspect_ratio, in_vid_path, out_vid_path)
        return side_cropped_vid_path
    else:
        raise Exception(f"ERROR: invalid {custom_edit_vid_method_str=}")

########################################################################################################################
# Main
########################################################################################################################
def make_tb_vid(final_vid_dim_tup, out_vid_path, top_vid_path, bottom_vid_path, use_audio_from_str = "top",
                time_trim_bottom_vid_method_str = "from_rand_start",
                custom_edit_bottom_vid_method_str = "crop_sides",
                custom_edit_top_vid_method_str = "crop_sides_by_percent",
                top_vid_custom_edit_percent = 10):
    """ - Zoom top vid in or out to fit final_vid_dim_tup,
        - Do same for bottom vid with remaining dims?
        - Assume top_vid is already the length you want
          - Use time_trim_bottom_vid_method_str to choose how bottom vid time is trimmed to match top
            - from_start - Just cut off extra from end
            - from_rand_start - Start from random point in bottom vid and cut off extra
              - Good for 10-hour vids
            - LOOP???
            - MORE???
    """
    ##################
    # Process top vid
    ##################

    cur_top_vid_path = top_vid_path

    # Will not create new vid if no black borders need to be removed
    cur_top_vid_path = veu.crop_black_border_from_vid_if_needed(cur_top_vid_path, TOP_VID_PATH__BLACK_BARS_REMOVED) # PUT BACK!!!!!!!!!!!!!!

    # Perform custom edit to top vid
    # - This can be different depending on custom_edit_top_vid_method_str to best match the type of vid on top
    # - This is done before final scaling (making top vid bigger or smaller) because this edit might not be
    #   pixel-perfect and the final top scale will stretch the vid a tiny bit if needed to fit pixels
    cur_top_vid_path = _custom_edit_top_vid(cur_top_vid_path, TOP_VID_PATH__CUSTOM_EDIT, custom_edit_top_vid_method_str, top_vid_custom_edit_percent, final_vid_dim_tup) # PUT BACK !!!!!!!!!
    # exit()

    cur_top_vid_path = _scale_vid_to_new_w_matched_vid_dims(final_vid_dim_tup, cur_top_vid_path, TOP__VID_PATH__SCALED) # PUT BACK!!!!!!!!!!!

    # The returns of this func. should be the only data from top vid needed to create final bottom vid
    # cur_top_vid_path = "C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\working\\top__scaled.mp4" # TMP !!!!!!!!!!!!!!!!!!!
    final_top_vid_dims_tup, final_top_vid_len = _get_and_check__final_top_vid__dims_tup__and__len(final_vid_dim_tup, cur_top_vid_path)
    print(f"{final_top_vid_dims_tup=}")
    print(f"{final_top_vid_len=}")

    #####################
    # Process bottom vid
    #####################
    cur_bottom_vid_path = bottom_vid_path

    # Trim bottom vid time to match top
    cur_bottom_vid_path = _time_trim_bottom_vid_to_match_top(final_top_vid_len, cur_bottom_vid_path, BOTTOM_VID_PATH__TIME_TRIMMED, time_trim_bottom_vid_method_str) # PUT BACK !!!!!!!!!

    # get remaining dims to be filled by bottom_vid
    new_bottom_vid_dim_tup = (final_top_vid_dims_tup[0], final_vid_dim_tup[1] - final_top_vid_dims_tup[1])
    print(f"{new_bottom_vid_dim_tup=}")

    # Perform custom edit to bottom vid
    # - This can be different depending on custom_edit_bottom_vid_method_str to best match the type of vid on bottom
    # - This is done before final scaling (making bottom vid bigger or smaller) because this edit might not be
    #   pixel-perfect and the final bottom scale will stretch the vid a tiny bit if needed to fit pixels
    # cur_bottom_vid_path = BOTTOM_VID_PATH__TIME_TRIMMED # TMP !!!!!!!!!!!!!!!!!!!!
    cur_bottom_vid_path = _custom_edit_bottom_vid(new_bottom_vid_dim_tup, cur_bottom_vid_path, BOTTOM_VID_PATH__CUSTOM_EDIT, custom_edit_bottom_vid_method_str) # PUT BACK !!!!!!!

    cur_bottom_vid_path = veu.scale_vid(new_bottom_vid_dim_tup, cur_bottom_vid_path, BOTTOM_VID_PATH__SCALED) # PUT BACK!!!!!!!!!!!

    #########################################################
    # Combine top and bottom vids to create final output vid
    #########################################################
    cur_out_vid_path = out_vid_path

    cur_out_vid_path = veu.stack_vids(cur_top_vid_path, cur_bottom_vid_path, cur_out_vid_path) # PUT BACK!!!!!!!!!

    print(f"Finished Making Top-Bottom Video: {out_vid_path}")


if __name__ == "__main__":
    print("init")
    import batch_make_tb_vids
    batch_make_tb_vids.main()