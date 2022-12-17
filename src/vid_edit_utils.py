from moviepy.tools import subprocess_call
from moviepy.config import get_setting
import os
import cv2
import subprocess
from pathlib import Path
import ffmpeg
from sms.file_system_utils import file_system_utils as fsu

def get_vid_dims(vid_file_path):
#     vid = cv2.VideoCapture(vid_file_path)
#     return (vid.get(cv2.CAP_PROP_FRAME_WIDTH), vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

    vid = cv2.VideoCapture(vid_file_path)
    vid_w_float, vid_h_float = vid.get(cv2.CAP_PROP_FRAME_WIDTH), vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    return(int(vid_w_float), int(vid_h_float))


def trim_vid(in_vid_path, out_vid_path, time_tup):
    def ffmpeg_extract_subclip(filename, t1, t2, targetname=None):
        """ Makes a new video file playing video file ``filename`` between
        the times ``t1`` and ``t2``. """
        print('in ffmpeg_extract_subclip')#```````````````````````````````````````````````````````````````````
        name, ext = os.path.splitext(filename)
        if not targetname:
            T1, T2 = [int(1000*t) for t in [t1, t2]]
            targetname = "%sSUB%d_%d.%s" % (name, T1, T2, ext)
    
        cmd = [get_setting("FFMPEG_BINARY"),"-y",
               "-ss", "%0.2f"%t1,
               "-i", filename,
               "-t", "%0.2f"%(t2-t1),
               "-vcodec", "copy", "-acodec", "copy", targetname]
        subprocess_call(cmd)
        
    ffmpeg_extract_subclip(in_vid_path, time_tup[0], time_tup[1], targetname=out_vid_path)
    

def scale_vid(new_vid_dim_tup, in_vid_path, out_vid_path):
    """ 
        new_vid_dims = w x h
        Example - ffmpeg -i video.mov -vf "scale=250:150" newmovie.mp4
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


def get_vid_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)



def stack_vids(top_vid_path, bottom_vid_path, out_vid_path):
    top_vid_dim_tup = get_vid_dims(top_vid_path)
    top_vid_w = top_vid_dim_tup[0]
    # top_vid_h = top_vid_dim_tup[1]
    bottom_vid_dim_tup = get_vid_dims(bottom_vid_path)
    bottom_vid_w = bottom_vid_dim_tup[0]
    # bottom_vid_h = bottom_vid_dim_tup[1]

    if top_vid_w != bottom_vid_w:
        raise Exception(f"Widths of vids not the same, behavior for this not implemented - {top_vid_dim_tup=} , {bottom_vid_dim_tup=}")

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
    #     -crf 18 specifies the quality level for the output video. A lower value results in a higher quality video, but a larger file size.
    #     -preset veryfast specifies the speed/quality tradeoff for the output video. A faster preset will result in a faster encoding time, but potentially lower quality.
    #     output.mp4 specifies the output file for the combined video.

    # Note that this command assumes that both input videos have the same length. If the videos have different lengths, you may need to specify an additional filter to pad one of the videos to match the length of the other. You can also adjust the parameters (e.g. codec, quality, etc.) to suit your needs.
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

