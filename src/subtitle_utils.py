# TODO make submodule and combine with my_movie_tools and Youtube_utils, thats probably it but check for more
from pprint import pprint
from langdetect import detect


from collections import namedtuple
import re
from typing import Optional, List, Tuple, Sequence
from pysubs2.common import IntOrFloat

from subtitle_filter import Subtitles


from pathlib import Path
import pysubs2
from sms.file_system_utils import file_system_utils as fsu
from sms.logger import txt_logger
import subprocess

def sync_subs_with_vid(vid_path, in_sub_path, out_sub_path):
    """ Best to use sub files without "(cheering)", "(gasps)", etc. (.HI.srt and more) """
    print("in sync_subs_with_vid() --------------------------")
    fsu.delete_if_exists(out_sub_path)
    Path(out_sub_path).parent.mkdir(parents=True, exist_ok=True)

    cmd = f'autosubsync "{vid_path}" "{in_sub_path}" "{out_sub_path}"'
    print(f"Running cmd: {cmd}...")
    subprocess.call(cmd, shell=False)
    print("end of sync_subs_with_vid() --------------------------")


def combine_mp4_and_sub_into_mkv(in_mp4_path, in_sub_path, out_mkv_path):
    """ Sub MAY need to be .srt """
    cmd = f'ffmpeg -i {in_mp4_path} -i {in_sub_path} -c copy -c:s copy {out_mkv_path}'
    print(f"Running {cmd}...")
    subprocess.call(cmd, shell=True)


def combine__mp4__and__sub_path_lang_dl__into_mkv(in_mp4_path, sub_path_lang_dl, out_mkv_path, default_sub_track_num = None):
    """ 
        First sub in sub_path_lang_dl will be default
        - Subs MAY need to be .srt
        - Set default_sub_track_num = 0 to make first sub track default
        - EXAMPLE:
            sub_path_lang_dl = [
                                    {
                                        "path": "<ABS_PATH_TO_SUB_FILE_1>",
                                        "lang": "en"
                                    },
                                    {
                                        "path": "<ABS_PATH_TO_SUB_FILE_2>",
                                        "lang": "en2"
                                    },
                                ]
    """
    if len(sub_path_lang_dl) == 0:
        raise Exception(f"ERROR: {sub_path_lang_dl=} Must have at least 1 element - {len(sub_path_lang_dl)=}")

    cmd = f'ffmpeg -i "{in_mp4_path}"'
    
    for sub_path_lang_d in sub_path_lang_dl:
        cmd += f' -i "{sub_path_lang_d["path"]}"'

    cmd += " -map 0"

    for i in range(len(sub_path_lang_dl)):
        cmd += f" -map {i + 1}"

    cmd += " -c copy"

    for sub_path_lang_d_num, sub_path_lang_d in enumerate(sub_path_lang_dl):
        cmd += f' -metadata:s:s:{sub_path_lang_d_num} language={sub_path_lang_d["lang"]}'

    if default_sub_track_num != None:
        cmd += f' -disposition:s:{default_sub_track_num} default'

    cmd += f' "{out_mkv_path}"'
    
    print(f"Running {cmd=}...\n")
    subprocess.call(cmd, shell=True)


def combine__mp4__and__sub_path_l__into_mkv__set_file_name_as_lang(in_mp4_path, sub_path_l, out_mkv_path):
    sub_path_lang_dl = []

    for sub_path in sub_path_l:
        sub_file_name = Path(sub_path).name

        sub_path_lang_dl.append({
            "path" : sub_path,
            "lang" : sub_file_name.replace(".", "_") # if this is too long might show up as [Fam] in player
        })

    combine__mp4__and__sub_path_lang_dl__into_mkv(in_mp4_path, sub_path_lang_dl, out_mkv_path)


