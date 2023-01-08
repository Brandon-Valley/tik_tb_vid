

from fuzzywuzzy import fuzz
from Series_Sub_Map import Series_Sub_map
from sms.file_system_utils import file_system_utils as fsu
from sms.logger import txt_logger
import pysubs2

FUZZ_STR_DELIM = " "

def _sub_path_to_fuzz_str(sub_path):
    # subs = pysubs2.load(sub_path, encoding="utf-8")
    subs = pysubs2.load(sub_path, encoding="latin1")

    subs_fuzz_str = ""
    for line in subs:
        subs_fuzz_str = subs_fuzz_str + line.text + FUZZ_STR_DELIM

    # subs_fuzz_str = subs_fuzz_str.replace("\\N", " ")
    # subs_fuzz_str = subs_fuzz_str.replace("\'", " ")
    # return subs_fuzz_str.lower()
    return subs_fuzz_str

def get_real_episode_sub_data_from_auto_sub(auto_sub_path, ssm, lang):
    print(f"in get_real_episode_sub_data_from_auto_sub() - {auto_sub_path=}")
    print(f"{ssm.get_num_episodes_in_lang(lang)=}")

    auto_sub_fuzz_str = _sub_path_to_fuzz_str(auto_sub_path)

    lang_ep_sub_data_l = ssm.get_episode_sub_data_l_for_lang(lang)

    print(f"{len(lang_ep_sub_data_l)=}")

    best_fuzz_ratio = 0
    best_lang_ep_sub_data_obj = None

    for lang_ep_sub_data in lang_ep_sub_data_l:
        print(f"  Checking {lang_ep_sub_data.get_season_episode_str()}...")
        real_sub_path = lang_ep_sub_data.main_sub_file_path
        real_sub_fuzz_str = _sub_path_to_fuzz_str(real_sub_path)

        print(f"{auto_sub_fuzz_str=}")
        print(f"{real_sub_fuzz_str=}")
        # fuzz_ratio = fuzz.ratio(auto_sub_fuzz_str, real_sub_fuzz_str)
        fuzz_ratio = fuzz.ratio(auto_sub_fuzz_str, real_sub_fuzz_str)

        if fuzz_ratio > best_fuzz_ratio:
            print(f"New best_lang_ep_sub_data_obj found: {lang_ep_sub_data}")
            best_fuzz_ratio = fuzz_ratio
            best_lang_ep_sub_data_obj = lang_ep_sub_data
    
    print(f"Final {best_fuzz_ratio=}, {best_lang_ep_sub_data_obj}")


if __name__ == "__main__":
    import os.path as path
    print("Running " , path.abspath(__file__) , '...')

    test_srt_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.en.srt"

    lang = "en"
    # in_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en"
    in_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_test_pilot"
    ssm = Series_Sub_map()
    ssm.load_lang(in_dir_path, lang)
    print(f"{ssm.get_num_episodes_in_lang(lang)=}")

    get_real_episode_sub_data_from_auto_sub(test_srt_path, ssm, lang)

    print("End of Main") 


