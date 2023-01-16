from pprint import pprint
import fuzz_common as fc
import os
from pathlib import Path

import re
import time

from fuzzywuzzy import fuzz
from Series_Sub_Map import Series_Sub_map
from sms.file_system_utils import file_system_utils as fsu
from sms.logger import txt_logger
from sms.logger import json_logger
import pysubs2

FUZZ_STR_DELIM = "\r"

# LATER Could make things more efficient if found truly idea values for these
NUM_TIMES_BIGGER_MIN_FUZZ_LEN_CAN_BE_FOR_INIT_PARTIAL_FUZZ_SEARCH_METHOD = 9 # Can change, picked this from lazy manual testing,
MIN_TIMES_BIGGER_MIN_FUZZ_LEN_CAN_BE_UNTIL_GIVE_UP = 4 # Can change, picked this from lazy manual testing

SEARCH_METHOD_KEY__INIT_PARTIAL_FUZZ = "init_partial_fuzz_search_method"
SEARCH_METHOD_KEY__AUTO_SUB_FUZZ_LEN_BASED = "auto_sub_fuzz_len_based"

EVAL_KEY__SUCCESS = "EVAL_KEY__SUCCESS"
EVAL_KEY__NO_CLEAR_WINNER = "EVAL_KEY__NO_CLEAR_WINNER"
EVAL_KEY__ALL_FR_SAME = "EVAL_KEY__ALL_FR_SAME"

CLIPS_DATA_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/CLIPS_DATA/"


def _get_best_ep_sub_partial_fuzz_ratio(ep_sub_data, auto_sub_fuzz_str, method_key, partial_fuzz_str_len=None):
    best_fuzz_ratio = 0
    best_real_sub_partial_fuzz_str = None

    # get partial_fuzz_str_l based on method_key
    if method_key == SEARCH_METHOD_KEY__INIT_PARTIAL_FUZZ:
        partial_fuzz_str_l = ep_sub_data.get_default_partial_fuzz_str_l()
    elif method_key == SEARCH_METHOD_KEY__AUTO_SUB_FUZZ_LEN_BASED:
        ep_sub_total_fuzz_str = json_logger.read(ep_sub_data.total_fuzz_str_json_path)
        print(f"{len(ep_sub_total_fuzz_str)=}")
        print(f"{partial_fuzz_str_len=}")
        print(f"{len(auto_sub_fuzz_str)=}")
        partial_fuzz_str_l = fc.get_partial_fuzz_str_l_from_total_fuzz_str(total_fuzz_str = ep_sub_total_fuzz_str,
                                                                                    min_partial_fuzz_str_num_char = partial_fuzz_str_len,
                                                                                    min_overlap_char = len(auto_sub_fuzz_str))
        print(f"{len(partial_fuzz_str_l)=}")

    print(f"{len(partial_fuzz_str_l)=}")

    for real_sub_partial_fuzz_str in partial_fuzz_str_l:

        fuzz_ratio = fuzz.ratio(auto_sub_fuzz_str, real_sub_partial_fuzz_str)

        if fuzz_ratio > best_fuzz_ratio:
            best_fuzz_ratio = fuzz_ratio
            best_real_sub_partial_fuzz_str = real_sub_partial_fuzz_str

    return best_fuzz_ratio, best_real_sub_partial_fuzz_str


def _write_fuzz_ratio_ep_sub_data_l_d_to_json(fuzz_ratio_ep_sub_data_l_d, json_path):
    # LATER need to init here b/c not deleting CLIPS_DATA ever, should fix this
    fsu.delete_if_exists(json_path)
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)

    json_ser_d = {}
    for fuzz_ratio, ep_sub_data_l in fuzz_ratio_ep_sub_data_l_d.items():
        json_ser_d[fuzz_ratio] = []
        for ep_sub_data in ep_sub_data_l:
            json_ser_d[fuzz_ratio].append(str(ep_sub_data))
    print(f"Writing serializable fuzz_ratio_ep_sub_data_l_d to {json_path=}...")
    json_logger.write(json_ser_d, json_path)