def make_embedded_mkv_sub_track_show_by_default(mkv_path, sub_track_num = 0):
    """ !!! WARNING !!! This is pretty fast, but still prints all the FFMPEG stuff, so may be better to just add the args to whatever other cmds you are using. """
    o = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/mkvs/S10E05__Family_Guy__Back_To_The_Pilot__Clip____TBSFIXEDDDDDDDDDDDD.mkv"
    # TODO finish
    # https://stackoverflow.com/questions/26956762/ffmpeg-set-subtitles-track-as-default
    mp_path = "C:/Program Files (x86)/MKVToolNix/mkvpropedit.exe" # TODO
    cmd = f'ffmpeg -i "{mkv_path}" -c copy -disposition:s:{sub_track_num} default {o}'
    print(f"Running {cmd}...")
    raise Exception("NOT FINISHED BUT SHOULD WORK BUT READ WARNING")


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
        new_sub_line_l.append(str(clean_sub_line_num + 1)) # starts at 1 for .srt
        new_sub_line_l.append(f"{ms_to_srt_time_str(clean_sub_line.start)} --> {ms_to_srt_time_str(clean_sub_line.end)}")
        new_sub_line_l.append(clean_sub_line.text.replace("\\N", "\n"))
        new_sub_line_l.append("")

    txt_logger.write(new_sub_line_l, out_sub_path, encoding="latin1")


def sub_file_readable_srt(sub_file_path):
    try:
        subs = pysubs2.load(sub_file_path, encoding="latin1")
        return True
    except pysubs2.UnknownFPSError:
        return False


def sub_file_is_correct_lang(sub_file_path, lang):
    file_str = ""
    subs = pysubs2.load(sub_file_path, encoding="latin1")

    for line in subs:
        file_str += line.text

    detected_lang = detect(file_str)
    if lang == detected_lang:
        return True
    else:
        return False


def remove_advertising_from_sub_file(sub_file_path):
    cmd = f'subnuker --yes --aeidon "{sub_file_path}"'
    print(f"Running {cmd=}...")
    subprocess.call(cmd, shell=True)

    cmd = f'subnuker --yes --regex "{sub_file_path}"'
    print(f"Running {cmd=}...")
    subprocess.call(cmd, shell=True)


def remove_advertising_from_sub_file_path_l(sub_file_path_l):
    cmd = f"subnuker --yes --aeidon"
    for sub_file_path in sub_file_path_l:
        cmd += f' "{sub_file_path}"'
    subprocess.call(cmd, shell=True)

    cmd = f"subnuker --yes --regex"
    for sub_file_path in sub_file_path_l:
        cmd += f' "{sub_file_path}"'
    subprocess.call(cmd, shell=True)


def write_filtered_subs(in_sub_path, out_sub_path):
    ''' Removes effects like [Music] and other things '''
    
    Path(out_sub_path).parent.mkdir(parents=True, exist_ok=True)

    subs = Subtitles(in_sub_path) # will break on .txt
    subs.filter(
        rm_fonts=True,
        rm_ast=True,
        rm_music=True,
        rm_effects=True,
        rm_names=True,
        rm_author=True,
    )
    fsu.delete_if_exists(out_sub_path)
    subs.save(out_sub_path)


