from pprint import pprint
import fuzz_common
import os
from sms.file_system_utils import file_system_utils as fsu
from sms.logger import json_logger
# from sms.logger import txt
from pathlib import Path
import pysubs2
import subtitle_utils as su

class Episode_Sub_Data:
    extra_metadata_d = {}
    sub_file_path_l = []
    main_sub_file_path = None
    series_name_match_str_set = set()
    partial_fuzz_str_l = []

    def __init__(self, episode_subs_dir_path, season_num, episode_num, lang = None, series_name = "Family Guy", load_method_str = "many_of_one_lang"):
        self.episode_subs_dir_path = episode_subs_dir_path
        self.season_num = season_num
        self.episode_num = episode_num
        self.load_method_str = load_method_str
        self.lang = lang
        self.series_name = series_name

        self._set_series_name_match_l()

        if load_method_str == "many_of_one_lang":
            self.sub_file_path_l = fsu.get_dir_content_l(self.episode_subs_dir_path, "file")
            self.main_sub_file_path = self._get_main_sub_file_path()

            print(f"{self.get_season_episode_str()} - Getting main_sub_fuzz_str from main_sub_path...")
            self.main_sub_fuzz_str = fuzz_common.get_fuzz_str_from_sub_path(self.main_sub_file_path)

            print(f"{self.get_season_episode_str()} - Getting main_sub_fuzz_str_len...")
            self.main_sub_fuzz_str_len = len(self.main_sub_fuzz_str)
            # self._load_dir__many_of_one_lang()
        else:
            raise Exception(f"ERROR: unknown {load_method_str=}")

    # def _get_num_char_in_main_sub_file(self):
    #     num_char = 0
    #     subs = pysubs2.load(self.main_sub_file_path, encoding="latin1")
    #     for line in subs:
    #         num_char += len(line.text)
    #     return num_char

    # LATER save inicies if takes too much mem
    def _set_partial_fuzz_str_l(self, min_partial_fuzz_str_len):
        # self.partial_fuzz_str_l = fuzz_common.get_partial_fuzz_str_l_from_total_fuzz_str(self.main_sub_fuzz_str, min_partial_fuzz_str_len)
        self.partial_fuzz_str_l = fuzz_common.get_partial_fuzz_str_l_from_total_fuzz_str(self.main_sub_fuzz_str, min_partial_fuzz_str_len)
        print(f"{self.partial_fuzz_str_l=}")
        pass

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

        remaining_sub_file_path_l = []

        for sub_file_path in self.sub_file_path_l:

            # Delete anything that isn't a readable .srt file (no MicroDVD files allowed)
            # print(f"{sub_file_path=}")
            if not su.sub_file_readable_srt(sub_file_path):
                print(f"Cleaning - Deleting sub file b/c it is not readable .srt file: {sub_file_path}...")
                fsu.delete_if_exists(sub_file_path)
                continue

            # Delete any sub files that aren't the correct lang
            # print(f"  Checking {sub_file_path}...")
            if not su.sub_file_is_correct_lang(sub_file_path, self.lang):
                print(f"Cleaning - Deleting sub file b/c it is the wrong lang: {sub_file_path}...")
                fsu.delete_if_exists(sub_file_path)
                continue

            # # LATER if too slow, try using list method?
            # # Remove advertising from subs
            # su.remove_advertising_from_sub_file(sub_file_path)
            
            remaining_sub_file_path_l.append(sub_file_path)

        # Remove advertising from subs
        print(f"Cleaning - Removing advertising from all remaining sub files for {self.get_season_episode_str()}...")
        su.remove_advertising_from_sub_file_path_l(remaining_sub_file_path_l)
        
        # Do not allow any empty dirs (may have been created by deleting wrong-lang-subs)
        if len(fsu.get_dir_content_l(self.episode_subs_dir_path, "all")) == 0:
            print(f"Cleaning - Deleting episode_subs_dir_path b/c empty after deleting bad subs: {self.episode_subs_dir_path}...")
            fsu.delete_if_exists(self.episode_subs_dir_path)

        # # TODO REMOVE, vv just temp for  fist big en clean test to see if ^^ breaks anything
        # su.sub_file_readable_srt(sub_file_path)


    def _get_main_sub_file_path(self):
        print(f"{self.get_season_episode_str()} - Getting main_sub_file_path...")

        # def _get_num_lines_in_file(file_path):
        #     # return sum(1 for i in open(file_path, 'rb'))
        #     # return 1
        #     return os.path.getsize(file_path)

        def _file_name_contains_series_name(file_path):
            for series_name_match_str in self.series_name_match_str_set:
                if Path(file_path).name.__contains__(series_name_match_str):
                    return True
            return False

        # sub_file_path_l_most_lines_first = self.sub_file_path_l.sort(key=_get_num_lines_in_file, reverse=True)
        # sub_file_path_l_most_lines_first = sorted(self.sub_file_path_l,key=_get_num_lines_in_file, reverse=True)

        # Default to picking sub with largest file size
        #  - # lines might be better but file size is WAY faster
        sub_file_path_l_most_lines_first = sorted(self.sub_file_path_l,key=os.path.getsize, reverse=True)

        # If any files exist with series name in file name, pick largest file
        # - Don't want to be fooled by subs for wrong show getting mixed-in
        for sub_file_path in sub_file_path_l_most_lines_first:
            if _file_name_contains_series_name(sub_file_path):
                return sub_file_path
                # self.main_sub_file_path = sub_file_path
                # return

        # If no files exist with series name in file name, just pick largest file
        if len(sub_file_path_l_most_lines_first) > 0:
            # self.main_sub_file_path = sub_file_path
            # return
            return sub_file_path_l_most_lines_first[0]

        return None

        # # If any files exist with series name in file name, pick file with most lines
        # for sub_file_path in list(sfp for sfp in self.sub_file_path_l if _file_name_contains_series_name(sfp)).sort(key=_get_num_lines_in_file, reverse=True):
        #     self.main_sub_file_path =sub_file_path
        #     return

        # # If no files exist with series name in file name:

        # # # If any files exist with series name in file name
        # # for sub_file_path in self.sub_file_path_l:
        # #     # if f".{self.lang}.srt" in Path(sub_file_path).stem and _file_name_contains_series_name(sub_file_path):
        # #     if f".{self.lang}.srt" in Path(sub_file_path).name and _file_name_contains_series_name(sub_file_path):
        # #         self.main_sub_file_path = sub_file_path
        # #         return

        # # If none of above exist, pick file with series name in file name
        # for sub_file_path in self.sub_file_path_l:
        #     if _file_name_contains_series_name(sub_file_path):
        #         self.main_sub_file_path = sub_file_path
        #         return

        # # If none of above exist, pick file with .en.srt
        # for sub_file_path in self.sub_file_path_l:
        #     # if f".{self.lang}.srt" in Path(sub_file_path).stem:
        #     if f".{self.lang}.srt" in Path(sub_file_path).name:
        #         self.main_sub_file_path = sub_file_path
        #         return

        # # # If none of above exist, just return the first sub with a match in self.series_name_match_str_set
        # # for sub_file_path in self.sub_file_path_l:
        # #     for series_name_match_str in self.series_name_match_str_set:
        # #         if Path(sub_file_path).name.__contains__(series_name_match_str):
        # #             self.main_sub_file_path = sub_file_path
        # #             return
        
        # # If none of above exist, just return the first valid sub_path in list
        # for sub_file_path in self.sub_file_path_l:
        #     self.main_sub_file_path = sub_file_path
        #     return


    def _set_series_name_match_l(self):
        self.series_name_match_str_set.add(self.series_name)
        self.series_name_match_str_set.add(self.series_name.replace(" ", "."))
        self.series_name_match_str_set.add(self.series_name.replace(" ", "_"))
        self.series_name_match_str_set.add(self.series_name.replace(" ", "-"))
        self.series_name_match_str_set.add(self.series_name.replace("_", " "))
        self.series_name_match_str_set.add(self.series_name.replace("_", "."))
        self.series_name_match_str_set.add(self.series_name.replace("_", "-"))
        self.series_name_match_str_set.add(self.series_name.replace(".", "-"))
        self.series_name_match_str_set.add(self.series_name.replace(".", " "))
        self.series_name_match_str_set.add(self.series_name.replace(".", "_"))
        self.series_name_match_str_set.add(self.series_name.replace("-", " "))
        self.series_name_match_str_set.add(self.series_name.replace("-", "."))
        self.series_name_match_str_set.add(self.series_name.replace("-", "_"))


    # def _load_dir__many_of_one_lang(self):
        
    #     self.sub_file_path_l = fsu.get_dir_content_l(self.episode_subs_dir_path, "file")
    #     # extra_metadata_d = []
    #     self.main_sub_file_path = self._get_main_sub_file_path()
    #     # print(f"Picked main sub file for episode {self.get_season_episode_str()}: {self.main_sub_file_path=}")


    def get_num_sub_files(self):
        return len(self.sub_file_path_l)

    def __repr__(self):
        rs = f"EpSubData: S{self.season_num}E{self.episode_num}, {self.get_num_sub_files()} Subs, Main: {self.main_sub_file_path}"
        return rs



