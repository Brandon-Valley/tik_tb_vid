from moviepy.tools import subprocess_call
from moviepy.config import get_setting
import os
import cv2


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
    
