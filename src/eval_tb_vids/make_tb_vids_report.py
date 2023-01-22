
if __name__ == "__main__":
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).parent.parent))

from sms.file_system_utils import file_system_utils as fsu
import vid_edit_utils as veu
import subtitle_utils as su

def _tmp_add_len_to_vid_titles(dir_path):
    vid_path_l = fsu.get_dir_content_l(dir_path, "file")

    for vid_path in vid_path_l:
        vid_len = veu.get_vid_length(vid_path)
        print(f"{vid_len=}")


if __name__ == "__main__":
    import os.path as path
    print("Running " , path.abspath(__file__) , '...')
    dp = "C:/p/tik_tb_vid_big_data/ignore/final_output"
    _tmp_add_len_to_vid_titles(dp)

    print("End of Main") 
