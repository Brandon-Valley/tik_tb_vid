
import vid_edit_utils as veu
from pathlib import Path
import os
import random
import cfg
from vid_edit_utils import Impossible_Dims_Exception
from sms.file_system_utils import file_system_utils as fsu
from os.path import join



cur_top_vid_path = "C:/p/tik_tb_vid_big_data/ignore/working/top__scaled.mp4.123"
final_top_vid_dims_tup = (1,222)

# Put top vid height in filename as ref. point if add subtitles
cur_out_vid_name = Path(cur_top_vid_path).name.split(".")[0] + f"__tvh_{final_top_vid_dims_tup[1]}_" + '.' + '.'.join(Path(cur_top_vid_path).name.split(".")[1:])
print(f"{cur_out_vid_name=}")