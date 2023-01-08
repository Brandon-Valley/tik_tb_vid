import os
from sms.file_system_utils import file_system_utils as fsu
from pathlib import Path


class Episode_Sub_Data:
    extra_metadata_d = {}
    sub_file_path_l = []
    main_sub_file_path = None

    def __init__(self, episode_subs_dir_path, season_num, episode_num, lang = None, load_method_str = "many_of_one_lang"):
        self.episode_subs_dir_path = episode_subs_dir_path
        self.season_num = season_num
        self.episode_num = episode_num
        self.load_method_str = load_method_str
        self.lang = lang

        if load_method_str == "many_of_one_lang":
            self._load_dir__many_of_one_lang()
        else:
            raise Exception(f"ERROR: unknown {load_method_str=}")


    def _pick_main_sub_file_path(self):
        print("in _pick_main_sub_file_path()")

        # pick first .en.srt, pick first in list otherwise
        for sub_file_path in self.sub_file_path_l:
            if f".{self.lang}.srt" in Path(sub_file_path).stem:
                self.main_sub_file_path = sub_file_path
                return
        if len(self.sub_file_path_l) > 0:
            self.main_sub_file_path = self.sub_file_path_l[0]



    def _load_dir__many_of_one_lang(self):
        print("in _load_dir__many_of_one_lang()")
        
        self.sub_file_path_l = fsu.get_dir_content_l(self.episode_subs_dir_path, "file")
        # extra_metadata_d = []
        self._pick_main_sub_file_path()


    def get_num_sub_files(self):
        return len(self.sub_file_path_l)

    def __repr__(self):
        rs = f"EpSubData: S{self.season_num}E{self.episode_num}, {self.get_num_sub_files()} Subs, Main: {self.main_sub_file_path}"
        # print(rs)
        return rs



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
                                               lang = lang,
                                               load_method_str = "many_of_one_lang")
                print(ep_sub_data)





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