def _get_fuzz_ratio_ep_sub_data_l_d(auto_sub_fuzz_str, ssm, lang, method_key, partial_fuzz_str_len = None):
    """
        For the given auto_sub_fuzz_str, go through every episode (in ssm), get fuzz_ratio, make dict of all these
        fuzz_ratios as keys w/ value == list of all ep_sub_data objects that returned that fuzz ratio
          - This fuzz_ratio_ep_sub_data_l_d will be evaluated to find next step/best-match/etc.
    """
    ep_sub_data_l = ssm.get_episode_sub_data_l_for_lang(lang)

    print(f"{len(ep_sub_data_l)=}")

    fuzz_ratio_ep_sub_data_l_d = {}

    for ep_sub_data in ep_sub_data_l:
        print(f"  Checking {ep_sub_data.get_season_episode_str()}...")

        ep_sub_fuzz_ratio, ep_sub_best_partial_fuzz_str = _get_best_ep_sub_partial_fuzz_ratio(ep_sub_data, auto_sub_fuzz_str, method_key, partial_fuzz_str_len)

        if ep_sub_fuzz_ratio in fuzz_ratio_ep_sub_data_l_d.keys():
            fuzz_ratio_ep_sub_data_l_d[ep_sub_fuzz_ratio].append(ep_sub_data)
        else:
            fuzz_ratio_ep_sub_data_l_d[ep_sub_fuzz_ratio] = [ep_sub_data]
    return fuzz_ratio_ep_sub_data_l_d


def get_eval_of__fuzz_ratio_ep_sub_data_l_d(fuzz_ratio_ep_sub_data_l_d, ssm, lang, fuzz_ratio_ep_sub_data_l_d_json_path):
    """ Evaluate fuzz_ratio_ep_sub_data_l_d, set EVAL_KEY based on fuzz_ratio_ep_sub_data_l_d"""

    if len(fuzz_ratio_ep_sub_data_l_d.keys()) == 0:
        raise Exception(f"ERROR, {fuzz_ratio_ep_sub_data_l_d=}, no clue how this happened")

    # If all episode's real sub's partial_fuzz_strs' gave same fuzz ratio
    #   - Try diff search method
    if len(fuzz_ratio_ep_sub_data_l_d.keys()) == 1 and ssm.get_num_episodes_in_lang(lang) != 1:
        return None, None, EVAL_KEY__ALL_FR_SAME

    max_fuzz_ratio = max(fuzz_ratio_ep_sub_data_l_d.keys())
    max_fuzz_ratio_ep_sub_data_l = fuzz_ratio_ep_sub_data_l_d[max_fuzz_ratio]

    # Success
    if len(max_fuzz_ratio_ep_sub_data_l) == 1:
        best_fuzz_ratio_ep_sub_data = max_fuzz_ratio_ep_sub_data_l[0]
        print(f"Success - Single ep_sub_data for highest {max_fuzz_ratio=} - {best_fuzz_ratio_ep_sub_data.get_season_episode_str()}, returning...")
        return max_fuzz_ratio, best_fuzz_ratio_ep_sub_data, EVAL_KEY__SUCCESS

    # If all episode's real sub's partial_fuzz_strs' DID NOT give same fuzz ratio, but also no clear winner
    else:
        return None, None, EVAL_KEY__NO_CLEAR_WINNER


