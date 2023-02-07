from pprint import pprint
from os.path import join
from pathlib import Path
from tempfile import mktemp
import time
import pysubs2
from fuzzywuzzy import fuzz

from time import sleep
from random import random
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait


if __name__ == "__main__":
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).parent.parent))

import cfg
from sms.file_system_utils import file_system_utils as fsu
from sms.audio_edit_utils import audio_edit_utils as aeu
from sms.logger import txt_logger
import vid_edit_utils as veu
import subtitle_utils as su
import fuzz_common as fc



def _get_line_dialog_fuzz_ratio_and_confidence(in_vid_audio_path, line):
    # return line.start

    line_start_time_sec = line.start / 1000
    line_end_time_sec   = line.end   / 1000

    # result = aeu.get_transcript_from_vid(in_vid_path, line_start_time_sec, line_end_time_sec, with_confidence = True)
    result = aeu.get_transcript_from_audio(in_vid_audio_path, line_start_time_sec, line_end_time_sec, with_confidence = True)

    if result == False:
        return 0, 0 # TMP is 0 confidence correct? should it be 100? 50?
    
    transcript_str, confidence = result

    # LATER do something with confidence?

    cleaned_transcript_str = fc.get_cleaned_line_text_str__from__sub_line_text_str(transcript_str)
    transcript_fuzz_str = fc.get_subs_fuzz_str__from__all_sub_lines_cleaned_text_str(cleaned_transcript_str)

    cleaned_line_text_str = fc.get_cleaned_line_text_str__from__sub_line_text_str(line.text)
    line_text_fuzz_str = fc.get_subs_fuzz_str__from__all_sub_lines_cleaned_text_str(cleaned_line_text_str)

    fuzz_ratio = fuzz.ratio(line_text_fuzz_str, transcript_fuzz_str)
    return fuzz_ratio, confidence



def _get_line_dialog_fuzz_ratio_l(in_vid_audio_path, filtered_subs):
    line_dialog_fuzz_ratio_and_confidence_tup_l = []

    def _get_and_append_line_dialog_fuzz_ratio_and_confidence_tup(in_vid_audio_path, line):
        line_dialog_fuzz_ratio_and_confidence_tup = _get_line_dialog_fuzz_ratio_and_confidence(in_vid_audio_path, line)
        print(f"{line_dialog_fuzz_ratio_and_confidence_tup=}")
        # line_dialog_fuzz_ratio_and_confidence_tup = 
        line_dialog_fuzz_ratio_and_confidence_tup_l.append(line_dialog_fuzz_ratio_and_confidence_tup)

    with ThreadPoolExecutor(cfg.NUM_CORES) as executor:
        futures = []

        # for line in filtered_subs[::int(len(filtered_subs) / 12)]: # TODO const
        for line in filtered_subs[::int(len(filtered_subs) / 12)]: # TODO const

            # submit tasks and collect futures
            futures = [executor.submit(_get_and_append_line_dialog_fuzz_ratio_and_confidence_tup, in_vid_audio_path, line)]

        # wait for all tasks to complete
        print('Waiting for tasks to complete...')
        wait(futures)
        print('All tasks are done!')

    return line_dialog_fuzz_ratio_and_confidence_tup_l



def get_avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d(in_vid_path, unique_final_vid_sub_path_l, filtered_real_subs_dir_path):
    start_time = time.time()
    fsu.delete_if_exists(filtered_real_subs_dir_path)
    Path(filtered_real_subs_dir_path).mkdir(parents=True, exist_ok=True)

    print(unique_final_vid_sub_path_l)

    tmp_vid_audio_path = mktemp(prefix=Path(in_vid_path).stem, suffix = ".wav")
    aeu.get_audio_from_video(in_vid_path, tmp_vid_audio_path)

    avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d = {}
    for sub_path in unique_final_vid_sub_path_l:

        # get filtered subs
        file_name = f"FILTERED__" + Path(sub_path).name.split("_")[0] + ".srt"
        filtered_sub_path = join(filtered_real_subs_dir_path, file_name)
        su.write_filtered_subs(sub_path, filtered_sub_path)
        filtered_subs = pysubs2.load(filtered_sub_path, encoding="latin1")
        
        line_dialog_fuzz_ratio_and_confidence_tup_l = _get_line_dialog_fuzz_ratio_l(tmp_vid_audio_path, filtered_subs)
        print(f"{line_dialog_fuzz_ratio_and_confidence_tup_l=}")

        # only evaluate the "most confident" fuzz ratios
        line_dialog_fuzz_ratio_sorted_by_confidence_l = [tup[0] for tup in sorted(line_dialog_fuzz_ratio_and_confidence_tup_l, key= lambda tup: tup[1], reverse=True)]
        print(f">>{line_dialog_fuzz_ratio_sorted_by_confidence_l=}")

        num_top_es_to_keep = int(len(line_dialog_fuzz_ratio_sorted_by_confidence_l) * 0.75) # TODO const
        print(f"{num_top_es_to_keep=}")
        most_confident_line_dialog_fuzz_ratio_l = line_dialog_fuzz_ratio_sorted_by_confidence_l[:num_top_es_to_keep]

        # Get avg and add to d
        avg = sum(most_confident_line_dialog_fuzz_ratio_l) / len(most_confident_line_dialog_fuzz_ratio_l)
        
        if avg in avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d.keys():
            avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d[avg].append(sub_path)
        else:
            avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d[avg] = [sub_path]

    fsu.delete_if_exists(tmp_vid_audio_path)

    total_time = time.time() - start_time
    print(f"Finished get_avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d() - {total_time=}")
    return avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d




if __name__ == "__main__":
    import os.path as path
    print("Running " , path.abspath(__file__) , '...')
    avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d = get_avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d(in_vid_path = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/Family_Guy___TBS/Family_Guy__Back_To_The_Pilot__Clip____TBS/Family_Guy__Back_To_The_Pilot__Clip____TBS.mp4",
               unique_final_vid_sub_path_l =[
        "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/YT_PL_DATA/Family_Guy__Back_To_The_Pilot__Clip____TBS/f0_family.guy.s10e05.back.to.the.pilot.dvdrip.x264-demand.srt",
        "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/YT_PL_DATA/Family_Guy__Back_To_The_Pilot__Clip____TBS/f1_Family.Guy.S10E05.720p.WEB-DL.DD5.1.H.264-CtrlHD.srt"
               ],
                filtered_real_subs_dir_path = "C:/tmp/dialog_match_test/filtered")

    print(f"{avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d=}")
    
    print("End of Main") 