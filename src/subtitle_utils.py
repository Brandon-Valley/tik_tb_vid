# TODO make submodule and combine with my_movie_tools and Youtube_utils, thats probably it but check for more
from pathlib import Path
import pysubs2
from sms.file_system_utils import file_system_utils as fsu
import subprocess

# def shift_and_trim_subs(in_sub_file_path, out_sub_file_path, shift_num_ms):
#     fsu.delete_if_exists(out_sub_file_path)
#     Path(out_sub_file_path).parent.mkdir(parents=True, exist_ok=True)

#     in_subs = pysubs2.load(in_sub_file_path, encoding="utf-8")

#     in_subs.shift(ms = shift_num_ms)

#     print(f"Saving shifted/trimmed subs to {out_sub_file_path=}...")
#     in_subs.save(out_sub_file_path)

# def shift_trim_and_sync_subs(in_sub_file_path, out_sub_file_path, shift_num_ms):
#     fsu.delete_if_exists(out_sub_file_path)
#     Path(out_sub_file_path).parent.mkdir(parents=True, exist_ok=True)

#     in_subs = pysubs2.load(in_sub_file_path, encoding="utf-8")

#     in_subs.shift(ms = shift_num_ms)

#     print(f"Saving shifted/trimmed subs to {out_sub_file_path=}...")
#     in_subs.save(out_sub_file_path)

    # sync_subs_with_vid()

def sync_subs_with_vid(vid_path, in_sub_path, out_sub_path):
    fsu.delete_if_exists(out_sub_path)
    Path(out_sub_path).parent.mkdir(parents=True, exist_ok=True)

    # cmd = f'ffs "{vid_path}" -i "{in_sub_path}" -o "{out_sub_path}"'
    cmd = f'autosubsync "{vid_path}" "{in_sub_path}" "{out_sub_path}"'
    print(f"Running cmd: {cmd}...")
    # subprocess.call(cmd, shell=True)
    subprocess.call(cmd, shell=False)



if __name__ == "__main__":
    import os.path as path
    print("Running ",  path.abspath(__file__),  '...')
    sync_subs_with_vid(vid_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.mp4",
     in_sub_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/init_shift.en.srt",
      out_sub_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.en.srt")
    print("End of Main")