def _search_and_log(clip_dir_data, auto_sub_fuzz_str, ssm, lang, method_key, partial_fuzz_str_len = None):

    fuzz_ratio_ep_sub_data_l_d_json_path = os.path.join(clip_dir_data.data_dir_path, f"fuzz_ratio_ep_sub_data_l_d.json")

    print(f"Getting fuzz_ratio_ep_sub_data_l_d for {clip_dir_data.auto_sub_path=}...")
    fuzz_ratio_ep_sub_data_l_d = _get_fuzz_ratio_ep_sub_data_l_d(auto_sub_fuzz_str, ssm, lang, method_key, partial_fuzz_str_len)
    _write_fuzz_ratio_ep_sub_data_l_d_to_json(fuzz_ratio_ep_sub_data_l_d, fuzz_ratio_ep_sub_data_l_d_json_path)
    fuzz_ratio, ep_sub_data, eval_str = get_eval_of__fuzz_ratio_ep_sub_data_l_d(fuzz_ratio_ep_sub_data_l_d, ssm, lang, fuzz_ratio_ep_sub_data_l_d_json_path)

    return fuzz_ratio, ep_sub_data, eval_str, fuzz_ratio_ep_sub_data_l_d



def _predict_search_method(auto_sub_fuzz_str, ssm, lang):
    print("in _predict_search_method()")
    min_fuzz_str_len = ssm.get_min_fuzz_str_len_for_lang(lang)

    min_fuzz_len_to_auto_sub_fuzz_len_ratio = min_fuzz_str_len / len(auto_sub_fuzz_str)

    if min_fuzz_len_to_auto_sub_fuzz_len_ratio < NUM_TIMES_BIGGER_MIN_FUZZ_LEN_CAN_BE_FOR_INIT_PARTIAL_FUZZ_SEARCH_METHOD:
        return SEARCH_METHOD_KEY__INIT_PARTIAL_FUZZ
    else:
        return SEARCH_METHOD_KEY__AUTO_SUB_FUZZ_LEN_BASED



