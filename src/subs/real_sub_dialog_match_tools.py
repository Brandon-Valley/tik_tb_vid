from pprint import pprint
from os.path import join
from pathlib import Path
import pysubs2

if __name__ == "__main__":
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).parent.parent))

from sms.file_system_utils import file_system_utils as fsu
import vid_edit_utils as veu
import subtitle_utils as su



def _get_line_dialog_fuzz_ratio(line):
    # return line.start

    line_start_time_sec = line.start / 1000
    line_end_time_sec   = line.end   / 1000


def get_thing(in_vid_path, unique_final_vid_sub_path_l):
    print(unique_final_vid_sub_path_l)

    for sub_path in unique_final_vid_sub_path_l:
        subs = pysubs2.load(sub_path, encoding="latin1")

        for line in subs:
            line_dialog_fuzz_ratio = _get_line_dialog_fuzz_ratio(line)
            print(f"{line_dialog_fuzz_ratio=}")




if __name__ == "__main__":
    import os.path as path
    print("Running " , path.abspath(__file__) , '...')
    get_thing(in_vid_path = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/Family_Guy___TBS/Family_Guy__Back_To_The_Pilot__Clip____TBS/Family_Guy__Back_To_The_Pilot__Clip____TBS.mp4",
               unique_final_vid_sub_path_l = )
    
    print("End of Main") 