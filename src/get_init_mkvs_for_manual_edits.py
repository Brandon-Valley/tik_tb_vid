import os
from pathlib import Path
from sms.file_system_utils import file_system_utils as fsu
from YT_PL_DL_Data import YT_PL_DL_Data
from get_real_episode_sub_data_from_auto_sub import get_real_episode_sub_data_from_auto_sub
from Series_Sub_Map import Series_Sub_map


WORKING_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS"
SERIES_SUB_EN_DIR_PATH = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en"
LANG = "en"

def main():

    # TODO download yt playlist with youtube_utils.dl_yt_playlist__fix_sub_times_convert_to__mp4_srt()
    # Init std subtitles for whole series data
    ssm = Series_Sub_map()
    ssm.load_lang(SERIES_SUB_EN_DIR_PATH, LANG)

    # Init std youtube playlist download data
    yt_pl_dl_dir_path = os.path.join(WORKING_DIR_PATH, "Family_Guy___TBS")
    yt_pl_dl_dir_data = YT_PL_DL_Data(yt_pl_dl_dir_path)


    fail_clip_dir_path_l = []

    for clip_dir_data in yt_pl_dl_dir_data.clip_dir_data_l:
        print(f"{clip_dir_data.clip_name=}")

        # get_real_episode_sub_data_from_auto_sub(auto_sub_path, ssm, lang)



    print("Done")


if __name__ == "__main__":
    import os.path as path
    print(f"Running " , path.abspath(__file__) , '...')
    main()
    print("End of Main") 