if __name__ == "__main__":
    import os.path as path
    print("Running ",  path.abspath(__file__),  '...')

    # write_filtered_subs("C:/tmp/filter_test/family.guy.s09e02.dvdrip.xvid-reward-eng.srt",
    #                     "C:/tmp/filter_test/FILTERED.srt")

    write_filtered_subs("C:/tmp/filter_test/family.guy.s09e02.dvdrip.xvid-reward-eng.srt",
                        "C:/tmp/filter_test/family.guy.s09e02.dvdrip.xvid-reward-eng.srt")
    
    # subs = pysubs2.load("C:/tmp/filter_test/OLD_Family_Guy__Brian_Goes_Republican_for_Rush_Limbaugh__Season_9_Clip____TBS.srt", encoding="latin1")
    # subs.save("C:/tmp/filter_test/Family_Guy__Brian_Goes_Republican_for_Rush_Limbaugh__Season_9_Clip____TBS.srt", encoding="utf-8")
    

    # nonascii = bytearray(range(0x80, 0x100))
    # with open('"C:/tmp/filter_test/OLD_Family_Guy__Brian_Goes_Republican_for_Rush_Limbaugh__Season_9_Clip____TBS.srt"','rb') as infile, open('d_parsed.txt','wb') as outfile:
    #     for line in infile: # b'\n'-separated lines (Linux, OSX, Windows)
    #         outfile.write(line.translate(None, nonascii))

    # nonascii = bytearray(range(0x80, 0x100))
    # with open("C:/tmp/filter_test/OLD_Family_Guy__Brian_Goes_Republican_for_Rush_Limbaugh__Season_9_Clip____TBS.srt",'wb') as infile:
    #     for line in infile: # b'\n'-separated lines (Linux, OSX, Windows)
    #         infile.write(line.translate(None, nonascii))


    # lines = txt_logger.read("C:/tmp/filter_test/FAILED_FILTER__Family_Guy__Brian_Goes_Republican_for_Rush_Limbaugh__Season_9_Clip____TBS.srt")
    # # txt_logger.write(lines, "C:/tmp/filter_test/Family_Guy__Brian_Goes_Republican_for_Rush_Limbaugh__Season_9_Clip____TBS.srt",encoding="ascii", decode=True)
    # txt_logger.write(lines, "C:/tmp/filter_test/Family_Guy__Brian_Goes_Republican_for_Rush_Limbaugh__Season_9_Clip____TBS.srt", decoding="ascii")

    # write_auto_subs_for_vid(in_vid_path = "C:/tmp/auto_caption_test/Family_Guy__Back_To_The_Pilot__Clip____TBS.mp4",
    #                          out_sub_path = "C:/tmp/auto_caption_test/Family_Guy__Back_To_The_Pilot__Clip____TBS.srt", format_str = "srt")



    # # sync_subs_with_vid(vid_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.mp4",
    # #  in_sub_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/init_shift.en.srt",
    # #   out_sub_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.en.srt")

    # in_vid_path = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/Family_Guy__TBS__alcho_and_pilot__SUB_SET_TEST/Family_Guy__Back_To_The_Pilot__Clip____TBS/Family_Guy__Back_To_The_Pilot__Clip____TBS.mp4"
    # # sub_file_l = ["C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s1_e1and2/s10/episode 5/Family.Guy.S10E05.HDTV.XviD-LOL.srt",
    # # "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s1_e1and2/s10/episode 5/Family.Guy.S10E05.HDTV.XviD-LOL.HI.srt"]
    # sub_file_l = ["C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s1_e1and2/s10/episode 5/Family.Guy.S10E05.HDTV.XviD-LOL.srt",
    # "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s1_e1and2/s10/episode 5/Family.Guy.S10E05.HDTV.XviD-LOL.HI.srt"]

    # # sub_path_lang_dl = [
    # #                         {
    # #                             "path": "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s1_e1and2/s10/episode 5/Family.Guy.S10E05.HDTV.XviD-LOL.srt",
    # #                             "lang": "en"
    # #                         },
    # #                         {
    # #                             "path": "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s1_e1and2/s10/episode 5/Family.Guy.S10E05.HDTV.XviD-LOL.HI.srt",
    # #                             "lang": "en2"
    # #                         },
    # #                     ]



    # # out_mkv_path = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/Family_Guy__TBS__alcho_and_pilot__SUB_SET_TEST/Family_Guy__Back_To_The_Pilot__Clip____TBS/Family_Guy__Back_To_The_Pilot__Clip____TBS.mkv"

    # # # combine__mp4__and__sub_path_lang_dl__into_mkv(in_vid_path, sub_path_lang_dl, out_mkv_path)


    # # combine__mp4__and__sub_path_l__into_mkv__set_file_name_as_lang(in_vid_path, sub_file_l, out_mkv_path)

    # make_embedded_mkv_sub_track_show_by_default(mkv_path = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/mkvs/S10E05__Family_Guy__Back_To_The_Pilot__Clip____TBS.mkv",
    #  sub_track_num = 0)


    # # remove_advertising_from_sub_file("C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s5_e17/s05/episode 17/Modern.Family.S05E17.720p.WEB-DL.DD5.1.H.264-HWD.en.srt")
    # # make_single_embedded_mkv_sub_show_by_default("C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/mkvs/S04E16__Family_Guy__Google_Earth__Clip____TBS.mkv")
    # # remove_advertising_from_sub_file_path_l(["C:/p/tik_tb_vid_big_data/ignore/test/sub_adv_remove_test/Family.Guy.S10E20.720p.HDTV.X264-DIMENSION - Copy.srt",
    # # "C:/p/tik_tb_vid_big_data/ignore/test/sub_adv_remove_test/Family.Guy.S10E20.720p.HDTV.X264-DIMENSION - Copy - Copy.srt"])
    print("End of Main")
