

import moviepy.editor as mp

from pprint import pprint
from moviepy.tools import subprocess_call
from moviepy.config import get_setting
import os
import cv2
import subprocess
from pathlib import Path
import ffmpeg
import pvleopard
from sms.file_system_utils import file_system_utils as fsu
from moviepy.editor import VideoFileClip

from PIL import Image
from PIL import ImageDraw

import PIL.ImageFont
import PIL.ImageOps

SCRIPT_PARENT_DIR_PATH = os.path.abspath(os.path.dirname(__file__)) # src
TEMP_FRAME_IMGS_DIR_PATH = os.path.join(SCRIPT_PARENT_DIR_PATH, "ignore__temp_frame_imgs")
START_FRAME_IMG_PATH = os.path.join(TEMP_FRAME_IMGS_DIR_PATH, "start_grey_frame_img.jpg")
END_FRAME_IMG_PATH = os.path.join(TEMP_FRAME_IMGS_DIR_PATH, "end_grey_frame_img.jpg")

BLACK_COLOR_RGB = 0

####################################################################################################
# Get data about given vid
####################################################################################################

def get_vid_dims(vid_file_path):
    vid = cv2.VideoCapture(vid_file_path)
    vid_w_float, vid_h_float = vid.get(cv2.CAP_PROP_FRAME_WIDTH), vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    return(int(vid_w_float), int(vid_h_float))

def get_vid_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

####################################################################################################
# Vid Time Related
####################################################################################################

def trim_vid(in_vid_path, out_vid_path, time_tup):
    """ Trims vid time from time_tup[0] to time_tup[1]"""
    def ffmpeg_extract_subclip(filename, t1, t2, target_name=None):
        """ Makes a new video file playing video file ``filename`` between
        the times ``t1`` and ``t2``. """
        print('in ffmpeg_extract_subclip')
        name, ext = os.path.splitext(filename)
        if not target_name:
            T1, T2 = [int(1000*t) for t in [t1, t2]]
            target_name = "%sSUB%d_%d.%s" % (name, T1, T2, ext)

        cmd = [get_setting("FFMPEG_BINARY"),"-y",
               "-ss", "%0.2f"%t1,
               "-i", filename,
               "-t", "%0.2f"%(t2-t1),
               "-vcodec", "copy", "-acodec", "copy", target_name]
        subprocess_call(cmd)

    ffmpeg_extract_subclip(in_vid_path, time_tup[0], time_tup[1], target_name=out_vid_path)
    return out_vid_path

####################################################################################################
# Resize Vid
####################################################################################################

# TODO look into better quality? ffmpeg -i input.mp4 -vf scale=1280:720 -preset slow -crf 18 output.mp4    https://ottverse.com/change-resolution-resize-scale-video-using-ffmpeg/
def scale_vid(new_vid_dim_tup, in_vid_path, out_vid_path):
    """
        new_vid_dims = w x h
        Example - ffmpeg -i video.mov -vf "scale=250:150" new_movie.mp4
        Will reduce H by 1 if not even
    """
    # Create out_vid_path if not exist
    out_vid_parent_dir_path_obj = Path(out_vid_path).parent
    out_vid_parent_dir_path_obj.mkdir(parents=True,exist_ok=True)

    # Delete out_vid_path if exists
    fsu.delete_if_exists(out_vid_path)

    w = new_vid_dim_tup[0]
    h = new_vid_dim_tup[1]

    # otherwise will get error:  ffmpeg height not divisible by 2
    if h % 2 != 0:
        h = h - 1

    cmd = f'ffmpeg -i {in_vid_path} -vf "scale={w}:{h}" {out_vid_path}'
    print(f"Running: {cmd}...")
    subprocess.call(cmd, shell = True)

    return out_vid_path

####################################################################################################
# Crop vid
####################################################################################################

