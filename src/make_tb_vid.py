import vid_edit_utils

import os
SCRIPT_PARENT_DIR_PATH = os.path.abspath(os.path.dirname(__file__)) # src
REPO_ROOT_DIR_PATH = os.path.dirname(SCRIPT_PARENT_DIR_PATH)
# print(REPO_ROOT_DIR_PATH)
BIG_DATA_DIR_PATH = os.path.join(os.path.dirname(REPO_ROOT_DIR_PATH), "tik_tb_vid_big_data")
print(BIG_DATA_DIR_PATH)

def make_tb_vid(vid_dim_tup, top_vid_path, bottom_vid_path, use_audio_from_str = "top"):
    """ - Zoom top vid in or out to fit vid_dim_tup,
        - Do same for bottom vid with remaining dims?
    """
    import ffmpeg

    def scale_video(input_file, output_file, width, height):
        # Load the input video
        stream = ffmpeg.input(input_file)

        # Scale the video to the desired dimensions
        stream = stream.filter('scale', width, height)

        # Save the scaled video to the output file
        ffmpeg.output(stream, output_file).run()

    # Example usage:
    # scale_video('input.mp4', 'output.mp4', 1280, 720)
    scale_video(top_vid_path, 'output.mp4', 1280, 720)



print("init")
vid_dim_tup = (1080,1920) # W x H

# make_tb_vid()