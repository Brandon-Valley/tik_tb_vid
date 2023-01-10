# TODO make submodule and combine with my_movie_tools and Youtube_utils, thats probably it but check for more
from langdetect import detect


from collections import namedtuple
import re
from typing import Optional, List, Tuple, Sequence
from pysubs2.common import IntOrFloat




from pathlib import Path
import pysubs2
from sms.file_system_utils import file_system_utils as fsu
from sms.logger import txt_logger
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


def combine_mp4_and_sub_into_mkv(in_mp4_path, in_sub_path, out_mkv_path):
    """ Sub MAY need to be .srt """
    cmd = f'ffmpeg -i {in_mp4_path} -i {in_sub_path} -c copy -c:s copy {out_mkv_path}'
    print(f"Running {cmd}...")
    subprocess.call(cmd, shell=True)

def ms_to_srt_time_str(ms):
    Times = namedtuple("Times", ["h", "m", "s", "ms"])

    def _ms_to_times(ms: IntOrFloat) -> Tuple[int, int, int, int]:
        """
        Convert milliseconds to normalized tuple (h, m, s, ms).
        
        Arguments:
            ms: Number of milliseconds (may be int, float or other numeric class).
                Should be non-negative.
        
        Returns:
            Named tuple (h, m, s, ms) of ints.
            Invariants: ``ms in range(1000) and s in range(60) and m in range(60)``
        """
        ms = int(round(ms))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return Times(h, m, s, ms)

    h, m, s, ms = _ms_to_times(abs(ms))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_manual_sub_line_l(manual_sub_line_l, out_sub_path):
    fsu.delete_if_exists(out_sub_path)
    Path(out_sub_path).parent.mkdir(parents=True, exist_ok=True)

    new_sub_line_l = []
    for clean_sub_line_num, clean_sub_line in enumerate(manual_sub_line_l):
        # new_sub_line_num = clean_sub_line_num + 1 # starts at 1 for .srt
        # print(f"{clean_sub_line_num=}")
        # exit()
        new_sub_line_l.append(str(clean_sub_line_num + 1)) # starts at 1 for .srt
        new_sub_line_l.append(f"{ms_to_srt_time_str(clean_sub_line.start)} --> {ms_to_srt_time_str(clean_sub_line.end)}")
        new_sub_line_l.append(clean_sub_line.text.replace("\\N", "\n"))
        new_sub_line_l.append("")

    txt_logger.write(new_sub_line_l, out_sub_path)

def sub_file_readable_srt(sub_file_path):
    try:
        subs = pysubs2.load(sub_file_path, encoding="latin1")
        return True
    except pysubs2.UnknownFPSError:
        return False


def sub_file_is_correct_lang(sub_file_path, lang):
    file_str = ""
    # # subs = pysubs2.load(sub_file_path, encoding="latin1")
    # lines = txt_logger.read(sub_file_path)
    # # for line in subs:
    # for line in lines:
    #     if len(line) > 1 and line[0].isalpha():
    #         file_str += line
    subs = pysubs2.load(sub_file_path, encoding="latin1")
    # lines = txt_logger.read(sub_file_path)
    for line in subs:
    # for line in lines:
        # if len(line) > 1 and line[0].isalpha():
        file_str += line.text

    detected_lang = detect(file_str)
    if lang == detected_lang:
        return True
    else:
        return False


if __name__ == "__main__":
    import os.path as path
    print("Running ",  path.abspath(__file__),  '...')
    sync_subs_with_vid(vid_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.mp4",
     in_sub_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/init_shift.en.srt",
      out_sub_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.en.srt")
    print("End of Main")
