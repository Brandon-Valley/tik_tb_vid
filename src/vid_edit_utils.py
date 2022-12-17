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



# def vid_resize(vid_path, output_path, width, overwrite = True):
#     '''
#     use ffmpeg to resize the input video to the width given, keeping aspect ratio
#     '''
#     if not( os.path.isdir(os.path.dirname(output_path))):
#         # raise ValueError(f'output_path directory does not exists: {os.path.dirname(output_path)}')

#         # Create out_vid_path if not exist
#         out_vid_parent_dir_path_obj = Path(output_path).parent
#         out_vid_parent_dir_path_obj.mkdir(parents=True,exist_ok=True)

#     if os.path.isfile(output_path) and not overwrite:
#         # warnings.warn(f'{output_path} already exists but overwrite switch is False, nothing done.')
#         # return None
#         raise Exception("ERROR: NOT IMPLEMENTED")

#     input_vid = ffmpeg.input(vid_path)
#     vid = (
#         input_vid
#         .filter('scale', width, -1)
#         .output(output_path)
#         .overwrite_output()
#         .run()
#     )
#     return output_path