def crop_vid(w, h, x, y, in_vid_path, out_vid_path):
    """
        w: Width of the output video (out_w). It defaults to iw. This expression is evaluated only once during the filter configuration.
        h: Height of the output video (out_h). It defaults to ih. This expression is evaluated only once during the filter configuration.
        x: Horizontal position, in the input video, of the left edge of the output video. It defaults to (in_w-out_w)/2. This expression is evaluated per-frame.
        y: Vertical position, in the input video, of the top edge of the output video. It defaults to (in_h-out_h)/2. This expression is evaluated per-frame.

        https://www.bogotobogo.com/FFMpeg/ffmpeg_cropping_video_image.php
    """

    fsu.delete_if_exists(out_vid_path)

    cmd = f'ffmpeg -i {in_vid_path} -vf "crop={w}:{h}:{x}:{y}" {out_vid_path}'
    print(f"Running: {cmd}...")
    subprocess.call(cmd, shell = True)


def crop_black_border_from_vid_if_needed(in_vid_path, out_vid_path):
    def _get_crop_coords_if_needed(color_rgb):
        ''' If no border of color_rgb, return False'''
        # TODO put in PIL utils
        def _get_crop_coords_from_border_size_d(img, border_size_d):
            """
                Gets coords for cropping out border with output of _get_color_border_size_d_fast__if_exists()
                - w: Width of the output video (out_w). It defaults to iw. This expression is evaluated only once during the filter configuration.
                - h: Height of the output video (out_h). It defaults to ih. This expression is evaluated only once during the filter configuration.
                - x: Horizontal position, in the input video, of the left edge of the output video. It defaults to (in_w-out_w)/2. This expression is evaluated per-frame.
                - y: Vertical position, in the input video, of the top edge of the output video. It defaults to (in_h-out_h)/2. This expression is evaluated per-frame.
            """
            print(f"in _get_crop_coords_from_border_size_d() - {img.size=}")
            w = img.width - border_size_d["left"] - border_size_d["right"]
            h = img.height - border_size_d["top"] - border_size_d["bottom"]
            x = border_size_d["left"]
            y = border_size_d["top"]
            return w,h,x,y

        # TODO put in PIL utils
        def _get_color_border_size_d_fast__if_exists(img, color_rgb, ret_false_if_no_border = True):
            """
             Returns dict of # pixel size of color border of each size.
               - Does this fast by checking individual lines to find min border instead of each individual pixel.
                 - B/c of this, false positives possible, change _get_const_y_pos_l() to adjust if needed
               - Focused on returning False in the case there is no border ASAP
               - If ret_false_if_no_border == False, will just return normal border_size_d with all values = 0
            """

            def _get_const_y_pos_l(img_h):
                """ If too many errors, add more/different y_pos"""
                return [
                        int(img_h * 0.25),
                        int(img_h * 0.50),
                        int(img_h * 0.75)
                    ]

            def _get_horz_num_pixels_until_not_color_multiple_lines(img, y_pos_l, color_rgb):

                def _get_horz_num_pixels_until_not_color_single_line(img, y_pos, color_rgb):
                    print("in {_get_horz_num_pixels_until_not_color_single_line()} {y_pos=}")
                    img_w, img_h = img.size

                    if y_pos < 0 or y_pos > img_h:
                        raise Exception(f"Error: Invalid y_pos ({y_pos=}) for given img dimensions: {img_w=}, {img_h=}")

                    # Could make more efficient with binary search, skipping given num pixels, etc.
                    for x in range(img_w):
                        if img.getpixel((x,y_pos)) != color_rgb:
                            print("Returning: ", (x,y_pos), x)
                            return x


                min_num_pixels_until_not_color = None

                for y_pos in y_pos_l:
                    num_pixels_until_not_color = _get_horz_num_pixels_until_not_color_single_line(img, y_pos, color_rgb)

                    # If ever find spot with no border, means edge has no border so no need to check other y_pos'
                    if num_pixels_until_not_color == 0:
                        return 0

                    if min_num_pixels_until_not_color == None:
                        min_num_pixels_until_not_color = num_pixels_until_not_color

                    # If not giving good results, maybe should add a check to require a given # of matches?
                    min_num_pixels_until_not_color = min(min_num_pixels_until_not_color, num_pixels_until_not_color)
                    print(f"....{min_num_pixels_until_not_color=}")
                return min_num_pixels_until_not_color

                # If get to end of img, means line of color_rgb goes all the way across
                return  # TODO should this be removed?>>>>>>>?>>>>?????


            border_size_d = {"left"  : 0,
                            "bottom": 0,
                            "right"  : 0,
                            "top" : 0}

            # Set what happens if no color border is found
            if ret_false_if_no_border:
                ret_on_no_border = False
            else:
                ret_on_no_border = border_size_d

            # If corners of img is not given color, must not have border of given color
            if  img.getpixel((0,0)) != 0 or \
                img.getpixel((img_w - 1, img_h - 1)) != 0:
                return ret_on_no_border

            border_size_d["left"]   = _get_horz_num_pixels_until_not_color_multiple_lines(img                         , _get_const_y_pos_l(img.height), color_rgb)
            border_size_d["top"]    = _get_horz_num_pixels_until_not_color_multiple_lines(img.rotate(90,  expand=True), _get_const_y_pos_l(img.width ), color_rgb)
            border_size_d["right"]  = _get_horz_num_pixels_until_not_color_multiple_lines(img.rotate(180, expand=True), _get_const_y_pos_l(img.height), color_rgb)
            border_size_d["bottom"] = _get_horz_num_pixels_until_not_color_multiple_lines(img.rotate(270, expand=True), _get_const_y_pos_l(img.width ), color_rgb)

            # ret_on_no_border if all sides 0
            for size in border_size_d.values():
                if size != 0:
                    return border_size_d
            return ret_on_no_border


        # Open the video file
        clip = VideoFileClip(in_vid_path)

        # Extract a series of frames from the video
        frames = [frame for frame in clip.iter_frames()]

        if (len(frames) < 22):
            raise Exception("ERROR: No hard reason this cant work, but being lazy and if you hit this then why is vid so short?")

        # Dont check very first or very last frame b/c more likely to be all black
        grey_start_frame = cv2.cvtColor(frames[10], cv2.COLOR_BGR2GRAY)
        grey_end_frame = cv2.cvtColor(frames[-10], cv2.COLOR_BGR2GRAY) # TODO Check more frames?

        # Create dirs if not exist
        fsu.delete_if_exists(START_FRAME_IMG_PATH)
        Path(START_FRAME_IMG_PATH).parent.mkdir(parents=True, exist_ok=True)

        # Check start frame
        print(f"Writing grey_start_frame to {START_FRAME_IMG_PATH}...")
        cv2.imwrite(START_FRAME_IMG_PATH, grey_start_frame)
        img = Image.open(START_FRAME_IMG_PATH)
        img_w, img_h = img.size

        border_size_d = _get_color_border_size_d_fast__if_exists(img, color_rgb, ret_false_if_no_border = True)
        pprint("border_size_d:")
        pprint(border_size_d)

        if not border_size_d:
            return False

        return tuple(_get_crop_coords_from_border_size_d(img, border_size_d))

    crop_coords = _get_crop_coords_if_needed(BLACK_COLOR_RGB)

    # If no black border, just return in_vid_path since no other file will be generated
    if crop_coords == False:
        print(f'Video does not have a black border: {in_vid_path}')
        return in_vid_path

    print("Video has a black border of some kind, cropping...")
    print(f"{crop_coords=}")

    w,h,x,y = crop_coords
    print(w,h,x,y)
    print(f"{get_vid_dims(in_vid_path)=}")
    print(f"Cropping vid at {in_vid_path=} to {out_vid_path=}...")
    crop_vid(w, h, x, y, in_vid_path, out_vid_path)
    print(f"{in_vid_path=}")
    print(w,h,x,y)
    print(f"{get_vid_dims(in_vid_path)=}")

    return out_vid_path


