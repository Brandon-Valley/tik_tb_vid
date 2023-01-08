from sms.file_system_utils import file_system_utils as fsu
from pathlib import Path


class Episode_Sub_Data:
    extra_metadata = None

    def __init__(self, episode_subs_dir_path, season_num, episode_num, load_method_str = "many_of_one_lang"):
        self.episode_subs_dir_path = episode_subs_dir_path
        self.season_num = season_num
        self.episode_num = episode_num
        self.load_method_str = load_method_str

        if load_method_str == "many_of_one_lang":
            self._load_dir__many_of_one_lang()
        else:
            raise Exception(f"ERROR: unknown {load_method_str=}")

    def _load_dir__many_of_one_lang(self):
        print("in _load_dir__many_of_one_lang()")
        # exit()
class Series_Sub_map():
    ep_sub_data_ld = {}


    def __init__(self):
        print("in init")
        pass

    def _load_lang__open_sub_lang_by_season_fg(self, in_dir_path, lang ):
        print("in _load_lang__open_sub_lang_by_season_fg()")

        self.ep_sub_data_ld[lang] = []

        lang_season_dir_path_l = fsu.get_dir_content_l(in_dir_path, "dir")
        # print(f"{lang_season_dir_path_l=}")

        for lang_season_dir_path in lang_season_dir_path_l:
            # get season_num
            season_dir_name = Path(lang_season_dir_path).stem
            # print(f"{season_dir_name=}")
            season_num = int(season_dir_name.split("s")[1])
            print(f"{season_num=}")

            ep_dir_path_l = fsu.get_dir_content_l(lang_season_dir_path, "dir")
            for ep_dir_path in ep_dir_path_l:
                
                ep_num = int(Path(ep_dir_path).stem.split("episode ")[1])
                print(f"{ep_num=}")

                ep_sub_data = Episode_Sub_Data(episode_subs_dir_path = ep_dir_path,
                                               season_num = season_num,
                                               episode_num = ep_num,
                                               load_method_str = "many_of_one_lang")





    def load_lang(self, in_dir_path, lang, load_style_str = "open_sub_lang_by_season_fg"):

        if load_style_str == "open_sub_lang_by_season_fg":
            self._load_lang__open_sub_lang_by_season_fg(in_dir_path, lang)
        else:
            raise Exception(f"ERROR: unknown {load_style_str=}")

if __name__ == "__main__":
    import os.path as path
    print("Running ",  path.abspath(__file__),  '...')

    lang = "en"
    in_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en"

    ssm = Series_Sub_map()
    ssm.load_lang(in_dir_path, lang)
    print("End of Main")