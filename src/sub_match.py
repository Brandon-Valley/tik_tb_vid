import pysubs2
from sms.file_system_utils import file_system_utils as fsu
from pathlib import Path

FUZZ_STR_DELIM = '`'

def _subs_to_subs_fuzz_str(in_subs):
    subs_fuzz_str = ""
    for line in in_subs:
        subs_fuzz_str = subs_fuzz_str + line.text + FUZZ_STR_DELIM
    return subs_fuzz_str

def trim_and_re_time_real_sub_file_from_auto_subs(real_sub_file_path, auto_sub_file_path, out_sub_path):

    fsu.delete_if_exists(out_sub_path)
    Path(out_sub_path).parent.mkdir(parents=True, exist_ok=True)

    # subs = pysubs2.load("my_subtitles.ass", encoding="utf-8")
    # subs = pysubs2.load(real_sub_file_path, encoding="utf-8")
    real_subs = pysubs2.load(real_sub_file_path, encoding="utf-8")
    auto_subs = pysubs2.load(auto_sub_file_path, encoding="utf-8")

    real_subs_fuzz_str = _subs_to_subs_fuzz_str(real_subs)
    auto_subs_fuzz_str = _subs_to_subs_fuzz_str(auto_subs)
    print(f"{real_subs_fuzz_str=}")
    print(f"{auto_subs_fuzz_str=}")

    # # subs.shift(s=2.5)
    # for line in subs:
    #     # line.text = "{\\be1}" + line.text
    #     print(f"{line.text=}")
    #     print(f"{line.start=}")
    #     print(f"{line.end=}")
    # subs.save(out_sub_path)



if __name__ == "__main__":
    real_sub_file_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/family.guy.s10.e05.back.to.the.pilot.(2011).eng.1cd.(4413506)/Family.Guy.S10E05.720p.WEB-DL.DD5.1.H.264-CtrlHD.srt"
    auto_sub_file_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.en.srt"
    out_sub_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS/out.en.srt"
    trim_and_re_time_real_sub_file_from_auto_subs(real_sub_file_path, auto_sub_file_path, out_sub_path)

    print("Done")