class Series_Sub_map():
    ep_sub_data_ld = {}
    lang_min_max_fuzz_str_len_ep_sub_data_d = {}

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
        # print(f"{out_json_d=}")
        # print(f"{out_json_path=}")
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


    def _load_lang__open_sub_lang_by_season_fg(self, in_dir_path, lang, series_name):
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
                                               series_name = series_name,
                                               load_method_str = "many_of_one_lang")
                # print(ep_sub_data)
                self.ep_sub_data_ld[lang].append(ep_sub_data)
        print(f"Done Loading {lang=}")




    def load_lang(self, in_dir_path, lang, series_name = "Family Guy", load_style_str = "open_sub_lang_by_season_fg"):

        if load_style_str == "open_sub_lang_by_season_fg":
            self._load_lang__open_sub_lang_by_season_fg(in_dir_path, lang, series_name)
        else:
            raise Exception(f"ERROR: unknown {load_style_str=}")

        self.set_lang_min_max_fuzz_str_len_ep_sub_data_d_for_lang(lang)

        min_fuzz_str_len = self.get_min_fuzz_str_len_for_lang(lang)

        for ep_sub_data in self.ep_sub_data_ld[lang]:
            ep_sub_data._set_partial_fuzz_str_l(min_fuzz_str_len)

    def get_min_fuzz_str_len_for_lang(self, lang):
        return self.lang_min_max_fuzz_str_len_ep_sub_data_d[lang]["min"].main_sub_fuzz_str_len

    def get_max_fuzz_str_len_for_lang(self, lang):
        return self.lang_min_max_fuzz_str_len_ep_sub_data_d[lang]["max"].main_sub_fuzz_str_len

    def get_min_fuzz_str_len_ep_sub_data_lang(self, lang):
        return self.lang_min_max_fuzz_str_len_ep_sub_data_d[lang]["min"]

    def get_max_fuzz_str_len_ep_sub_data_lang(self, lang):
        return self.lang_min_max_fuzz_str_len_ep_sub_data_d[lang]["max"]


    def set_lang_min_max_fuzz_str_len_ep_sub_data_d_for_lang(self, lang):
        print("Getting min and max char lengths of main sub files...")

        # self.lang_min_max_fuzz_str_len_ep_sub_data_d[lang] = {
        #     "min" : None,
        #     "max" : None,
        #     "min_char_ep_sub_data": None,
        #     "max_char_ep_sub_data": None
        # }
        
        # min = None
        # max = None
        min_char_ep_sub_data = None
        max_char_ep_sub_data = None

        for ep_sub_data in self.ep_sub_data_ld[lang]:
            print(f"{ep_sub_data.get_season_episode_str()} - Getting min and max char lengths of main sub file...")
            # sub_path = ep_sub_data.main_sub_file_path
            # num_char = ep_sub_data._get_num_char_in_main_sub_file()
            num_char = ep_sub_data.main_sub_fuzz_str_len
            # print(f"{num_char=}")

            # init and if only 1 ep_sub_data
            if min_char_ep_sub_data == None:
                max_char_ep_sub_data = ep_sub_data
                min_char_ep_sub_data = ep_sub_data
                continue

            if num_char < min_char_ep_sub_data.main_sub_fuzz_str_len:
                print(f"  {ep_sub_data.get_season_episode_str()} - New min found: {num_char}")
                min_char_ep_sub_data = ep_sub_data
                continue

            if num_char > max_char_ep_sub_data.main_sub_fuzz_str_len:
                print(f"  {ep_sub_data.get_season_episode_str()} - New max found: {num_char}")
                max_char_ep_sub_data = ep_sub_data
                continue
        
        self.lang_min_max_fuzz_str_len_ep_sub_data_d[lang] = {"max": None,
                                                              "min": None}
        self.lang_min_max_fuzz_str_len_ep_sub_data_d[lang]["min"] = min_char_ep_sub_data
        self.lang_min_max_fuzz_str_len_ep_sub_data_d[lang]["max"] = max_char_ep_sub_data

        print("  Got min and max char lengths of main sub files:")
        # # print(f"{min=}")
        # # print(f"{max=}")
        # print(f"{min_char_ep_sub_data=}")
        # print(f"{max_char_ep_sub_data=}")

        # if min_char_ep_sub_data
        # pprint(self.lang_min_max_fuzz_str_len_ep_sub_data_d)
        print(f"    {self.get_min_fuzz_str_len_for_lang(lang)}")
        print(f"    {self.get_max_fuzz_str_len_for_lang(lang)}")
        print(f"    {self.get_min_fuzz_str_len_ep_sub_data_lang(lang)}")
        print(f"    {self.get_max_fuzz_str_len_ep_sub_data_lang(lang)}")



        # return min, max



    # def _get_min_and_max_episode_fuzz_str_len(self, lang):
    #     print("Getting min and max char lengths of main sub files...")

    #     min = None
    #     max = None
    #     min_char_ep_sub_data = None
    #     max_char_ep_sub_data = None

    #     for ep_sub_data in self.ep_sub_data_ld[lang]:
    #         print(f"Getting min and max char lengths of main sub files - Checking {ep_sub_data.get_season_episode_str()}")
    #         # sub_path = ep_sub_data.main_sub_file_path
    #         # num_char = ep_sub_data._get_num_char_in_main_sub_file()
    #         num_char = ep_sub_data.main_sub_fuzz_str_len

    #         # init and if only 1 ep_sub_data
    #         if min == None:
    #             max_char_ep_sub_data = ep_sub_data
    #             max = num_char
    #             min_char_ep_sub_data = ep_sub_data
    #             min = num_char
    #             continue

    #         if num_char < min:
    #             min_char_ep_sub_data = ep_sub_data
    #             min = num_char
    #             continue

    #         if num_char > max:
    #             max_char_ep_sub_data = ep_sub_data
    #             max = num_char
    #             continue

    #     print("Got min and max char lengths of main sub files:")
    #     print(f"{min=}")
    #     print(f"{max=}")
    #     print(f"{min_char_ep_sub_data=}")
    #     print(f"{max_char_ep_sub_data=}")

    #     return min, max






if __name__ == "__main__":
    import os.path as path
    print("Running ",  path.abspath(__file__),  '...')

    lang = "en"
    # in_dir_path = "C:/Users/Brandon/Documents/Personal_Projects/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en"
    in_dir_path = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en_s4_16_and_17"
    # in_dir_path = "C:/p/tik_tb_vid_big_data/ignore/subs/fg/og_bulk_sub_dl_by_season/en"

    ssm = Series_Sub_map()
    ssm.load_lang(in_dir_path, lang)
    # print(ssm.get_min_and_max_episode_fuzz_str_len(lang))
    ssm.write_log_json("C:/p/tik_tb_vid_big_data/ignore/BIG_BOY_fg_TBS/SSM_log.json")
    # print(f"{ssm.get_num_episodes_in_lang(lang)=}")
    # print(f"{ssm.get_episode_sub_data_l_for_lang(lang)=}")
    print("End of Main")