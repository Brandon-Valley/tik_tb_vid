import pysubs2
from sms.file_system_utils import file_system_utils as fsu
from pathlib import Path
# from fuzzysearch import find_near_matches

from fuzzywuzzy import fuzz


FUZZ_STR_DELIM = ' '

# def _subs_to_subs_fuzz_str(in_subs):
#     subs_fuzz_str = ""
#     for line in in_subs:
#         subs_fuzz_str = subs_fuzz_str + line.text + FUZZ_STR_DELIM
#     return subs_fuzz_str

# def _get_fuzzy_search_match_from_fuzz_strs(real_subs_fuzz_str, auto_subs_fuzz_str):
#     # search for 'PATTERN' with a maximum Levenshtein Distance of 1
#     # match = find_near_matches('PATTERN', '---PATERN---', max_l_dist=1)
#     match = find_near_matches(auto_subs_fuzz_str, real_subs_fuzz_str, max_l_dist=1)
#     print(f"{match=}")
#     # [Match(start=3, end=9, dist=1, matched="PATERN")]
#     return match

def _compare_sub_slots(real_subs, auto_subs, sub_slot_offset):
    sub_slot_score = 0
    best_auto_sub_line_match_index = False
    best_auto_sub_line_match_score = 0

    for auto_sub_line_num, auto_sub_line in enumerate(auto_subs):
        real_sub_line = real_subs[auto_sub_line_num + sub_slot_offset]
        print(f"{auto_sub_line_num=}")
        print(f"{auto_sub_line.text=}")
        print(f"{real_sub_line.text=}")

        auto_sub_line_match_score = fuzz.ratio(auto_sub_line.text, real_sub_line.text)
        sub_slot_score += auto_sub_line_match_score
        
        if auto_sub_line_match_score > best_auto_sub_line_match_score:
            best_auto_sub_line_match_score = auto_sub_line_match_score
            best_auto_sub_line_match_index = auto_sub_line_num

    return sub_slot_score, best_auto_sub_line_match_index

def trim_and_re_time_real_sub_file_from_auto_subs(real_sub_file_path, auto_sub_file_path, out_sub_path):

    fsu.delete_if_exists(out_sub_path)
    Path(out_sub_path).parent.mkdir(parents=True, exist_ok=True)

    real_subs = pysubs2.load(real_sub_file_path, encoding="utf-8")
    auto_subs = pysubs2.load(auto_sub_file_path, encoding="utf-8")

    if len(real_subs) == 0:
        raise Exception(f"ERROR: {len(real_subs)=} - I assume this is a problem?")
    if len(auto_subs) == 0:
        raise Exception(f"ERROR: {len(auto_subs)=} - I assume this is a problem?")
    if len(auto_subs) > len(real_subs):
        raise Exception(f"ERROR: {len(auto_subs)=} > {len(real_subs)=} - This should never be possible, maybe sub formats are weird? {real_sub_file_path=}, {auto_sub_file_path=}")

    possible_sub_slots = len(real_subs) - len(auto_subs)
    print(f"{possible_sub_slots=}")

    for sub_slot_offset in range(possible_sub_slots):
        print(f"{sub_slot_offset=}")
        sub_slot_score, best_auto_sub_line_match_index = _compare_sub_slots(real_subs, auto_subs, sub_slot_offset)
        print(f"..{sub_slot_score=}")
        print(f"..{best_auto_sub_line_match_index=}")

        if best_auto_sub_line_match_index == False:
            raise Exception(f"ERROR: {best_auto_sub_line_match_index=}, this means maybe some subs are empty or something else happened?")




    print(f"{possible_sub_slots=}")

    # # subs.shift(s=2.5)
    # for line in subs:
    #     # line.text = "{\\be1}" + line.text
    #     print(f"{line.text=}")
    #     print(f"{line.start=}")
    #     print(f"{line.end=}")
    # subs.save(out_sub_path)

    print(fuzz.ratio("this is a test", "this is a test!"))



if __name__ == "__main__":
    real_sub_file_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/family.guy.s10.e05.back.to.the.pilot.(2011).eng.1cd.(4413506)/Family.Guy.S10E05.720p.WEB-DL.DD5.1.H.264-CtrlHD.srt"
    auto_sub_file_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.en.srt"
    out_sub_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS/out.en.srt"
    trim_and_re_time_real_sub_file_from_auto_subs(real_sub_file_path, auto_sub_file_path, out_sub_path)

    print("Done")