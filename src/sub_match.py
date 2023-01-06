import pysubs2


def trim_and_re_time_real_sub_file_from_auto_subs(real_sub_file_path, auto_sub_file_path):
    # subs = pysubs2.load("my_subtitles.ass", encoding="utf-8")
    # subs = pysubs2.load(real_sub_file_path, encoding="utf-8")
    subs = pysubs2.load(auto_sub_file_path, encoding="utf-8")
    # subs.shift(s=2.5)
    for line in subs:
        # line.text = "{\\be1}" + line.text
        print(f"{line.text=}")
    subs.save("my_subtitles_edited.ass")



if __name__ == "__main__":
    real_sub_file_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/family.guy.s10.e05.back.to.the.pilot.(2011).eng.1cd.(4413506)/Family.Guy.S10E05.720p.WEB-DL.DD5.1.H.264-CtrlHD.srt"
    auto_sub_file_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.en.srt"

    trim_and_re_time_real_sub_file_from_auto_subs(real_sub_file_path, auto_sub_file_path)

    print("Done")