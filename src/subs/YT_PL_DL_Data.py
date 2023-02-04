import os
from pathlib import Path

if __name__ == "__main__":
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).parent.parent))

import fuzz_common

from sms.file_system_utils import file_system_utils as fsu
from sms.logger import json_logger


class Clip_Dir_Data:
    mp4_path = False
    auto_sub_path = False
    fuzz_str_len = False

    def __init__(self, clip_dir_path, pl_data_dir_path):
        self.clip_dir_path = clip_dir_path
        self.clip_name = Path(clip_dir_path).name
        self.data_dir_path = os.path.join(pl_data_dir_path, self.clip_name)
        self.trim_re_time_working_dir_path = os.path.join(self.data_dir_path, "trim_re_time_wrk")
        self.fuzz_str_json_path = os.path.join(self.data_dir_path, "fuzz_str.json")

        fsu.delete_if_exists(self.data_dir_path)
        Path(self.data_dir_path).mkdir(parents=True, exist_ok=True)
        Path(self.trim_re_time_working_dir_path).mkdir(parents=True, exist_ok=True)

        self._set_mp4_and_auto_sub_paths()

        # print("end of init")


    def get_auto_sub_fuzz_str(self):
        return json_logger.read(self.fuzz_str_json_path)

    def write_auto_sub_fuzz_str_to_json_if_needed(self):
        if self.auto_sub_path != None:
            fuzz_str = fuzz_common.get_fuzz_str_from_sub_path(self.auto_sub_path)
            self.fuzz_str_len = len(fuzz_str)
            json_logger.write(fuzz_str, self.fuzz_str_json_path)


    def get_final_vid_sub_path(self, sub_path, sub_num):
        return os.path.join(self.data_dir_path, f"f{sub_num}_{Path(sub_path).name}")

    def has_subs(self):
        return not (self.auto_sub_path == None)

    def _set_mp4_and_auto_sub_paths(self):
        # clip_dir_path will pretty much always contain 1 .mp4 and 1 .srt, .mp4 is required, .srt optional, error if > 2 files in dir
        clip_dir_file_path_l = fsu.get_dir_content_l(self.clip_dir_path, "file")
        if len(clip_dir_file_path_l) > 2:
            raise Exception(f"ERROR: {len(clip_dir_file_path_l)} > 2, dir can contain 2 files at most (1 .srt and 1.mp4) {clip_dir_file_path_l=}")

        # No dirs allowed
        clip_dir_dir_path_l = fsu.get_dir_content_l(self.clip_dir_path, "dir")
        if len(clip_dir_dir_path_l) > 0:
            raise Exception(f"ERROR: {len(clip_dir_dir_path_l)} > 0, dir can contain no dirs")

        clip_mp4_path = os.path.join(self.clip_dir_path, self.clip_name + ".mp4")

        # .mp4 with same name required
        if not Path(clip_mp4_path).is_file():
            raise Exception(f"ERROR: {clip_mp4_path=} does not exist, {clip_dir_file_path_l=}")

        # Sub file not required, but will be .srt if exists, and is only other file allowed to exist in dir
        # However, .srt files can have different pre-suffixes like .en.srt, .en-orig.srt, .en-en.srt, etc.
        auto_sub_srt_path = None
        if len(clip_dir_file_path_l) == 2:
            sub_file_path_l = list(Path(self.clip_dir_path).glob("*.srt"))

            if len(sub_file_path_l) != 1:
                raise Exception(f"ERROR: {len(sub_file_path_l)=} != 1, if dir contains more than just 1 .mp4 file, that means it must contain 1 .srt file, 2 files in dir, but 0 .srt files found, {clip_dir_file_path_l=}")

            auto_sub_srt_path = sub_file_path_l[0]

        self.mp4_path = clip_mp4_path
        self.auto_sub_path = auto_sub_srt_path

        # print("all good",clip_dir_file_path_l)


class YT_PL_DL_Data:
    clip_dir_data_l = []
    def __init__(self, in_dir_path, pl_data_dir_path):
        self.pl_data_dir_path = pl_data_dir_path
        self.dir_path = in_dir_path

        fsu.delete_if_exists(pl_data_dir_path)
        Path(pl_data_dir_path).mkdir(parents=True, exist_ok=True)

        self.max_fuzz_str_len = 0

        clip_dir_path_l = fsu.get_dir_content_l(in_dir_path, "dir")
        for clip_dir_path in clip_dir_path_l:
            new_clip_dir_data = Clip_Dir_Data(clip_dir_path, self.pl_data_dir_path)

            # self.max_fuzz_str_len
            new_clip_dir_data.write_auto_sub_fuzz_str_to_json_if_needed()
            if new_clip_dir_data.fuzz_str_len > self.max_fuzz_str_len:
                self.max_fuzz_str_len = new_clip_dir_data.fuzz_str_len


            self.clip_dir_data_l.append(new_clip_dir_data)


if __name__ == "__main__":
    import os.path as path
    print(f"Running " , path.abspath(__file__) , '...')
    import get_init_mkvs_for_manual_edits
    get_init_mkvs_for_manual_edits.main()
    print("End of Main") 