from pprint import pprint
import os
from os.path import join
from tempfile import mkdtemp

# from sms.logger import txt
from pathlib import Path
import pysubs2

if __name__ == "__main__":
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).parent.parent))

import fuzz_common
import thread_utils

import cfg
import subtitle_utils as su
from sms.file_system_utils import file_system_utils as fsu
from sms.logger import json_logger
from sms.logger import txt_logger

class Matched_Vid_Sub_Dir:
    vid_path = None
    sub_path = None
    def __init__(self, in_dir_path):
        self.dir_path = in_dir_path

        self._set_and_validate_vid_and_sub_paths()
    

    def _set_and_validate_vid_and_sub_paths(self):
        path_l = fsu.get_dir_content_l(self.dir_path, "file")

        if len(path_l) != 2:
            raise ValueError(f"{len(path_l)=} != 2, expecting 1 vid and 1 sub file in {self.dir_path=}")
        
        for path in path_l:
            if Path(path).suffix == ".mp4":
                self.vid_path = path
            elif Path(path).suffix == ".srt":
                self.sub_path = path

        if self.vid_path == None or self.sub_path == None:
            raise ValueError(f"Both {self.vid_path=} and {self.sub_path=} should be set, must mean the files in {self.dir_path=} do not have the correct exts")
    

if __name__ == "__main__":
    import os.path as path
    print("Running " , path.abspath(__file__) , '...')
    mvsd = Matched_Vid_Sub_Dir("C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/o_mp4_srt_dirs/w_subs/Family_Guy__Back_To_The_Pilot__Clip____TBS")
    print(f"{mvsd.dir_path=}")
    print(f"{mvsd.vid_path=}")
    print(f"{mvsd.sub_path=}")
    print("End of Main") 