def crop_sides_of_vid_to_match_aspect_ratio(vid_dim_tup_to_match_aspect_ratio, in_vid_path, out_vid_path):
    """
        Makes in_vid match given aspect ratio by only cropping the sides of video
        Good for trimming sides of MC Parkour vids while keeping center 
    """
    in_vid_dim_tup = get_vid_dims(in_vid_path)
    in_vid_w = in_vid_dim_tup[0]
    in_vid_h = in_vid_dim_tup[1]

    aspect_ratio = vid_dim_tup_to_match_aspect_ratio[0] / vid_dim_tup_to_match_aspect_ratio[1]

    new_vid_w = in_vid_h * aspect_ratio
    print(f"new vid dims {new_vid_w} x {in_vid_h}")

    # At this point, h should be the same, only w has changed (reduced)
    w_diff = in_vid_w - new_vid_w
    num_pixels_to_trim_from_both_sides = int(w_diff / 2)

    crop_vid(w = w_diff,
             h = in_vid_h,
             x = num_pixels_to_trim_from_both_sides,
             y = 0,
             in_vid_path = in_vid_path, out_vid_path = out_vid_path)


def crop_sides_of_vid_by_percent(trim_percent, in_vid_path, out_vid_path):
    """
        Crops trim_percent of total width of in_vid from the sides evenly, leaving the video centered
        - Good for trimming non-important sides of shows like Family Guy
        - trim_percent =  10, 20, 30, etc.
        - EXAMPLE:
            If in_vid.size == (100, 44) pixels and trim_percent == 10:
                out_vid.size will = (90, 44) pixels, created from cropping 5 pixels from each side of in_vid
    """
    in_vid_dim_tup = get_vid_dims(in_vid_path)
    in_vid_w = in_vid_dim_tup[0]
    in_vid_h = in_vid_dim_tup[1]

    num_pixels_wide_to_remove_total = int(in_vid_w / trim_percent)
    num_pixels_wide_to_keep_total = in_vid_w - num_pixels_wide_to_remove_total
    num_pixels_to_trim_from_both_sides = int(num_pixels_wide_to_remove_total / 2)

    crop_vid(w = num_pixels_wide_to_keep_total,
                h = in_vid_h,
                x = num_pixels_to_trim_from_both_sides,
                y = 0,
                in_vid_path = in_vid_path, out_vid_path = out_vid_path)


