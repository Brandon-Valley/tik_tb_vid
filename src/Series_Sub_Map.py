from sms.file_system_utils import file_system_utils as fsu



class Episode_Sub_Data:
    def __init__(self):
        pass


class Series_Sub_map():
    ep_sub_data_l = []


    def __init__(self):
        print("in init")
        pass

    def _load_lang__open_sub_lang_by_season_fg(self,in_dir_path, lang ):
        print("in _load_lang__open_sub_lang_by_season_fg()")

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