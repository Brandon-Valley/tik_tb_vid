import os
from pathlib import Path
from sms.file_system_utils import file_system_utils as fsu
from YT_PL_DL_Data import YT_PL_DL_Data


WORKING_DIR_PATH = "C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS"

def main():

    # TODO download yt playlist with youtube_utils.dl_yt_playlist__fix_sub_times_convert_to__mp4_srt()

    yt_pl_dl_dir_path = os.path.join(WORKING_DIR_PATH, "Family_Guy___TBS")
    yt_pl_dl_dir_data = YT_PL_DL_Data(yt_pl_dl_dir_path)


    print("Done")


if __name__ == "__main__":
    import os.path as path
    print(f"Running " , path.abspath(__file__) , '...')
    main()
    print("End of Main") 