####################################################################################################
# Combine multiple vids into new vid
####################################################################################################

def stack_vids(top_vid_path, bottom_vid_path, out_vid_path):
    top_vid_dim_tup = get_vid_dims(top_vid_path)
    top_vid_w = top_vid_dim_tup[0]
    bottom_vid_dim_tup = get_vid_dims(bottom_vid_path)
    print(f"{bottom_vid_dim_tup=}")
    bottom_vid_w = bottom_vid_dim_tup[0]

    if top_vid_w != bottom_vid_w:
        raise Exception(f"Widths of vids not the same, behavior for this not implemented - {top_vid_dim_tup=} , {bottom_vid_dim_tup=}")

    fsu.delete_if_exists(out_vid_path)

    # This command does the following:
    #     ffmpeg is the command to run ffmpeg.
    #     -i top_video.mp4 specifies the input file for the top video.
    #     -i bottom_video.mp4 specifies the input file for the bottom video.
    #     -filter_complex "[0:v][1:v]vstack=inputs=2[v]" specifies a filter complex that takes the video streams from
    #                                                    both input files ([0:v] and [1:v]) and stacks them vertically
    #                                                    to create a new video stream ([v]).
    #     -map "[v]" tells ffmpeg to use the stacked video stream as the output video.
    #     -map 0:a tells ffmpeg to use the audio stream from the top video (0:a) as the output audio.
    #     -c:v libx264 specifies the codec to use for the output video.
    #     -crf 18 specifies the quality level for the output video. A lower value results in a higher quality video,
    #             but a larger file size.
    #     -preset veryfast specifies the speed/quality tradeoff for the output video. A faster preset will result in a
    #                      faster encoding time, but potentially lower quality.
    #     output.mp4 specifies the output file for the combined video.
    # Note that this command assumes that both input videos have the same length. If the videos have different lengths,
    # you may need to specify an additional filter to pad one of the videos to match the length of the other. You can
    # also adjust the parameters (e.g. codec, quality, etc.) to suit your needs.
    cmd = f'ffmpeg \
        -i {top_vid_path} \
        -i {bottom_vid_path} \
        -filter_complex "[0:v][1:v]vstack=inputs=2[v]" \
        -map "[v]" \
        -map 0:a \
        -c:v libx264 \
        -crf 18 \
        -preset veryfast \
        {out_vid_path}'

    print(f"Running: {cmd}...")
    subprocess.call(cmd, shell = True)
    return out_vid_path

if __name__ == "__main__":
    # import make_tb_vid
    # make_tb_vid.make_tb_vid()

    import batch_make_tb_vids
    batch_make_tb_vids.main()