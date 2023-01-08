

from Series_Sub_Map import Series_Sub_map


def get_real_episode_sub_data_from_auto_sub(auto_sub_path, ssm):
    print(auto_sub_path)


if __name__ == "__main__":
    import os.path as path
    print("Running " , path.abspath(__file__) , '...')

    test_srt_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/test/sub_match/Family_Guy__Back_To_The_Pilot_(Clip)___TBS/Family_Guy__Back_To_The_Pilot_(Clip)___TBS.en.srt"

    lang = "en"
    in_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en"
    ssm = Series_Sub_map()
    ssm.load_lang(in_dir_path, lang)

    get_real_episode_sub_data_from_auto_sub(test_srt_path, ssm)

    print("End of Main") 


