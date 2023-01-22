from os.path import join
from pathlib import Path

if __name__ == "__main__":
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).parent.parent))

from sms.file_system_utils import file_system_utils as fsu
import vid_edit_utils as veu
import subtitle_utils as su

def _tmp_add_len_to_vid_titles(dir_path):
    vid_path_l = fsu.get_dir_content_l(dir_path, "file")

    for vid_path in vid_path_l:
        vid_len_str = veu.get_vid_length(vid_path, return_type = "min_sec_str")
        new_vid_name = f"{vid_len_str}__" + Path(vid_path).name
        new_vid_path = join(Path(vid_path).parent, new_vid_name)
        print(f"Renaming {vid_path} to {new_vid_path}...")
        fsu.rename_file_overwrite(vid_path, new_vid_path)


if __name__ == "__main__":
    import os.path as path
    print("Running " , path.abspath(__file__) , '...')
    dp = "C:/p/tik_tb_vid_big_data/ignore/final_output"
    # _tmp_add_len_to_vid_titles(dp)

    print("End of Main") 