def get_real_episode_sub_data_from_auto_sub(clip_dir_data, ssm, lang):
    print(f"Searching for best real sub file from auto sub file:{clip_dir_data.auto_sub_path}...")
    start_time = time.time()
    print(f"in get_real_episode_sub_data_from_auto_sub() - {clip_dir_data.auto_sub_path=}")
    print(f"{ssm.get_num_episodes_in_lang(lang)=}")

    auto_sub_fuzz_str = clip_dir_data.get_auto_sub_fuzz_str()

    # Try to predict method that will find match fastest
    # LATER for SEARCH_METHOD_KEY__AUTO_SUB_FUZZ_LEN_BASED, make it also give partial_fuzz_str_len
    search_method_key = _predict_search_method(auto_sub_fuzz_str, ssm, lang)
    print(f"init predicted {search_method_key=}")

    # Default - Use the largest possible equal partial_fuzz_strs created for each episode during SSM.load_lang()
    if search_method_key == SEARCH_METHOD_KEY__INIT_PARTIAL_FUZZ:
        fuzz_ratio, ep_sub_data, eval_key, fuzz_ratio_ep_sub_data_l_d = _search_and_log(clip_dir_data,auto_sub_fuzz_str, ssm, lang,
                                                                                        method_key = SEARCH_METHOD_KEY__INIT_PARTIAL_FUZZ,
                                                                                        partial_fuzz_str_len = None)
        print(f"{fuzz_ratio=}")
        print(f"{ep_sub_data=}")
        print(f"{eval_key=}")

        # Evaluate results of search
        if eval_key == EVAL_KEY__SUCCESS:
            total_time = time.time() - start_time
            return fuzz_ratio, ep_sub_data, eval_key, total_time
        # LATER SHOULD ADD SOMETHING HERE FOR EVAL_KEY__NO_CLEAR_WINNER - like if its just down to 2 subs
        elif eval_key == EVAL_KEY__NO_CLEAR_WINNER:
            print(f"Init predicted {search_method_key=} was wrong, made it through every ep without finding clear winner, changing search_method_key to try len based...")
            search_method_key = SEARCH_METHOD_KEY__AUTO_SUB_FUZZ_LEN_BASED
        else:
            print(f"Init predicted {search_method_key=} was wrong, made it through every ep without success, changing search_method_key to try len based...")
            search_method_key = SEARCH_METHOD_KEY__AUTO_SUB_FUZZ_LEN_BASED

    # For ^^ fails and shorter clips/auto_subs, chop up episode's total fuzz str into custom smaller chunks based on
    # (fuzz_str_len) num auto_sub chars, start with standard # times bigger than auto_sub's fuzz_str to chop things up
    # with, if fail, keep reducing this until success or until chop sizes hit a constant min size and give up
    if search_method_key == SEARCH_METHOD_KEY__AUTO_SUB_FUZZ_LEN_BASED:

        init_partial_fuzz_str_len = len(auto_sub_fuzz_str) * NUM_TIMES_BIGGER_MIN_FUZZ_LEN_CAN_BE_FOR_INIT_PARTIAL_FUZZ_SEARCH_METHOD

        # for if got here from failed SEARCH_METHOD_KEY__INIT_PARTIAL_FUZZ and auto_sub_fuzz_str is very large
        if ssm.get_min_fuzz_str_len_for_lang(lang) < init_partial_fuzz_str_len:
            partial_fuzz_str_len = len(auto_sub_fuzz_str)
        else:
            partial_fuzz_str_len = init_partial_fuzz_str_len
        print(f"{partial_fuzz_str_len=}")

        # keep reducing partial_fuzz_str_len until success or until chop sizes hit a constant min size and give up
        while (partial_fuzz_str_len >= len(auto_sub_fuzz_str) * MIN_TIMES_BIGGER_MIN_FUZZ_LEN_CAN_BE_UNTIL_GIVE_UP):
            if ssm.get_min_fuzz_str_len_for_lang(lang) < partial_fuzz_str_len:
                raise Exception(f"ERROR: {ssm.get_min_fuzz_str_len_for_lang(lang)=} (from episode sub {ssm.get_min_fuzz_str_len_ep_sub_data_lang(lang)}) can never be less than {partial_fuzz_str_len=}")

            fuzz_ratio, ep_sub_data, eval_key, fuzz_ratio_ep_sub_data_l_d = _search_and_log(clip_dir_data, auto_sub_fuzz_str, ssm, lang,
                                                                                            method_key = SEARCH_METHOD_KEY__AUTO_SUB_FUZZ_LEN_BASED,
                                                                                            partial_fuzz_str_len = partial_fuzz_str_len)
            print(f"{fuzz_ratio=}")
            print(f"{ep_sub_data=}")
            print(f"{eval_key=}")

            if eval_key == EVAL_KEY__SUCCESS:
                break
            else:
                partial_fuzz_str_len = int(partial_fuzz_str_len / 2)

        # Evaluate results of search
        if eval_key != EVAL_KEY__SUCCESS:
            print(f"After fuzzy-searching every episode's subs, did not find a match for auto-sub, returning None: {eval_key=}...")
        else:
            print(f"Found best real sub for auto-sub: {ep_sub_data}")

        total_time = time.time() - start_time
        return fuzz_ratio, ep_sub_data, eval_key, total_time

    raise Exception(f"SHOULD NEVER GET HERE - {search_method_key=}, {partial_fuzz_str_len=}")



if __name__ == "__main__":
    import os.path as path
    print("Running " , path.abspath(__file__) , '...')

    # test_srt_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.en.srt"

    # lang = "en"
    # in_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en"
    # # in_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_test_pilot"
    # # in_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_test_s10_and_11"
    # ssm = Series_Sub_map()
    # ssm.load_lang(in_dir_path, lang)
    # print(f"{ssm.get_num_episodes_in_lang(lang)=}")

    # get_real_episode_sub_data_from_auto_sub(test_srt_path, ssm, lang)

    import get_init_mkvs_for_manual_edits
    get_init_mkvs_for_manual_edits.main()
    print("End of Main")


