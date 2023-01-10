import os
from sms.file_system_utils import file_system_utils as fsu
from sms.logger import json_logger
from pathlib import Path
import pysubs2
import subtitle_utils as su

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

    def get_as_json_d(self):
        return {
            "season_episode_str" : self.get_season_episode_str(),
            "episode_subs_dir_path" : self.episode_subs_dir_path,
            "main_sub_file_path" : self.main_sub_file_path,
            "sub_file_path_l" : self.sub_file_path_l,
            "load_method_str" : self.load_method_str,
            "lang" : self.lang,
            "season_num" : self.season_num,
            "episode_num" : self.episode_num,
            "extra_metadata_d" : self.extra_metadata_d
            }

    def get_season_episode_str(self):
        str(1).zfill(2)
        return f"S{str(self.season_num).zfill(2)}E{str(self.episode_num).zfill(2)}"


    def clean_episode_subs_after_fresh_download(self):
        """
            Have gotten spanish subs not marked when dl mass english subs 
                - Run this once after dl b/c it takes a bit
                - Make new SSM after this
        """
        print(f"Cleaning {self.get_season_episode_str()}...")

        for sub_file_path in self.sub_file_path_l:

            # Delete anything that isn't a readable .srt file (no MicroDVD files allowed)
            if not su.sub_file_readable_srt(sub_file_path):
                print(f"Cleaning - Deleting sub file b/c it is not readable .srt file: {sub_file_path}...")
                fsu.delete_if_exists(sub_file_path)
                continue

            # Delete any sub files that aren't the correct lang
            print(f"  Checking {sub_file_path}...")
            if not su.sub_file_is_correct_lang(sub_file_path, self.lang):
                print(f"Cleaning - Deleting sub file b/c it is the wrong lang: {sub_file_path}...")
                fsu.delete_if_exists(sub_file_path)
                continue
        
        # Do not allow any empty dirs (may have been created by deleting wrong-lang-subs)
        if len(fsu.get_dir_content_l(self.episode_subs_dir_path, "all")) == 0:
            print(f"Cleaning - Deleting episode_subs_dir_path b/c empty after deleting bad subs: {self.episode_subs_dir_path}...")
            fsu.delete_if_exists(self.episode_subs_dir_path)


    def _pick_main_sub_file_path(self):
        # pick first .en.srt, pick first in list otherwise
        for sub_file_path in self.sub_file_path_l:
            # if f".{self.lang}.srt" in Path(sub_file_path).stem and su.sub_file_is_correct_lang(sub_file_path, self.lang):
            if f".{self.lang}.srt" in Path(sub_file_path).stem:
                self.main_sub_file_path = sub_file_path
                return
        
        # If none of above exist, just return the first valid sub_path in list
        for sub_file_path in self.sub_file_path_l:
            # if su.sub_file_is_correct_lang(sub_file_path, self.lang):
            self.main_sub_file_path = sub_file_path
            return

        # # If the only subtitles available are the wrong lang, just take the first wrong lang sub
        # if len(self.sub_file_path_l) > 0:
        #     self.main_sub_file_path = self.sub_file_path_l[0]
        #     return


    def _load_dir__many_of_one_lang(self):
        
        self.sub_file_path_l = fsu.get_dir_content_l(self.episode_subs_dir_path, "file")
        # extra_metadata_d = []
        self._pick_main_sub_file_path()
        # print(f"Picked main sub file for episode {self.get_season_episode_str()}: {self.main_sub_file_path=}")


    def get_num_sub_files(self):
        return len(self.sub_file_path_l)

    def __repr__(self):
        rs = f"EpSubData: S{self.season_num}E{self.episode_num}, {self.get_num_sub_files()} Subs, Main: {self.main_sub_file_path}"
        return rs



class Series_Sub_map():
    ep_sub_data_ld = {}

    def __init__(self):
        pass

    def get_num_episodes_in_lang(self, lang):
        return len(self.ep_sub_data_ld[lang])

    def get_episode_sub_data_l_for_lang(self, lang):
        return self.ep_sub_data_ld[lang]

    def write_log_json(self, out_json_path):
        out_json_d = {}
        for lang, ep_sub_data_l in self.ep_sub_data_ld.items():
            out_json_d[lang] = []
            for ep_sub_data in ep_sub_data_l:
                out_json_d[lang].append(ep_sub_data.get_as_json_d())
        print(f"{out_json_d=}")
        print(f"{out_json_path=}")
        json_logger.write(out_json_d, out_json_path)




    def clean_subs_after_fresh_download(self, lang = "ALL_LANGS"):
        """
            Have gotten spanish subs not marked when dl mass english subs 
                - Run this once after dl b/c it takes a bit
                - Make new SSM after this
        """
        def _clean_lang_ep_sub_data_l(lang):
            print(f"  Cleaning Lang: {lang}...")
            # ep_sub_data_l = self.ep_sub_data_ld[lang]
            # for ep_sub_data in ep_sub_data_l:
            for ep_sub_data in self.ep_sub_data_ld[lang]:
                ep_sub_data.clean_episode_subs_after_fresh_download()

        if lang == "ALL_LANGS":
            print("Cleaning all Langs...")
            for lang_key_str in self.ep_sub_data_ld.keys():
                _clean_lang_ep_sub_data_l(lang_key_str)
        else:
            _clean_lang_ep_sub_data_l(lang)









    def _load_lang__open_sub_lang_by_season_fg(self, in_dir_path, lang ):
        print(f"Loading {lang=} into Series_Sub_Map from: {in_dir_path}...")

        self.ep_sub_data_ld[lang] = []

        lang_season_dir_path_l = fsu.get_dir_content_l(in_dir_path, "dir")

        for lang_season_dir_path in lang_season_dir_path_l:
            # get season_num
            season_dir_name = Path(lang_season_dir_path).stem
            season_num = int(season_dir_name.split("s")[1])

            ep_dir_path_l = fsu.get_dir_content_l(lang_season_dir_path, "dir")
            for ep_dir_path in ep_dir_path_l:
                
                ep_num = int(Path(ep_dir_path).stem.split("episode ")[1])

                ep_sub_data = Episode_Sub_Data(episode_subs_dir_path = ep_dir_path,
                                               season_num = season_num,
                                               episode_num = ep_num,
                                               lang = lang,
                                               load_method_str = "many_of_one_lang")
                # print(ep_sub_data)
                self.ep_sub_data_ld[lang].append(ep_sub_data)
        print(f"Done Loading {lang=}")


    def load_lang(self, in_dir_path, lang, load_style_str = "open_sub_lang_by_season_fg"):

        if load_style_str == "open_sub_lang_by_season_fg":
            self._load_lang__open_sub_lang_by_season_fg(in_dir_path, lang)
        else:
            raise Exception(f"ERROR: unknown {load_style_str=}")



if __name__ == "__main__":
    import os.path as path
    print("Running ",  path.abspath(__file__),  '...')

    lang = "en"
    # in_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en"
    # in_dir_path = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s4_16_and_17"
    in_dir_path = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en"

    ssm = Series_Sub_map()
    ssm.load_lang(in_dir_path, lang)
    ssm.write_log_json("C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/SSM_log.json")
    print(f"{ssm.get_num_episodes_in_lang(lang)=}")
    # print(f"{ssm.get_episode_sub_data_l_for_lang(lang)=}")
    print("End of Main")